import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { vscDarkPlus, vs } from 'react-syntax-highlighter/dist/cjs/styles/prism'
import { useTheme } from 'nextra-theme-docs'

interface ConfigFileProps {
  content: string
  language?: string
  filename?: string
  showLineNumbers?: boolean
}

export default function ConfigFile({
  content,
  language = 'yaml',
  filename,
  showLineNumbers = true
}: ConfigFileProps) {
  const { resolvedTheme } = useTheme()
  const isDark = resolvedTheme === 'dark'

  return (
    <div className="config-file" style={{ margin: '2rem 0' }}>
      {filename && (
        <div
          style={{
            background: isDark ? '#1e1e1e' : '#f5f5f5',
            padding: '0.5rem 1rem',
            borderTopLeftRadius: '8px',
            borderTopRightRadius: '8px',
            fontFamily: 'monospace',
            fontSize: '0.9rem',
            color: isDark ? '#d4d4d4' : '#333',
            borderBottom: `1px solid ${isDark ? '#333' : '#ddd'}`
          }}
        >
          📄 {filename}
        </div>
      )}
      <SyntaxHighlighter
        language={language}
        style={isDark ? vscDarkPlus : vs}
        showLineNumbers={showLineNumbers}
        customStyle={{
          margin: 0,
          borderRadius: filename ? '0 0 8px 8px' : '8px',
          fontSize: '0.9rem'
        }}
      >
        {content}
      </SyntaxHighlighter>
    </div>
  )
}
