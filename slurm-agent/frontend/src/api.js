// Async generator: yields OpenAI delta objects from SSE stream
// Pass an AbortSignal to cancel mid-stream
const evalHost = typeof window !== 'undefined' ? window.location.hostname : 'localhost'
const EVAL_URL = `http://${evalHost}:8080`

export async function* streamChat(
  agentUrl,
  sessionId,
  userText,
  signal,
  mcpUrl,
  llmProvider = null,
  llmModel = null,
  llmSpecialistModel = null,
  llmJudgeModel = null,
  hitlDecision = null,
  llmMainProvider = null,
  llmSpecialistProvider = null,
  llmJudgeProvider = null,
  openaiParallel = false,
) {
  const headers = { 'Content-Type': 'application/json' }
  const mainProvider = llmMainProvider || llmProvider
  if (mcpUrl) headers['X-MCP-URL'] = mcpUrl
  if (mainProvider) {
    headers['X-LLM-Provider'] = mainProvider
    headers['X-LLM-Main-Provider'] = mainProvider
  }
  if (llmSpecialistProvider) headers['X-LLM-Specialist-Provider'] = llmSpecialistProvider
  if (llmJudgeProvider) headers['X-LLM-Judge-Provider'] = llmJudgeProvider
  if (openaiParallel && mainProvider === 'openai') headers['X-LLM-Parallel-Tool-Calls'] = 'true'
  if (llmModel) headers['X-LLM-Model'] = llmModel
  if (llmSpecialistModel) headers['X-LLM-Specialist-Model'] = llmSpecialistModel
  if (llmJudgeModel) headers['X-LLM-Judge-Model'] = llmJudgeModel
  const payload = {
    model: 'slurm-agent',
    messages: [{ role: 'user', content: userText }],
    stream: true,
    chat_id: sessionId,
  }
  if (hitlDecision) payload.hitl_decision = hitlDecision
  const resp = await fetch(`${agentUrl}/v1/chat/completions`, {
    method: 'POST',
    headers,
    body: JSON.stringify(payload),
    signal,
  })

  if (!resp.ok) {
    const body = await resp.text().catch(() => '')
    throw new Error(`HTTP ${resp.status}: ${body || resp.statusText}`)
  }

  const reader = resp.body.getReader()
  const decoder = new TextDecoder()
  let buf = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break

    buf += decoder.decode(value, { stream: true })
    const lines = buf.split('\n')
    buf = lines.pop() ?? ''

    for (const line of lines) {
      const t = line.trim()
      if (!t || t === 'data: [DONE]') continue
      if (!t.startsWith('data: ')) continue
      try {
        const data = JSON.parse(t.slice(6))
        const delta = data?.choices?.[0]?.delta
        if (delta) yield delta
      } catch { /* skip malformed chunk */ }
    }
  }
}

export async function checkHealth(agentUrl) {
  const r = await fetch(`${agentUrl}/health`, {
    signal: AbortSignal.timeout(3000),
  })
  return r.ok
}

export async function getEvalRuntimeConfig() {
  const r = await fetch(`${EVAL_URL}/api/runtime-config`, {
    signal: AbortSignal.timeout(3000),
  })
  if (!r.ok) return null
  return r.json()
}

export async function clearSessionOnServer(agentUrl, sessionId) {
  await fetch(`${agentUrl}/sessions/${sessionId}`, { method: 'DELETE' })
}

export async function uploadFile(agentUrl, file) {
  const form = new FormData()
  form.append('file', file)
  const resp = await fetch(`${agentUrl}/upload`, { method: 'POST', body: form })
  if (!resp.ok) {
    const body = await resp.text().catch(() => '')
    throw new Error(body || resp.statusText)
  }
  return resp.json()
}
