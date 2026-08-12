import { apiClient } from "@/lib/apiClient"

import type {
  CreateEnquiryPayload,
  EnquiryDetail,
  EnquiryListItem,
  EnquiryListQueryParams,
  PatchEnquiryPayload,
} from "@/features/enquiries/types/enquiryTypes"

export async function fetchEnquiries(params: EnquiryListQueryParams): Promise<EnquiryListItem[]> {
  const response = await apiClient.get<EnquiryListItem[]>("/enquiries", { params })
  return response.data
}

export async function fetchEnquiryDetail(enquiryId: number): Promise<EnquiryDetail> {
  const response = await apiClient.get<EnquiryDetail>(`/enquiries/${enquiryId}`)
  return response.data
}

export async function createEnquiry(payload: CreateEnquiryPayload): Promise<EnquiryDetail> {
  const response = await apiClient.post<EnquiryDetail>("/enquiries", payload)
  return response.data
}

export async function patchEnquiry(enquiryId: number, payload: PatchEnquiryPayload): Promise<EnquiryDetail> {
  const response = await apiClient.patch<EnquiryDetail>(`/enquiries/${enquiryId}`, payload)
  return response.data
}

export async function reExtractEnquiry(enquiryId: number): Promise<EnquiryDetail> {
  const response = await apiClient.post<EnquiryDetail>(`/enquiries/${enquiryId}/re-extract`)
  return response.data
}

export async function resetEnquiryOverrides(enquiryId: number): Promise<EnquiryDetail> {
  const response = await apiClient.post<EnquiryDetail>(`/enquiries/${enquiryId}/reset-overrides`)
  return response.data
}
