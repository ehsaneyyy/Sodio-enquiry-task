export type ServiceLine = "ai" | "blockchain" | "web" | "mobile" | "game" | "other"

export type EnquiryStatus = "new" | "contacted" | "qualified" | "dropped"

export type Priority = "high" | "medium" | "low"

export type ExtractionStatus = "pending" | "processing" | "success" | "failed"

export type TimelineUrgency = "asap" | "near" | "later" | "flexible" | "unknown"

export type EnquirySort = "date" | "priority"

export interface EnquiryListItem {
  id: number
  status: EnquiryStatus
  priority: Priority
  extraction_status: ExtractionStatus
  source: string
  created_at: string
  overridden_fields: string[]
  company: string | null
  contact_name: string | null
  contact_email: string | null
  service_line: ServiceLine | null
  budget_raw: string | null
  budget_min: number | null
  budget_max: number | null
  budget_currency: string | null
  timeline: string | null
  summary: string | null
  is_genuine: boolean | null
}

export interface ExtractionRun {
  id: number
  created_at: string
  model: string | null
  prompt_version: string | null
  company: string | null
  contact_name: string | null
  contact_email: string | null
  service_line: ServiceLine | null
  budget_raw: string | null
  budget_min: number | null
  budget_max: number | null
  budget_currency: string | null
  timeline: string | null
  timeline_urgency: TimelineUrgency | null
  summary: string | null
  is_genuine: boolean | null
  error: string | null
}

export interface EnquiryDetail {
  id: number
  original_text: string
  source: string
  status: EnquiryStatus
  priority: Priority
  extraction_status: ExtractionStatus
  extraction_error: string | null
  created_at: string
  updated_at: string
  overridden_fields: string[]
  effective: EnquiryListItem
  latest_extraction: ExtractionRun | null
  extraction_history: ExtractionRun[]
}

export interface EnquiryListQueryParams {
  service_line?: ServiceLine | null
  priority?: Priority | null
  status?: EnquiryStatus | null
  sort?: EnquirySort
}

export interface CreateEnquiryPayload {
  original_text: string
}

export interface PatchEnquiryPayload {
  status?: EnquiryStatus | null
  overrides?: Record<string, unknown>
}
