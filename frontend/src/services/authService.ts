import { apiClient } from '../lib/apiClient'
import { clearAuthToken, setAuthToken } from '../lib/authStorage'

export type user = {
  id: string
  name: string
  email: string
  avatar_url: string
  xp_points: number
  level: number
  streak: number
  created_at: string
}

export type AuthCredentials = {
  email: string
  password: string
}

export type SignUpInput = AuthCredentials & {
  name: string
}

export type EditUserInput = Partial<Pick<user, 'name' | 'avatar_url' | 'xp_points' | 'level' | 'streak'>>

type AuthResponse = {
  user: user
  token: string
}

type ApiEnvelope<T> = {
  success: boolean
  message?: string
  data?: T
}

const toError = (error: unknown): Error => {
  if (axios.isAxiosError(error)) {
    const message = (error.response?.data as { message?: string } | undefined)?.message
    if (message) {
      return new Error(message)
    }
  }

  if (error instanceof Error) {
    return error
  }

  return new Error('An unexpected authentication error occurred.')
}

const persistAuth = (response: AuthResponse) => {
  setAuthToken(response.token)
  return response.user
}

export const signIn = async ({ email, password }: AuthCredentials) => {
  try {
    const { data } = await apiClient.post<ApiEnvelope<AuthResponse>>('/auth/login', {
      email: email.trim(),
      password,
    })

    const authData = data.data

    if (!authData?.user || !authData.token) {
      throw new Error('Invalid login response from server')
    }

    return persistAuth(authData)
  } catch (error) {
    throw toError(error)
  }
}

export const signUp = async ({ name, email, password }: SignUpInput) => {
  try {
    const resolvedName = name.trim() || email.trim().split('@')[0] || 'New User'

    const { data } = await apiClient.post<ApiEnvelope<AuthResponse>>('/auth/register', {
      name: resolvedName,
      email: email.trim(),
      password,
    })

    const authData = data.data

    if (!authData?.user || !authData.token) {
      throw new Error('Invalid registration response from server')
    }

    return persistAuth(authData)
  } catch (error) {
    throw toError(error)
  }
}

export const signInWithGoogle = async () => {
  throw new Error('Google sign-in is not configured for this backend.')
}

export const signOut = async () => {
  clearAuthToken()

  try {
    await apiClient.post('/auth/logout')
  } catch (error) {
    throw toError(error)
  }
}

export const getCurrentUser = async () => {
  try {
    const { data } = await apiClient.get<ApiEnvelope<{ user: user }>>('/auth/me')
    return data.data?.user ?? null
  } catch (error) {
    clearAuthToken()
    throw toError(error)
  }
}

export const editUser = async (updates: EditUserInput) => {
  try {
    const { data } = await apiClient.put<ApiEnvelope<{ user: user }>>('/users/me', updates)
    return data.data?.user ?? null
  } catch (error) {
    throw toError(error)
  }
}
