import { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { AlertTriangle, ShieldCheck, X } from 'lucide-react'
import { AuthError, NetworkError, RateLimitError, ShieldBlockedError, ValidationError, sendChat } from '../api'
import Composer from './Composer.jsx'
import Message, { Thinking } from './Message.jsx'
import AlertModal from './AlertModal.jsx'

const SUGGESTIONS = [
  'Explain how a hash map works',
  'Write a Python function that reverses a string',
  'Summarize the causes of World War 1',
  'How does prompt injection work?',
]

export default function Chat({ t }) {
  const nav = useNavigate()
  const thread = t.threads.find((x) => x.id === t.activeId)
  const [busy, setBusy] = useState(false)
  const [block, setBlock] = useState(null)   // attack alert (modal)
  const [notice, setNotice] = useState(null) // non-attack problems (banner)
  const endRef = useRef(null)

  useEffect(() => { endRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' }) }, [thread?.messages.length, busy])
  useEffect(() => { setNotice(null) }, [t.activeId])

  const send = async (text) => {
    let id = t.activeId
    if (!id) id = t.create()
    const userMsg = { id: t.uid(), role: 'user', content: text }

    t.patch(id, (th) => ({
      ...th,
      title: th.messages.length === 0 ? text.slice(0, 40) : th.title,
      messages: [...th.messages, userMsg],
    }))
    setBusy(true); setNotice(null)

    try {
      // One session per thread, so attacks split across messages are still caught.
      const r = await sendChat(text, `web-${id}`)
      t.patch(id, (th) => ({ ...th, messages: [...th.messages, { id: t.uid(), role: 'assistant', content: r.response }] }))
    } catch (e) {
      if (e instanceof ShieldBlockedError) {
        // Never show an AI answer for a blocked request: mark the message and raise the alert.
        t.patch(id, (th) => ({ ...th, messages: th.messages.map((m) => (m.id === userMsg.id ? { ...m, blocked: true } : m)) }))
        setBlock(e)
      } else if (e instanceof AuthError) {
        setNotice({ kind: 'auth', text: e.message })
      } else if (e instanceof RateLimitError) {
        setNotice({ kind: 'rate', text: `You are sending messages too quickly. Wait ${e.retryAfter} seconds and try again.` })
      } else if (e instanceof ValidationError || e instanceof NetworkError) {
        setNotice({ kind: 'err', text: e.message })
      } else {
        setNotice({ kind: 'err', text: e.message || 'Something went wrong.' })
      }
    } finally { setBusy(false) }
  }

  const empty = !thread || thread.messages.length === 0

  return (
    <div className="flex min-h-0 flex-1 flex-col">
      {notice && (
        <div role="alert" className="mx-auto mt-3 flex w-full max-w-3xl items-start gap-3 rounded-xl border border-amber-500/40 bg-amber-950/40 px-4 py-3 text-sm text-amber-100">
          <AlertTriangle size={18} className="mt-0.5 shrink-0" />
          <div className="flex-1">
            {notice.text}
            {notice.kind === 'auth' && <> Check your keys in <button onClick={() => nav('/settings')} className="font-semibold underline">Settings</button>.</>}
          </div>
          <button onClick={() => setNotice(null)} aria-label="Dismiss" className="rounded p-0.5 hover:bg-white/10"><X size={16} /></button>
        </div>
      )}

      <div className="scroll flex-1 overflow-y-auto">
        {empty ? (
          <div className="mx-auto flex h-full max-w-3xl flex-col items-center justify-center px-4 pb-10 text-center">
            <div className="mb-5 grid size-14 place-items-center rounded-full bg-brand/15 text-brand"><ShieldCheck size={30} /></div>
            <h1 className="text-3xl font-semibold tracking-tight">How can I help today?</h1>
            <p className="mt-2 text-zinc-400">Every message is checked for prompt attacks before it reaches the model.</p>
            <div className="mt-8 grid w-full max-w-xl gap-2 sm:grid-cols-2">
              {SUGGESTIONS.map((s) => (
                <button key={s} onClick={() => send(s)} disabled={busy} className="rounded-2xl border border-line px-4 py-3 text-left text-sm text-zinc-300 hover:bg-white/5 disabled:opacity-50">{s}</button>
              ))}
            </div>
          </div>
        ) : (
          <div className="mx-auto w-full max-w-3xl space-y-8 px-4 py-8">
            {thread.messages.map((m) => <Message key={m.id} m={m} />)}
            {busy && <Thinking />}
            <div ref={endRef} />
          </div>
        )}
      </div>

      <Composer onSend={send} busy={busy} />
      {block && <AlertModal block={block} onClose={() => setBlock(null)} />}
    </div>
  )
}
