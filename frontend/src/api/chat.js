import request from "./request"
import { uiState } from '@/store/uiState'

export const sendToAI = (msg, convoId, userId) => request.post('/api/chat', { message: msg, convo_id: convoId, user_id: userId, active_mode: uiState.activeMode })

export async function sendToAIStream(msg, convoId, userId, callbacks) {
  const response = await fetch('http://127.0.0.1:8000/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message: msg, convo_id: convoId, user_id: userId, active_mode: uiState.activeMode }),
  })

  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break

    buffer += decoder.decode(value, { stream: true })
    const lines = buffer.split('\n')
    buffer = lines.pop()

    for (const line of lines) {
      if (line.startsWith('data: ')) {
        const event = JSON.parse(line.slice(6))
        if (event.type === 'meta') callbacks.onMeta?.(event)
        else if (event.type === 'token') callbacks.onToken?.(event.content)
        else if (event.type === 'done') callbacks.onDone?.(event)
      }
    }
  }
}

export const getConvos = (userId) => request.get(`/api/conversations?user_id=${userId}`)

export const createConvo = (userId) => request.post(`/api/conversations?user_id=${userId}`)

export const getHistoryMessages = (convoId) => request.get(`/api/conversations/${convoId}/messages`)

export const renameConvo = (id, title) => request.patch(`/api/conversations/${id}?title=${title}`)

export const deleteConvo = (id) => request.delete(`/api/conversations/${id}`)
