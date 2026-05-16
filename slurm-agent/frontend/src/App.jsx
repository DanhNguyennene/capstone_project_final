import { useCallback, useEffect, useRef, useState } from 'react'
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
  MAIN_PROVIDER_KEY,
  SPECIALIST_PROVIDER_KEY,
  JUDGE_PROVIDER_KEY,
  OLLAMA_MODEL_KEY,
  OPENAI_MODEL_KEY,
  AZURE_OPENAI_MODEL_KEY,
  OLLAMA_SPECIALIST_MODEL_KEY,
  OPENAI_SPECIALIST_MODEL_KEY,
  AZURE_OPENAI_SPECIALIST_MODEL_KEY,
  OLLAMA_JUDGE_MODEL_KEY,
  OPENAI_JUDGE_MODEL_KEY,
  AZURE_OPENAI_JUDGE_MODEL_KEY,
  JUDGE_MODEL_KEY,
  OPENAI_PARALLEL_KEY,
  EVAL_PARALLEL_WORKERS_KEY,
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
  'slurm-todo-specialist-qwen05b-lora-quick',
  'gpt-5',
  'gpt-5-mini',
  'gpt-5-nano',
  'gpt-5-chat-latest',
  'gpt-4o',
  'gpt-4o-mini',
  'gpt-4.5-preview',
  'gpt-4.1',
  'gpt-4.1-mini',
  'gpt-4.1-nano',
  'o3',
  'o3-mini',
  'o3-pro',
  'o4-mini',
  'o1',
  'o1-mini',
]

const AZURE_OPENAI_MODEL_OPTIONS = [
  'gpt-4o',
  'gpt-4o-mini',
  'gpt-4.1-mini',
  'gpt-4.1',
]

const browserHost = typeof window !== 'undefined' ? window.location.hostname : 'localhost'
const defaultAgentUrl = `http://${browserHost}:8000`
const defaultMcpUrl = `http://${browserHost}:3002`

const normalizeProvider = value => {
  const normalized = String(value || '').trim().toLowerCase()
  if (normalized === 'openai') return 'openai'
  if (normalized === 'azure' || normalized === 'azure_openai' || normalized === 'azure-openai') return 'azure-openai'
  if (normalized === 'finetuned' || normalized === 'ft' || normalized === 'lora') return 'finetuned'
  return 'ollama'
}
const clampParallelWorkers = value => Math.max(1, Math.min(8, Number(value) || 1))
const FT_MODEL_OPTIONS = ['slurm-agent']

const modelOptionsForProvider = provider => {
  const p = normalizeProvider(provider)
  if (p === 'openai') return OPENAI_MODEL_OPTIONS
  if (p === 'azure-openai') return AZURE_OPENAI_MODEL_OPTIONS
  if (p === 'finetuned') return FT_MODEL_OPTIONS
  return OLLAMA_MODEL_OPTIONS
}

