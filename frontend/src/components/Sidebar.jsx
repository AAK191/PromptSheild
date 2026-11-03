import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { MessageSquare, PanelLeftClose, Settings, SquarePen, Trash2 } from 'lucide-react'

export default function Sidebar({ t, open, setOpen, connected }) {
  const nav = useNavigate()
  const [confirm, setConfirm] = useState(false)
  const go = (fn) => () => { fn(); nav('/'); if (window.innerWidth < 768) setOpen(false) }

  return (
    <>
      {open && <div className="fixed inset-0 z-30 bg-black/60 md:hidden" onClick={() => setOpen(false)} />}
      <aside
        aria-label="Chat history" inert={!open ? '' : undefined}
        className={'fixed inset-y-0 left-0 z-40 flex w-[260px] flex-col bg-side transition-[margin,transform] duration-200 md:static ' +
          (open ? 'translate-x-0 md:ml-0' : '-translate-x-full md:-ml-[260px]')}
      >
        <div className="flex items-center justify-between p-2">
          <button onClick={go(() => t.create())} className="flex flex-1 items-center gap-2.5 rounded-lg px-3 py-2.5 text-sm hover:bg-white/10">
            <SquarePen size={18} /> New chat
          </button>
          <button onClick={() => setOpen(false)} aria-label="Close sidebar" className="rounded-lg p-2.5 text-zinc-300 hover:bg-white/10">
            <PanelLeftClose size={18} />
          </button>
        </div>

        <nav className="scroll flex-1 overflow-y-auto px-2 pb-2">
          {t.threads.length === 0 ? (
            <p className="px-3 py-6 text-sm text-zinc-500">Your chats will appear here.</p>
          ) : (
            <>
              <p className="px-3 pb-1 pt-3 text-xs font-medium text-zinc-500">Recent</p>
              <ul>
                {t.threads.map((th) => (
                  <li key={th.id} className="group relative">
                    <button
                      onClick={go(() => t.setActiveId(th.id))}
                      aria-current={t.activeId === th.id ? 'page' : undefined}
                      className={'flex w-full items-center gap-2.5 rounded-lg px-3 py-2 pr-9 text-left text-sm ' + (t.activeId === th.id ? 'bg-white/10' : 'hover:bg-white/5')}
                    >
                      <MessageSquare size={15} className="shrink-0 text-zinc-400" />
                      <span className="truncate">{th.title}</span>
                    </button>
                    <button
                      onClick={() => t.remove(th.id)} aria-label={`Delete chat ${th.title}`}
                      className="absolute right-1.5 top-1/2 -translate-y-1/2 rounded p-1.5 text-zinc-400 opacity-0 hover:bg-white/10 hover:text-white focus-visible:opacity-100 group-hover:opacity-100"
                    >
                      <Trash2 size={14} />
                    </button>
                  </li>
                ))}
              </ul>
            </>
          )}
        </nav>

        <div className="border-t border-line p-2">
          {t.threads.length > 0 && (
            <button
              onClick={() => (confirm ? (t.clearAll(), setConfirm(false)) : setConfirm(true))}
              onBlur={() => setConfirm(false)}
              className="mb-1 flex w-full items-center gap-2.5 rounded-lg px-3 py-2 text-sm text-zinc-400 hover:bg-white/10"
            >
              <Trash2 size={16} /> {confirm ? 'Click again to delete all chats' : 'Clear all chats'}
            </button>
          )}
          <button onClick={() => { nav('/settings'); if (window.innerWidth < 768) setOpen(false) }} className="flex w-full items-center gap-2.5 rounded-lg px-3 py-2.5 text-sm hover:bg-white/10">
            <Settings size={18} /> Settings
            <span className={'ml-auto size-2 rounded-full ' + (connected ? 'bg-brand' : 'bg-zinc-600')} title={connected ? 'API key saved' : 'No API key'} />
          </button>
        </div>
      </aside>
    </>
  )
}
