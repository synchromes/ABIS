import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import api from '../services/api'

export const useAuthStore = create(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isAuthenticated: false,

      login: async (username, password) => {
        try {
          const response = await api.post('/auth/login/json', { username, password })
          const { access_token } = response.data
          
          const userResponse = await api.get('/auth/me', {
            headers: { Authorization: `Bearer ${access_token}` }
          })
          
          set({
            user: userResponse.data,
            token: access_token,
            isAuthenticated: true,
          })
          
          return { success: true }
        } catch (error) {
          return {
            success: false,
            error: error.response?.data?.detail || 'Login failed'
          }
        }
      },

      logout: () => {
        set({
          user: null,
          token: null,
          isAuthenticated: false,
        })
      },

      getToken: () => get().token,
    }),
    {
      name: 'auth-storage',
    }
  )
)
