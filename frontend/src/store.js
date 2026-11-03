import { useCallback, useEffect, useState } from 'react'

const KEY = 'ps_threads_v1'
const uid = () => (crypto.randomUUID ? crypto.randomUUID() : String(Date.now() + Math.random()))

function load() {
  try { return JSON.parse(localStorage.getItem(KEY)) || [] } catch { return [] }
}

export function useThreads() {
  const [threads, setThreads] = useState(load)
  const [activeId, setActiveId] = useState(null)

  useEffect(() => {
    try { localStorage.setItem(KEY, JSON.stringify(threads)) } catch { /* storage full or blocked */ }
  }, [threads])

  const create = useCallback(() => {
    const t = { id: uid(), title: 'New chat', messages: [], updated: Date.now() }
    setThreads((ts) => [t, ...ts])
    setActiveId(t.id)
    return t.id
  }, [])

  const patch = useCallback((id, fn) => {
    setThreads((ts) => ts.map((t) => (t.id === id ? { ...fn(t), updated: Date.now() } : t)))
  }, [])

  const remove = useCallback((id) => {
    setThreads((ts) => ts.filter((t) => t.id !== id))
    setActiveId((a) => (a === id ? null : a))
  }, [])

  const clearAll = useCallback(() => { setThreads([]); setActiveId(null) }, [])

  return { threads, activeId, setActiveId, create, patch, remove, clearAll, uid }
}
