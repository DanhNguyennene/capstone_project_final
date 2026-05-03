// lib/storage.js
// All localStorage keys and helpers in one place.

export const SESSIONS_KEY = 'slurm_sessions_v2'
export const ACTIVE_KEY   = 'slurm_active_v2'
export const URL_KEY      = 'slurm_url'
export const MCP_URL_KEY  = 'slurm_mcp_url'
export const LLM_PROVIDER_KEY = 'slurm_llm_provider'
export const MAIN_PROVIDER_KEY = 'slurm_main_provider'
export const SPECIALIST_PROVIDER_KEY = 'slurm_specialist_provider'
export const JUDGE_PROVIDER_KEY = 'slurm_judge_provider'
export const OLLAMA_MODEL_KEY = 'slurm_ollama_model'
export const OPENAI_MODEL_KEY = 'slurm_openai_model'
export const AZURE_OPENAI_MODEL_KEY = 'slurm_azure_openai_model'
export const OLLAMA_SPECIALIST_MODEL_KEY = 'slurm_ollama_specialist_model'
export const OPENAI_SPECIALIST_MODEL_KEY = 'slurm_openai_specialist_model'
export const AZURE_OPENAI_SPECIALIST_MODEL_KEY = 'slurm_azure_openai_specialist_model'
export const OLLAMA_JUDGE_MODEL_KEY = 'slurm_ollama_judge_model'
export const OPENAI_JUDGE_MODEL_KEY = 'slurm_openai_judge_model'
export const AZURE_OPENAI_JUDGE_MODEL_KEY = 'slurm_azure_openai_judge_model'
export const JUDGE_MODEL_KEY = 'slurm_judge_model'
export const OPENAI_PARALLEL_KEY = 'slurm_openai_parallel'
export const EVAL_PARALLEL_WORKERS_KEY = 'slurm_eval_parallel_workers'

export function loadSessions() {
  try { return JSON.parse(localStorage.getItem(SESSIONS_KEY) || '{}') }
  catch { return {} }
}

export function mkId() {
  return 'sess_' + Date.now() + '_' + Math.random().toString(36).slice(2, 6)
}

export function mkMsg(role, content = '') {
  return {
    id: Date.now() + Math.random(),
    role,
    content,
    thinking: '',
    steps: [],
    charts: [],
    webResults: [],
    streaming: false,
    pendingActions: [],
  }
}
