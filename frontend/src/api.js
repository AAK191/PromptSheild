// API client layer. Every response is turned into either a result or a typed error,
// so the UI never has to inspect status codes or JSON flags itself.

const read = (k) => { try { return localStorage.getItem(k) || '' } catch { return '' } }
const write = (k, v) => { try { localStorage.setItem(k, v) } catch { /* storage blocked */ } }

export const keys = {
  api: () => read('ps_api_key'),
  admin: () => read('ps_admin_key'),
  save: (api, admin) => { write('ps_api_key', api); write('ps_admin_key', admin) },
}

export class ShieldBlockedError extends Error {   // the prompt, or the model's reply, was stopped
  constructor(data) {
    super('blocked')
    this.stage = data.stage            // 'input' | 'output'
    this.score = data.score ?? null
    this.categories = data.categories || data.findings || []
  }
}
export class AuthError extends Error {}
export class RateLimitError extends Error { constructor(m, retryAfter) { super(m); this.retryAfter = retryAfter } }
export class ValidationError extends Error {}  // 422: bad body or too long. NOT an attack.
export class NetworkError extends Error {}
export class ServerError extends Error {}

function throwHttp(res, data) {
  const detail = typeof data.detail === 'string' ? data.detail : ''
  if (res.status === 401) throw new AuthError(detail || 'The API key is missing or invalid.')
  if (res.status === 429) throw new RateLimitError('Too many requests.', Number(res.headers.get('Retry-After')) || 30)
  if (res.status === 422) throw new ValidationError('That message is too long or could not be read. Shorten it and try again.')
  if (res.status === 400) throw new ShieldBlockedError({ stage: 'input', ...data })
  if (res.status === 503) throw new ServerError(detail || 'The model is unavailable. Check that Ollama is running.')
  if (!res.ok) throw new ServerError(detail || `Request failed (${res.status}).`)
}

async function request(path, { method = 'GET', body, auth } = {}) {
  const headers = { 'Content-Type': 'application/json' }
  if (auth === 'key') headers['X-API-Key'] = keys.api()
  if (auth === 'admin') headers['X-Admin-Key'] = keys.admin()

  let res
  try {
    res = await fetch('/api' + path, { method, headers, body: body ? JSON.stringify(body) : undefined })
  } catch {
    throw new NetworkError('Cannot reach the Prompt Shield server. Check that the backend is running on port 8000.')
  }
  const data = await res.json().catch(() => ({}))
  throwHttp(res, data)

  // This backend reports blocks as HTTP 200 with a flag.
  if (data.blocked === true) throw new ShieldBlockedError(data)
  return data
}

export const sendChat = (prompt, sessionId) =>
  request('/chat', { method: 'POST', body: { prompt, session_id: sessionId }, auth: 'key' })
export const testApiKey = () => request('/scan', { method: 'POST', body: { prompt: 'connection test' }, auth: 'key' })
export const testAdminKey = () => request('/stats', { auth: 'admin' })

// Streaming chat. Calls onDelta(fullTextSoFar) as words arrive and resolves with the final,
// shield-checked text. Throws ShieldBlockedError if the prompt or the reply is stopped.
export async function streamChat(prompt, sessionId, { onDelta, signal } = {}) {
  let res
  try {
    res = await fetch('/api/chat/stream', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-API-Key': keys.api() },
      body: JSON.stringify({ prompt, session_id: sessionId }),
      signal,
    })
  } catch (e) {
    if (e.name === 'AbortError') throw e
    throw new NetworkError('Cannot reach the Prompt Shield server. Check that the backend is running on port 8000.')
  }
  if (!res.ok) throwHttp(res, await res.json().catch(() => ({})))

  const reader = res.body.getReader()
  const decoder = new TextDecoder()
  let buf = ''
  let text = ''
  for (;;) {
    const { value, done } = await reader.read()
    if (done) break
    buf += decoder.decode(value, { stream: true })
    let end
    while ((end = buf.indexOf('\n\n')) !== -1) {
      const line = buf.slice(0, end)
      buf = buf.slice(end + 2)
      if (!line.startsWith('data: ')) continue
      const ev = JSON.parse(line.slice(6))
      if (ev.type === 'delta') {
  text += ev.text;
  onDelta?.(text);
} else if (ev.type === 'done') {
  return ev.text;
} else if (ev.type === 'blocked') {
  throw new ShieldBlockedError(ev);
} else if (ev.type === 'error') {
  throw new ServerError(ev.message);
}    
}
  }

  if (!text) {
    throw new ServerError('The stream finished without returning any text. Please try again.')
  }

  return text
}