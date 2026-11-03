import { useEffect, useRef, useState } from 'react'
import { ArrowUp } from 'lucide-react'

export default function Composer({ onSend, busy }) {
  const [text, setText] = useState('')
  const ref = useRef(null)

  // Grow with the content, up to about 8 lines, then scroll.
  useEffect(() => {
    const el = ref.current
    if (!el) return
    el.style.height = 'auto'
    el.style.height = Math.min(el.scrollHeight, 200) + 'px'
  }, [text])

  const canSend = text.trim().length > 0 && !busy
  const submit = () => {
    if (!canSend) return
    onSend(text.trim())
    setText('')
  }
  const onKey = (e) => {
    if (e.key === 'Enter' && !e.shiftKey && !e.nativeEvent.isComposing) {
      e.preventDefault()
      submit()
    }
  }

  return (
    <div className="mx-auto w-full max-w-3xl px-4 pb-3">
      <div className="flex items-end gap-2 rounded-[28px] bg-bubble py-2.5 pl-5 pr-2.5 focus-within:ring-1 focus-within:ring-zinc-500">
        <textarea
          ref={ref} rows={1} value={text} maxLength={20000}
          onChange={(e) => setText(e.target.value)} onKeyDown={onKey}
          placeholder="Message Prompt Shield" aria-label="Message"
          className="scroll max-h-[200px] flex-1 resize-none self-center bg-transparent py-1 outline-none placeholder:text-zinc-400 focus-visible:outline-none"
        />
        <button
          onClick={submit} disabled={!canSend} aria-label="Send message"
          className="grid size-9 shrink-0 place-items-center rounded-full bg-white text-black transition-opacity disabled:cursor-not-allowed disabled:opacity-30"
        >
          <ArrowUp size={20} strokeWidth={2.5} />
        </button>
      </div>
      <p className="px-2 pt-2 text-center text-xs text-zinc-500">
        Prompt Shield checks each message before the model sees it. No filter is perfect, so double-check important answers.
      </p>
    </div>
  )
}
