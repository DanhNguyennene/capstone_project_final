import { useEffect, useRef, useState } from 'react'
import Sidebar  from './Sidebar'
import Messages from './Messages'
import InputBar from './InputBar'
import TodoList from './components/TodoList'
import EvalPage from './EvalPage'
import { checkHealth, getEvalRuntimeConfig } from './api'
import {
  URL_KEY,
  MCP_URL_KEY,
  LLM_PROVIDER_KEY,
  OLLAMA_MODEL_KEY,
  OPENAI_MODEL_KEY,
  OLLAMA_SPECIALIST_MODEL_KEY,
  OPENAI_SPECIALIST_MODEL_KEY,
  OLLAMA_JUDGE_MODEL_KEY,
  OPENAI_JUDGE_MODEL_KEY,
  JUDGE_MODEL_KEY,
} from './lib/storage'
import { useSessions } from './hooks/useSessions'
import { useStream }   from './hooks/useStream'

const OLLAMA_MODEL_OPTIONS = [
  'qwen3.5:9b',
  'qwen2.5:7b',
  'qwen3.5:27b',
  'gpt-oss:20b',
]

const OPENAI_MODEL_OPTIONS = [
  'gpt-4o-mini',
  'gpt-4.1-mini',
  'gpt-4.1',
  'o4-mini',
]

const browserHost = typeof window !== 'undefined' ? window.location.hostname : 'localhost'
const defaultAgentUrl = `http://${browserHost}:8000`
const defaultMcpUrl = `http://${browserHost}:3002`

