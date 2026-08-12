import axios from "axios"

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "/api",
  timeout: 60000,
})

export function apiErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const detail = (error.response?.data as { detail?: string | unknown } | undefined)?.detail
    if (typeof detail === "string") {
      return detail
    }
    return error.message
  }
  if (error instanceof Error) {
    return error.message
  }
  return "Unexpected error"
}
