import { ShieldAlert, ShieldCheck } from 'lucide-react'
import Markdown from './Markdown.jsx'

export function Thinking() {
  return (
    <div className="flex gap-4">
      <Avatar />
      <div className="flex items-center gap-1.5 pt-2" role="status" aria-label="The assistant is replying">
        <span className="dot size-2 rounded-full bg-zinc-400" /><span className="dot size-2 rounded-full bg-zinc-400" /><span className="dot size-2 rounded-full bg-zinc-400" />
      </div>
    </div>
  )
}

const Avatar = () => (
  <div className="mt-0.5 grid size-8 shrink-0 place-items-center rounded-full border border-line bg-chat text-brand">
    <ShieldCheck size={18} />
  </div>
)

export default function Message({ m }) {
  if (m.role === 'user') {
    return (
      <div className="flex flex-col items-end gap-1.5">
        <div className={'max-w-[85%] whitespace-pre-wrap break-words rounded-3xl px-5 py-2.5 ' + (m.blocked ? 'border border-red-500/60 bg-red-950/40' : 'bg-bubble')}>
          {m.content}
        </div>
        {m.blocked && (
          <span className="flex items-center gap-1.5 pr-2 text-xs text-red-300">
            <ShieldAlert size={13} /> Blocked by Prompt Shield. This message was not answered.
          </span>
        )}
      </div>
    )
  }
  return (
    <div className="flex gap-4">
      <Avatar />
      <div className="min-w-0 flex-1 pt-0.5">
        {m.error ? <p className="text-red-300">{m.content}</p> : <Markdown>{m.content}</Markdown>}
      </div>
    </div>
  )
}
