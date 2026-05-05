import request from "@/api/request"
import { service } from "@/api/request"

export const fetchUsers = (params) => service.get("/api/admin/users", { params })

export const deleteUser = (id) => service.delete(`/api/admin/users/${id}`)

export const resetUserPassword = (id, newPassword) =>
  service.post(`/api/admin/users/${id}/reset-password`, { new_password: newPassword })

export const uploadDocs = (formData) => {
  return service({
    url: '/api/admin/upload_docs',
    method: 'post',
    data: formData,
    timeout: 60000 
  })
}

export const getDocs = () => request.get('/api/admin/docs')

export const deleteDoc = (id) => service.delete(`/api/admin/docs/${id}`)

export const previewDoc = (id) => service.get(`/api/admin/docs/${id}/preview`)

export const getDocsStatus = () => service.get('/api/admin/status')

export const rebuildIndex = (id, params) => {
  const formData = new FormData()
  formData.append('chunk_size', params.chunk_size)
  formData.append('chunk_overlap', params.chunk_overlap)
  formData.append('strategy', params.strategy)
  return request.post(`/api/admin/docs/${id}/rebuild`, formData)
}

export const fetchAdminResources = (params) => request.get('/api/admin/resources', { params })

export const updateResource = (id, data) => service.patch(`/api/admin/resources/${id}`, data)

export const deleteResource = (id) => {
  return service.delete(`/api/admin/resources/${id}`)
}

export const batchImportResources = (resources) => {
  return service.post('/api/admin/resources/batch-import', resources)
}

export const fetchAmapSearch = (params) => request.get('/api/admin/resources/amap-search', { params })
