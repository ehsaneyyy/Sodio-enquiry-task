import { Badge } from "@/components/ui/badge"
import type { EnquiryStatus, ExtractionStatus, Priority } from "@/features/enquiries/types/enquiryTypes"

const priorityVariant: Record<Priority, "default" | "secondary" | "outline" | "destructive"> = {
  high: "destructive",
  medium: "secondary",
  low: "outline",
}

const statusVariant: Record<EnquiryStatus, "default" | "secondary" | "outline" | "destructive"> = {
  new: "secondary",
  contacted: "default",
  qualified: "default",
  dropped: "outline",
}

const extractionVariant: Record<ExtractionStatus, "default" | "secondary" | "outline" | "destructive"> = {
  pending: "outline",
  processing: "secondary",
  success: "default",
  failed: "destructive",
}

export function PriorityBadge({ priority }: { priority: Priority }) {
  return <Badge variant={priorityVariant[priority]}>{priority}</Badge>
}

export function EnquiryStatusBadge({ status }: { status: EnquiryStatus }) {
  return <Badge variant={statusVariant[status]}>{status}</Badge>
}

export function ExtractionStatusBadge({ extractionStatus }: { extractionStatus: ExtractionStatus }) {
  return <Badge variant={extractionVariant[extractionStatus]}>{extractionStatus}</Badge>
}

export function GenuineBadge({ isGenuine }: { isGenuine: boolean | null }) {
  if (isGenuine === null) {
    return <Badge variant="outline">unknown</Badge>
  }
  if (isGenuine) {
    return <Badge variant="default">genuine</Badge>
  }
  return <Badge variant="destructive">spam</Badge>
}
