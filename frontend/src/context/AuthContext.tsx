import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from 'react'
import { clearAuthToken, getAuthToken } from '../lib/authStorage'
import {
  editUser,
  getCurrentUser,
  signIn,
  signOut,
  signUp,
  type user,
  type AuthCredentials,
  type SignUpInput,
} from '../services/authService'

type AuthContextValue = {
  user: user | null
  isLoading: boolean
  signIn: (credentials: AuthCredentials) => Promise<user | null>
  signUp: (input: SignUpInput) => Promise<user | null>
  signOut: () => Promise<void>
  refreshUser: () => Promise<user | null>
  updateUser: (updates: Partial<user>) => Promise<user | null>
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined)

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<user | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const hydrateUser = async () => {
      const token = getAuthToken()

      if (!token) {
        setIsLoading(false)
        return
      }

      try {
        const currentUser = await getCurrentUser()
        setUser(currentUser)
      } finally {
        setIsLoading(false)
      }
    }

    void hydrateUser()
  }, [])

  const value = useMemo<AuthContextValue>(() => ({
    user,
    isLoading,
    signIn: async (credentials) => {
      const response = await signIn(credentials)
      setUser(response)
      return response
    },
    signUp: async (input) => {
      const response = await signUp(input)
      setUser(response)
      return response
    },
    signOut: async () => {
      await signOut()
      setUser(null)
      clearAuthToken()
    },
    refreshUser: async () => {
      const currentUser = await getCurrentUser()
      setUser(currentUser)
      return currentUser
    },
    updateUser: async (updates) => {
      const currentUser = await editUser(updates)
      setUser(currentUser)
      return currentUser
    },
  }), [isLoading, user])

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export const useAuth = () => {
  const context = useContext(AuthContext)

  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }

  return context
}