export default function App() {
  const [agentUrl,    setAgentUrl]    = useState(() => localStorage.getItem(URL_KEY) || defaultAgentUrl)
  const [mcpUrl,      setMcpUrl]      = useState(() => localStorage.getItem(MCP_URL_KEY) || defaultMcpUrl)
  const [mainProvider, setMainProvider] = useState(() => normalizeProvider(
    localStorage.getItem(MAIN_PROVIDER_KEY) || localStorage.getItem(LLM_PROVIDER_KEY) || 'ollama'
  ))
  const [specialistProvider, setSpecialistProvider] = useState(() => normalizeProvider(
    localStorage.getItem(SPECIALIST_PROVIDER_KEY)
    || localStorage.getItem(MAIN_PROVIDER_KEY)
    || localStorage.getItem(LLM_PROVIDER_KEY)
    || 'ollama'
  ))
  const [judgeProvider, setJudgeProvider] = useState(() => normalizeProvider(
    localStorage.getItem(JUDGE_PROVIDER_KEY)
    || localStorage.getItem(MAIN_PROVIDER_KEY)
    || localStorage.getItem(LLM_PROVIDER_KEY)
    || 'ollama'
  ))
  const [openaiParallel, setOpenaiParallel] = useState(() => localStorage.getItem(OPENAI_PARALLEL_KEY) === 'true')
  const [parallelWorkers, setParallelWorkers] = useState(() => clampParallelWorkers(localStorage.getItem(EVAL_PARALLEL_WORKERS_KEY)))
  const [ollamaMainModel, setOllamaMainModel] = useState(() => localStorage.getItem(OLLAMA_MODEL_KEY) || 'qwen3.5:9b')
  const [openaiMainModel, setOpenaiMainModel] = useState(() => localStorage.getItem(OPENAI_MODEL_KEY) || 'gpt-4o-mini')
  const [azureOpenaiMainModel, setAzureOpenaiMainModel] = useState(
    () => localStorage.getItem(AZURE_OPENAI_MODEL_KEY) || 'gpt-4o'
  )
  const [ollamaSpecialistModel, setOllamaSpecialistModel] = useState(
    () => localStorage.getItem(OLLAMA_SPECIALIST_MODEL_KEY) || 'qwen2.5:7b'
  )
  const [openaiSpecialistModel, setOpenaiSpecialistModel] = useState(
    () => localStorage.getItem(OPENAI_SPECIALIST_MODEL_KEY) || 'gpt-4o-mini'
  )
  const [azureOpenaiSpecialistModel, setAzureOpenaiSpecialistModel] = useState(
    () => localStorage.getItem(AZURE_OPENAI_SPECIALIST_MODEL_KEY) || 'gpt-4o'
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
  const [azureOpenaiJudgeModel, setAzureOpenaiJudgeModel] = useState(() => {
    const stored = localStorage.getItem(AZURE_OPENAI_JUDGE_MODEL_KEY)
    if (stored && AZURE_OPENAI_MODEL_OPTIONS.includes(stored)) return stored
    const legacy = localStorage.getItem(JUDGE_MODEL_KEY)
    if (legacy && AZURE_OPENAI_MODEL_OPTIONS.includes(legacy)) return legacy
    return 'gpt-4o'
  })
  const [streaming,   setStreaming]   = useState(false)
  const [status,      setStatus]      = useState({ state: 'idle', text: 'Connecting…' })
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [todoList,    setTodoList]    = useState([])  // session-level plan
  const [view,        setView]        = useState('chat') // 'chat' | 'eval'
  const modelFor = (provider, ollamaModel, openaiModel, azureModel) => {
    if (provider === 'openai') return openaiModel
    if (provider === 'azure-openai') return azureModel
    if (provider === 'finetuned') return 'slurm-agent'
    return ollamaModel
  }
  const mainModel = modelFor(mainProvider, ollamaMainModel, openaiMainModel, azureOpenaiMainModel)
  const specialistModel = modelFor(specialistProvider, ollamaSpecialistModel, openaiSpecialistModel, azureOpenaiSpecialistModel)
  const judgeModel = modelFor(judgeProvider, ollamaJudgeModel, openaiJudgeModel, azureOpenaiJudgeModel)
  const mainModelOptions = modelOptionsForProvider(mainProvider)
  const specialistModelOptions = modelOptionsForProvider(specialistProvider)
  const judgeModelOptions = modelOptionsForProvider(judgeProvider)

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
    llmProvider: mainProvider,
    llmMainProvider: mainProvider,
    llmSpecialistProvider: specialistProvider,
    llmJudgeProvider: judgeProvider,
    llmMainModel: mainModel,
    llmSpecialistModel: specialistModel,
    llmJudgeModel: judgeModel,
    openaiParallel,
    activeIdRef, setSessions, setStreaming, setStatus, patchMsg, createSession,
    onTodoUpdate: setTodoList,
  })

  const handleMainModelChange = value => {
    if (mainProvider === 'openai') setOpenaiMainModel(value)
    else if (mainProvider === 'azure-openai') setAzureOpenaiMainModel(value)
    else setOllamaMainModel(value)
  }

  const handleSpecialistModelChange = value => {
    if (specialistProvider === 'openai') setOpenaiSpecialistModel(value)
    else if (specialistProvider === 'azure-openai') setAzureOpenaiSpecialistModel(value)
    else setOllamaSpecialistModel(value)
  }

  const handleJudgeModelChange = value => {
    if (judgeProvider === 'openai') setOpenaiJudgeModel(value)
    else if (judgeProvider === 'azure-openai') setAzureOpenaiJudgeModel(value)
    else setOllamaJudgeModel(value)
  }

  const handleParallelWorkersChange = useCallback(value => {
    setParallelWorkers(clampParallelWorkers(value))
  }, [])

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
          const syncedMainProvider = normalizeProvider(config.main_provider || config.llm_provider)
          const syncedSpecialistProvider = normalizeProvider(config.specialist_provider || syncedMainProvider)
          const syncedJudgeProvider = normalizeProvider(config.judge_provider || syncedMainProvider)
          setMainProvider(syncedMainProvider)
          setSpecialistProvider(syncedSpecialistProvider)
          setJudgeProvider(syncedJudgeProvider)
          setOpenaiParallel(Boolean(config.openai_parallel))
          if (localStorage.getItem(EVAL_PARALLEL_WORKERS_KEY) == null) {
            setParallelWorkers(clampParallelWorkers(config.parallel_workers || 1))
          }
          if (config.main_model) {
            if (syncedMainProvider === 'openai') setOpenaiMainModel(config.main_model)
            else if (syncedMainProvider === 'azure-openai') setAzureOpenaiMainModel(config.main_model)
            else setOllamaMainModel(config.main_model)
          }
          if (config.specialist_model) {
            if (syncedSpecialistProvider === 'openai') setOpenaiSpecialistModel(config.specialist_model)
            else if (syncedSpecialistProvider === 'azure-openai') setAzureOpenaiSpecialistModel(config.specialist_model)
            else setOllamaSpecialistModel(config.specialist_model)
          }
          if (config.judge_model) {
            if (syncedJudgeProvider === 'openai') setOpenaiJudgeModel(config.judge_model)
            else if (syncedJudgeProvider === 'azure-openai') setAzureOpenaiJudgeModel(config.judge_model)
            else setOllamaJudgeModel(config.judge_model)
          }
        } catch {
          // Older eval servers do not expose runtime config; keep local selections.
        }
      })
      .catch(() => setStatus({ state: 'offline', text: 'Disconnected' }))
    return () => { cancelled = true }
  }, [agentUrl, mcpUrl])

  useEffect(() => {
    localStorage.setItem(LLM_PROVIDER_KEY, mainProvider)
    localStorage.setItem(MAIN_PROVIDER_KEY, mainProvider)
    localStorage.setItem(SPECIALIST_PROVIDER_KEY, specialistProvider)
    localStorage.setItem(JUDGE_PROVIDER_KEY, judgeProvider)
    localStorage.setItem(OPENAI_PARALLEL_KEY, openaiParallel ? 'true' : 'false')
    localStorage.setItem(EVAL_PARALLEL_WORKERS_KEY, String(parallelWorkers))
    localStorage.setItem(OLLAMA_MODEL_KEY, ollamaMainModel)
    localStorage.setItem(OPENAI_MODEL_KEY, openaiMainModel)
    localStorage.setItem(AZURE_OPENAI_MODEL_KEY, azureOpenaiMainModel)
    localStorage.setItem(OLLAMA_SPECIALIST_MODEL_KEY, ollamaSpecialistModel)
    localStorage.setItem(OPENAI_SPECIALIST_MODEL_KEY, openaiSpecialistModel)
    localStorage.setItem(AZURE_OPENAI_SPECIALIST_MODEL_KEY, azureOpenaiSpecialistModel)
    localStorage.setItem(OLLAMA_JUDGE_MODEL_KEY, ollamaJudgeModel)
    localStorage.setItem(OPENAI_JUDGE_MODEL_KEY, openaiJudgeModel)
    localStorage.setItem(AZURE_OPENAI_JUDGE_MODEL_KEY, azureOpenaiJudgeModel)
    localStorage.setItem(JUDGE_MODEL_KEY, judgeModel)
  }, [
    mainProvider,
    specialistProvider,
    judgeProvider,
    openaiParallel,
    parallelWorkers,
    ollamaMainModel,
    openaiMainModel,
    azureOpenaiMainModel,
    ollamaSpecialistModel,
    openaiSpecialistModel,
    azureOpenaiSpecialistModel,
    ollamaJudgeModel,
    openaiJudgeModel,
    azureOpenaiJudgeModel,
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
        mainProvider={mainProvider}
        specialistProvider={specialistProvider}
        judgeProvider={judgeProvider}
        onMainProviderChange={setMainProvider}
        onSpecialistProviderChange={setSpecialistProvider}
        onJudgeProviderChange={setJudgeProvider}
        mainModel={mainModel}
        specialistModel={specialistModel}
        judgeModel={judgeModel}
        mainModelOptions={mainModelOptions}
        specialistModelOptions={specialistModelOptions}
        judgeModelOptions={judgeModelOptions}
        onMainModelChange={handleMainModelChange}
        onSpecialistModelChange={handleSpecialistModelChange}
        onJudgeModelChange={handleJudgeModelChange}
        openaiParallel={openaiParallel}
        onOpenaiParallelChange={setOpenaiParallel}
        parallelWorkers={parallelWorkers}
        onParallelWorkersChange={handleParallelWorkersChange}
        view={view}
        onViewChange={setView}
      />

      {view === 'eval' ? (
        <EvalPage
          agentUrl={agentUrl}
          mcpUrl={mcpUrl}
          llmProvider={mainProvider}
          mainProvider={mainProvider}
          specialistProvider={specialistProvider}
          judgeProvider={judgeProvider}
          mainModel={mainModel}
          specialistModel={specialistModel}
          judgeModel={judgeModel}
          openaiParallel={openaiParallel}
          parallelWorkers={parallelWorkers}
          onParallelWorkersChange={handleParallelWorkersChange}
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
