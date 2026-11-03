import { useEffect, useRef, useState } from 'react'
import { ChevronDown, ShieldAlert } from 'lucide-react'

const FRIENDLY = {
  instruction_override: 'Tries to override the assistant’s instructions',
  prompt_leak: 'Tries to extract the system prompt',
  jailbreak: 'Jailbreak or role-play attempt',
  ml_classifier: 'Flagged by the classifier',
  llm_judge: 'Flagged by the judge model',
  obfuscated: 'Hidden inside encoded text',
  unknown_encoding: 'Contains an unreadable encoded block',
  canary_leak: 'Reply contained the internal marker',
}
const label = (c) => {
  const b = c.split('[')[0]
  if (FRIENDLY[b]) return FRIENDLY[b]
  if (b.startsWith('system_prompt_overlap')) return 'Reply repeated the system prompt'
  if (b.startsWith('secret:')) return 'Reply contained a secret'
  return b.replace(/_/g, ' ')
}

export default function AlertModal({ block, onClose }) {
  const btn = useRef(null)
  const [open, setOpen] = useState(false)

  useEffect(() => {
    btn.current?.focus()
    const onKey = (e) => { if (e.key === 'Escape') onClose() }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [onClose])

  const output = block.stage === 'output'
  const cats = [...new Set(block.categories.map(label))]

  return (
    <div className="fixed inset-0 z-50 grid place-items-center bg-black/70 p-4" onMouseDown={(e) => e.target === e.currentTarget && onClose()}>
      <div role="alertdialog" aria-modal="true" aria-labelledby="ps-t" aria-describedby="ps-d"
        className="w-full max-w-md rounded-2xl border border-red-500/50 bg-[#2a1616] p-6 shadow-2xl">
        <div className="flex items-start gap-4">
          <div className="grid size-11 shrink-0 place-items-center rounded-full bg-red-500/20 text-red-300"><ShieldAlert size={24} /></div>
          <div>
            <h2 id="ps-t" className="text-lg font-semibold text-red-100">Prompt Shield Alert</h2>
            <p id="ps-d" className="mt-1.5 text-[15px] leading-relaxed text-red-100/90">
              {output
                ? 'Prompt Shield Alert: The assistant’s reply was withheld because it could expose protected information. This request has been blocked for safety.'
                : 'Prompt Shield Alert: Potential prompt attack or malicious instruction detected. This request has been blocked for safety.'}
            </p>
          </div>
        </div>

        {(cats.length > 0 || block.score !== null) && (
          <div className="mt-4">
            <button onClick={() => setOpen(!open)} aria-expanded={open} className="flex items-center gap-1 text-sm text-red-200/80 hover:text-red-100">
              Why was this blocked? <ChevronDown size={16} className={open ? 'rotate-180' : ''} />
            </button>
            {open && (
              <ul className="mt-2 space-y-1 rounded-lg bg-black/25 p-3 text-sm text-red-100/90">
                {cats.map((c) => <li key={c}>{c}</li>)}
                {block.score !== null && <li className="text-red-200/70">Risk score {Number(block.score).toFixed(2)} (blocked at 0.70)</li>}
              </ul>
            )}
          </div>
        )}

        <p className="mt-4 text-xs text-red-200/60">Think this was a mistake? Rephrase your message and try again.</p>
        <button ref={btn} onClick={onClose} className="mt-5 w-full rounded-xl bg-white py-2.5 font-medium text-black hover:bg-zinc-200">Okay</button>
      </div>
    </div>
  )
}
