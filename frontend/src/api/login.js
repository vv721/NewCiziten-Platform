import request from "@/api/request"

export function roleLogin(username, password) {
  return request.post('/login', {
    username,
    password,
  })
}

export const registerApi = (data) => request.post('/api/register', data);
