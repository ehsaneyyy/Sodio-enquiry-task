import { apiClient } from "@/lib/apiClient"

import type { BatchCreatedResponse, BatchDetailResponse } from "@/features/batches/types/batchTypes"

export async function uploadEnquiryFile(file: File): Promise<BatchCreatedResponse> {
  const formData = new FormData()
  formData.append("file", file)
  const response = await apiClient.post<BatchCreatedResponse>("/batches", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  })
  return response.data
}

export async function fetchBatchDetail(batchId: number): Promise<BatchDetailResponse> {
  const response = await apiClient.get<BatchDetailResponse>(`/batches/${batchId}`)
  return response.data
}

export async function retryFailedBatchItems(batchId: number): Promise<BatchCreatedResponse> {
  const response = await apiClient.post<BatchCreatedResponse>(`/batches/${batchId}/retry-failed`)
  return response.data
}
