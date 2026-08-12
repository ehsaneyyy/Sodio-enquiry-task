import type { ExtractionStatus } from "@/features/enquiries/types/enquiryTypes"

export interface BatchCreatedResponse {
  batch_id: number
  enquiry_ids: number[]
  total: number
}

export interface BatchItemResponse {
  enquiry_id: number
  extraction_status: ExtractionStatus
  error: string | null
}

export interface BatchDetailResponse {
  id: number
  filename: string | null
  status: string
  total: number
  completed_count: number
  failed_count: number
  pending_count: number
  processing_count: number
  items: BatchItemResponse[]
}
