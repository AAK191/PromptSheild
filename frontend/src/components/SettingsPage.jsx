import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ArrowLeft, CheckCircle2, Eye, EyeOff, XCircle } from 'lucide-react'
import { keys, testAdminKey, testApiKey } from '../api'

function KeyField({ id, label, hint, value, onChange }) {
  const [show, setShow] = useState(false)
  return (
    <div className="mb-6">
      <label htmlFor={id} className="mb-1.5 block text-sm font-medium">{label}</label>
      <div className="flex items-center rounded-xl border border-line bg-bubble focus-within:ring-1 focus-within:ring-zinc-500">
        <input id={id} type={show ? 'text' : 'password'} value={value} onChange={(e) => onChange(e.target.value)}
          autoComplete="off" spellCheck="false" className="min-w-0 flex-1 bg-transparent px-4 py-2.5 font-mono text-sm outline-none focus-visible:outline-none" />
        <button type="button" onClick={() => setShow(!show)} aria-label={show ? `Hide ${label}` : `Show ${label}`} className="p-3 text-zinc-400 hover:text-white">
          {show ? <EyeOff size={18} /> : <Eye size={18} />}
        </button>
      </div>
      <p className="mt-1.5 text-xs text-zinc-500">{hint}</p>
    </div>
  )
}

export default function SettingsPage({ onSaved }) {
  const nav = useNavigate()
  const [api, setApi] = useState(keys.api())
  const [admin, setAdmin] = useState(keys.admin())
  const [results, setResults] = useState(null)
  const [busy, setBusy] = useState(false)

  const save = () => { keys.save(api.trim(), admin.trim()); onSaved() }

  const test = async () => {
    save(); setBusy(true); setResults(null)
    const out = []
    try { await testApiKey(); out.push({ ok: true, text: 'API key works.' }) }
    catch (e) { out.push({ ok: e.message === 'blocked', text: `API key: ${e.message}` }) }
    if (admin.trim()) {
      try { await testAdminKey(); out.push({ ok: true, text: 'Admin key works.' }) }
      catch (e) { out.push({ ok: false, text: `Admin key: ${e.message}` }) }
    } else out.push({ ok: true, text: 'No admin key set. It is only needed for the logs and stats endpoints.' })
    setResults(out); setBusy(false)
  }

  return (
    <div className="scroll flex-1 overflow-y-auto">
      <div className="mx-auto max-w-xl px-5 py-10">
        <button onClick={() => nav('/')} className="mb-6 flex items-center gap-2 text-sm text-zinc-400 hover:text-white"><ArrowLeft size={16} /> Back to chat</button>
        <h1 className="text-2xl font-semibold">Settings</h1>
        <p className="mb-8 mt-2 text-sm text-zinc-400">Keys are saved in this browser only and are sent to your own Prompt Shield server.</p>

        <KeyField id="api" label="API key" value={api} onChange={setApi} hint="Starts with ps_. Create one with POST /admin/keys. It is shown only once." />
        <KeyField id="adm" label="Admin key" value={admin} onChange={setAdmin} hint="The ADMIN_KEY you set before starting the server. Optional for chatting." />

        <div className="flex gap-3">
          <button onClick={save} className="rounded-xl border border-line px-5 py-2.5 text-sm font-medium hover:bg-white/5">Save</button>
          <button onClick={test} disabled={busy || !api.trim()} className="rounded-xl bg-white px-5 py-2.5 text-sm font-medium text-black hover:bg-zinc-200 disabled:opacity-40">
            {busy ? 'Testing…' : 'Save and test'}
          </button>
        </div>

        {results && (
          <ul className="mt-6 space-y-2" role="status">
            {results.map((r) => (
              <li key={r.text} className={'flex items-start gap-2 text-sm ' + (r.ok ? 'text-emerald-300' : 'text-red-300')}>
                {r.ok ? <CheckCircle2 size={17} className="mt-0.5 shrink-0" /> : <XCircle size={17} className="mt-0.5 shrink-0" />}{r.text}
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  )
}