export default function App() {
  const [agentUrl,    setAgentUrl]    = useState(() => localStorage.getItem(URL_KEY) || defaultAgentUrl)
  const [mcpUrl,      setMcpUrl]      = useState(() => localStorage.getItem(MCP_URL_KEY) || defaultMcpUrl)
  const [llmProvider, setLlmProvider] = useState(() => localStorage.getItem(LLM_PROVIDER_KEY) || 'ollama')
  const [ollamaMainModel, setOllamaMainModel] = useState(() => localStorage.getItem(OLLAMA_MODEL_KEY) || 'qwen3.5:9b')
  const [openaiMainModel, setOpenaiMainModel] = useState(() => localStorage.getItem(OPENAI_MODEL_KEY) || 'gpt-4o-mini')
  const [ollamaSpecialistModel, setOllamaSpecialistModel] = useState(
    () => localStorage.getItem(OLLAMA_SPECIALIST_MODEL_KEY) || 'qwen2.5:7b'
  )
  const [openaiSpecialistModel, setOpenaiSpecialistModel] = useState(
    () => localStorage.getItem(OPENAI_SPECIALIST_MODEL_KEY) || 'gpt-4o-mini'
  )
  const [ollamaJudgeModel, setOllamaJudgeModel] = useState(() => {
    const stored = localStorage.getItem(OLLAMA_JUDGE_MODEL_KEY)
    if (stored && OLLAMA_MODEL_OPTIONS.includes(stored)) return stored
    const legacy = localStorage.getItem(JUDGE_MODEL_KEY)
    if (legacy && OLLAMA_MODEL_OPTIONS.includes(legacy)) return legacy
    return 'qwen3.5:9b'
  })
  const [openaiJudgeModel, setOpenaiJudgeModel] = useState(() => {
    const stored = localStorage.getItem(OPENAI_JUDGE_MODEL_KEY)
    if (stored && OPENAI_MODEL_OPTIONS.includes(stored)) return stored
    const legacy = localStorage.getItem(JUDGE_MODEL_KEY)
    if (legacy && OPENAI_MODEL_OPTIONS.includes(legacy)) return legacy
    return 'gpt-4o-mini'
  })
  const [streaming,   setStreaming]   = useState(false)
  const [status,      setStatus]      = useState({ state: 'idle', text: 'Connecting…' })
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [todoList,    setTodoList]    = useState([])  // session-level plan
  const [view,        setView]        = useState('chat') // 'chat' | 'eval'
  const mainModel = llmProvider === 'openai' ? openaiMainModel : ollamaMainModel
  const specialistModel = llmProvider === 'openai' ? openaiSpecialistModel : ollamaSpecialistModel
  const judgeModel = llmProvider === 'openai' ? openaiJudgeModel : ollamaJudgeModel
  const providerModelOptions = llmProvider === 'openai' ? OPENAI_MODEL_OPTIONS : OLLAMA_MODEL_OPTIONS

  const {
    sessions, setSessions, activeId, setActiveId,
    sessionList, currentSession,
    createSession, selectSession, deleteSession, clearSession,
    patchMsg,
  } = useSessions()

  // Stable ref so async stream callbacks always see the latest activeId
  const activeIdRef  = useRef(activeId)
  activeIdRef.current = activeId

  const { sendMessage, handleAction, abortRef } = useStream({
    agentUrl,
    mcpUrl,
    llmProvider,
    llmMainModel: mainModel,
    llmSpecialistModel: specialistModel,
    llmJudgeModel: judgeModel,
    activeIdRef, setSessions, setStreaming, setStatus, patchMsg, createSession,
    onTodoUpdate: setTodoList,
  })

  const handleMainModelChange = value => {
    if (llmProvider === 'openai') setOpenaiMainModel(value)
    else setOllamaMainModel(value)
  }

  const handleSpecialistModelChange = value => {
    if (llmProvider === 'openai') setOpenaiSpecialistModel(value)
    else setOllamaSpecialistModel(value)
  }

  const handleJudgeModelChange = value => {
    if (llmProvider === 'openai') setOpenaiJudgeModel(value)
    else setOllamaJudgeModel(value)
  }

  // Clear plan when switching sessions
  useEffect(() => { setTodoList([]) }, [activeId])

  // Bootstrap: ensure at least one session exists
  useEffect(() => {
    if (!activeId || !sessions[activeId]) createSession()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  // Ping agent on URL change
  useEffect(() => {
    let cancelled = false
    localStorage.setItem(URL_KEY, agentUrl)
    localStorage.setItem(MCP_URL_KEY, mcpUrl)
    checkHealth(agentUrl)
      .then(async ok => {
        if (cancelled) return
        if (!ok) {
          setStatus({ state: 'offline', text: 'Unreachable' })
          return
        }
        setStatus({ state: 'online', text: 'Ready' })
        try {
          const config = await getEvalRuntimeConfig()
          if (cancelled || !config?.llm_provider) return
          const provider = config.llm_provider === 'openai' ? 'openai' : 'ollama'
          setLlmProvider(provider)
          if (provider === 'openai') {
            if (config.main_model) setOpenaiMainModel(config.main_model)
            if (config.specialist_model) setOpenaiSpecialistModel(config.specialist_model)
            if (config.judge_model && OPENAI_MODEL_OPTIONS.includes(config.judge_model)) {
              setOpenaiJudgeModel(config.judge_model)
            }
          } else {
            if (config.main_model) setOllamaMainModel(config.main_model)
            if (config.specialist_model) setOllamaSpecialistModel(config.specialist_model)
            if (config.judge_model && OLLAMA_MODEL_OPTIONS.includes(config.judge_model)) {
              setOllamaJudgeModel(config.judge_model)
            }
          }
        } catch {
          // Older eval servers do not expose runtime config; keep local selections.
        }
      })
      .catch(() => setStatus({ state: 'offline', text: 'Disconnected' }))
    return () => { cancelled = true }
  }, [agentUrl, mcpUrl])

  useEffect(() => {
    localStorage.setItem(LLM_PROVIDER_KEY, llmProvider)
    localStorage.setItem(OLLAMA_MODEL_KEY, ollamaMainModel)
    localStorage.setItem(OPENAI_MODEL_KEY, openaiMainModel)
    localStorage.setItem(OLLAMA_SPECIALIST_MODEL_KEY, ollamaSpecialistModel)
    localStorage.setItem(OPENAI_SPECIALIST_MODEL_KEY, openaiSpecialistModel)
    localStorage.setItem(OLLAMA_JUDGE_MODEL_KEY, ollamaJudgeModel)
    localStorage.setItem(OPENAI_JUDGE_MODEL_KEY, openaiJudgeModel)
    localStorage.setItem(JUDGE_MODEL_KEY, judgeModel)
  }, [
    llmProvider,
    ollamaMainModel,
    openaiMainModel,
    ollamaSpecialistModel,
    openaiSpecialistModel,
    ollamaJudgeModel,
    openaiJudgeModel,
    judgeModel,
  ])

  return (
    <div className="app">
      <Sidebar
        open={sidebarOpen}
        sessions={sessionList}
        activeId={activeId}
        onNew={createSession}
        onSelect={selectSession}
        onDelete={deleteSession}
        agentUrl={agentUrl}
        onAgentUrlChange={setAgentUrl}
        mcpUrl={mcpUrl}
        onMcpUrlChange={setMcpUrl}
        llmProvider={llmProvider}
        onLlmProviderChange={setLlmProvider}
        mainModel={mainModel}
        specialistModel={specialistModel}
        judgeModel={judgeModel}
        llmModelOptions={providerModelOptions}
        judgeModelOptions={providerModelOptions}
        onMainModelChange={handleMainModelChange}
        onSpecialistModelChange={handleSpecialistModelChange}
        onJudgeModelChange={handleJudgeModelChange}
        view={view}
        onViewChange={setView}
      />

      {view === 'eval' ? (
        <EvalPage
          agentUrl={agentUrl}
          mcpUrl={mcpUrl}
          llmProvider={llmProvider}
          mainModel={mainModel}
          specialistModel={specialistModel}
          judgeModel={judgeModel}
          sidebarOpen={sidebarOpen}
          onToggleGlobalSidebar={() => setSidebarOpen(o => !o)}
        />
      ) : (
      <div className="main">
        <header className="topbar">
          <button className="icon-btn" onClick={() => setSidebarOpen(o => !o)} title="Toggle sidebar">☰</button>
          <span className="topbar-title">{currentSession?.title || 'New Chat'}</span>
          <div className="status-group">
            <span className={`dot dot-${status.state}`} />
            <span className="status-label">{status.text}</span>
          </div>
          <button className="ghost-btn" onClick={() => clearSession(agentUrl, activeId)}>Clear</button>
        </header>

        <Messages
          messages={currentSession?.messages || []}
          onSuggestion={sendMessage}
          onAction={handleAction}
          todoList={todoList}
        />

        <InputBar onSend={sendMessage} disabled={streaming} onStop={() => abortRef.current?.abort()} agentUrl={agentUrl} />
      </div>
      )}
    </div>
  )
}
