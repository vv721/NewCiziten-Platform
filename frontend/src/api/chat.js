import request, { BASE_URL } from "./request"
import { uiState } from '@/store/uiState'

function getUserPosition() {
  return new Promise((resolve) => {
    if (!navigator.geolocation) {
      resolve({ lat: null, lng: null })
      return
    }
    navigator.geolocation.getCurrentPosition(
      (pos) => resolve({ lat: pos.coords.latitude, lng: pos.coords.longitude }),
      () => resolve({ lat: null, lng: null }),
      { timeout: 5000 },
    )
  })
}

export const sendToAI = (msg, convoId, userId) => request.post('/api/chat', { message: msg, convo_id: convoId, user_id: userId, active_mode: uiState.activeMode })

export async function sendToAIStream(msg, convoId, userId, callbacks) {
  const pos = await getUserPosition()
  const body = { message: msg, convo_id: convoId, user_id: userId, active_mode: uiState.activeMode }
  if (pos.lat != null) {
    body.lat = pos.lat
    body.lng = pos.lng
  }

  const response = await fetch(`${BASE_URL}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
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
