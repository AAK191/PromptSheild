import { useState } from 'react'
import { Route, Routes } from 'react-router-dom'
import { PanelLeftOpen, SquarePen } from 'lucide-react'
import { keys } from './api'
import { useThreads } from './store'
import Sidebar from './components/Sidebar.jsx'
import Chat from './components/Chat.jsx'
import SettingsPage from './components/SettingsPage.jsx'

export default function App() {
  const t = useThreads()
  const [open, setOpen] = useState(() => window.innerWidth >= 768)
  const [connected, setConnected] = useState(!!keys.api())

  return (
    <div className="flex h-full">
      <Sidebar t={t} open={open} setOpen={setOpen} connected={connected} />
      <div className="flex min-w-0 flex-1 flex-col">
        <header className="flex h-12 items-center gap-1 px-2">
          {!open && (
            <>
              <button onClick={() => setOpen(true)} aria-label="Open sidebar" className="rounded-lg p-2.5 text-zinc-300 hover:bg-white/10"><PanelLeftOpen size={20} /></button>
              <button onClick={() => t.create()} aria-label="New chat" className="rounded-lg p-2.5 text-zinc-300 hover:bg-white/10"><SquarePen size={20} /></button>
            </>
          )}
          <span className="px-2 text-lg font-medium text-zinc-200">Prompt Shield</span>
        </header>
        <Routes>
          <Route path="/" element={<Chat t={t} />} />
          <Route path="/settings" element={<SettingsPage onSaved={() => setConnected(!!keys.api())} />} />
          <Route path="*" element={<Chat t={t} />} />
        </Routes>
      </div>
    </div>
  )
}
