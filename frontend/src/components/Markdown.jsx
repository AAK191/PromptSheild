import { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { Check, Copy } from 'lucide-react'

function CodeBlock({ lang, text }) {
  const [done, setDone] = useState(false)
  const copy = async () => {
    try {
      await navigator.clipboard.writeText(text)
      setDone(true)
      setTimeout(() => setDone(false), 1800)
    } catch { /* clipboard blocked */ }
  }
  return (
    <div className="my-4 overflow-hidden rounded-xl border border-line bg-[#0d0d0d]">
      <div className="flex items-center justify-between bg-[#2a2a2a] px-4 py-2 text-xs text-zinc-300">
        <span>{lang || 'code'}</span>
        <button onClick={copy} className="flex items-center gap-1.5 rounded px-1.5 py-0.5 hover:bg-white/10" aria-label="Copy code">
          {done ? <Check size={14} /> : <Copy size={14} />}{done ? 'Copied' : 'Copy'}
        </button>
      </div>
      <pre className="scroll overflow-x-auto p-4 text-[13px] leading-6"><code className="font-mono">{text}</code></pre>
    </div>
  )
}

// react-markdown ignores raw HTML by default, so model output cannot inject markup.
export default function Markdown({ children }) {
  return (
    <div className="md">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          pre({ children: c }) {
            const child = Array.isArray(c) ? c[0] : c
            const cls = child?.props?.className || ''
            const lang = /language-([\w-]+)/.exec(cls)?.[1]
            const text = String(child?.props?.children ?? '').replace(/\n$/, '')
            return <CodeBlock lang={lang} text={text} />
          },
          a: ({ children: c, ...p }) => <a {...p} target="_blank" rel="noopener noreferrer">{c}</a>,
        }}
      >
        {children}
      </ReactMarkdown>
    </div>
  )
}
