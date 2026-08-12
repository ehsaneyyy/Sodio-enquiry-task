import { useState } from "react"
import { Check, X } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { TableCell, TableRow } from "@/components/ui/table"
import { ExtractionStatusBadge } from "@/features/enquiries/components/badges"
import { usePatchEnquiryMutation } from "@/features/enquiries/hooks/useEnquiries"
import type {
  EnquiryListItem,
  EnquiryStatus,
  ServiceLine,
} from "@/features/enquiries/types/enquiryTypes"

const serviceLines: ServiceLine[] = ["ai", "blockchain", "web", "mobile", "game", "other"]
const enquiryStatuses: EnquiryStatus[] = ["new", "contacted", "qualified", "dropped"]

interface DraftState {
  company: string
  contact_name: string
  contact_email: string
  service_line: string
  budget: string
  timeline: string
  is_genuine: string
  status: EnquiryStatus
}

function draftFromEnquiry(enquiry: EnquiryListItem): DraftState {
  return {
    company: enquiry.company ?? "",
    contact_name: enquiry.contact_name ?? "",
    contact_email: enquiry.contact_email ?? "",
    service_line: enquiry.service_line ?? "",
    budget: enquiry.budget_raw ?? "",
    timeline: enquiry.timeline ?? "",
    is_genuine: enquiry.is_genuine === null ? "unset" : enquiry.is_genuine ? "true" : "false",
    status: enquiry.status,
  }
}

export function InlineEnquiryEditRow({
  enquiry,
  onSaved,
  onCancel,
}: {
  enquiry: EnquiryListItem
  onSaved: () => void
  onCancel: () => void
}) {
  const [draft, setDraft] = useState<DraftState>(() => draftFromEnquiry(enquiry))
  const patchEnquiryMutation = usePatchEnquiryMutation()

  function updateField<K extends keyof DraftState>(field: K, value: DraftState[K]) {
    setDraft((currentDraft) => ({ ...currentDraft, [field]: value }))
  }

  function handleSave() {
    const overrides: Record<string, unknown> = {}
    if (draft.company !== (enquiry.company ?? "")) {
      overrides.company = draft.company.trim() || null
    }
    if (draft.contact_name !== (enquiry.contact_name ?? "")) {
      overrides.contact_name = draft.contact_name.trim() || null
    }
    if (draft.contact_email !== (enquiry.contact_email ?? "")) {
      overrides.contact_email = draft.contact_email.trim() || null
    }
    if (draft.service_line !== (enquiry.service_line ?? "")) {
      overrides.service_line = draft.service_line || null
    }
    if (draft.budget !== (enquiry.budget_raw ?? "")) {
      overrides.budget = draft.budget.trim() || null
    }
    if (draft.timeline !== (enquiry.timeline ?? "")) {
      overrides.timeline = draft.timeline.trim() || null
    }
    const currentGenuine = enquiry.is_genuine === null ? "unset" : enquiry.is_genuine ? "true" : "false"
    if (draft.is_genuine !== currentGenuine) {
      overrides.is_genuine = draft.is_genuine === "unset" ? null : draft.is_genuine === "true"
    }

    const hasOverrides = Object.keys(overrides).length > 0
    const hasStatusChange = draft.status !== enquiry.status
    if (!hasOverrides && !hasStatusChange) {
      onCancel()
      return
    }

    patchEnquiryMutation.mutate(
      {
        enquiryId: enquiry.id,
        payload: {
          ...(hasStatusChange ? { status: draft.status } : {}),
          ...(hasOverrides ? { overrides } : {}),
        },
      },
      { onSuccess: onSaved },
    )
  }

  const isSaving = patchEnquiryMutation.isPending

  return (
    <TableRow className="bg-muted/30">
      <TableCell>
        <Input
          value={draft.company}
          onChange={(event) => updateField("company", event.target.value)}
          className="h-8"
        />
      </TableCell>
      <TableCell>
        <div className="flex flex-col gap-1">
          <Input
            value={draft.contact_name}
            onChange={(event) => updateField("contact_name", event.target.value)}
            placeholder="Contact name"
            className="h-8"
          />
          <Input
            value={draft.contact_email}
            onChange={(event) => updateField("contact_email", event.target.value)}
            placeholder="Email"
            className="h-8"
          />
        </div>
      </TableCell>
      <TableCell>
        <span className="text-muted-foreground text-xs">auto</span>
      </TableCell>
      <TableCell>
        <Select value={draft.status} onValueChange={(value) => updateField("status", value as EnquiryStatus)}>
          <SelectTrigger className="h-8 w-32">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {enquiryStatuses.map((status) => (
              <SelectItem key={status} value={status}>
                {status}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </TableCell>
      <TableCell>
        <div className="flex flex-col items-start gap-1">
          <ExtractionStatusBadge extractionStatus={enquiry.extraction_status} />
          <Select
            value={draft.is_genuine}
            onValueChange={(value) => updateField("is_genuine", value)}
          >
            <SelectTrigger className="h-8 w-28">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="true">Genuine</SelectItem>
              <SelectItem value="false">Not genuine</SelectItem>
              <SelectItem value="unset">Unset</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </TableCell>
      <TableCell>
        <Select
          value={draft.service_line}
          onValueChange={(value) => updateField("service_line", value)}
        >
          <SelectTrigger className="h-8 w-32">
            <SelectValue placeholder="—" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="">Unset</SelectItem>
            {serviceLines.map((serviceLine) => (
              <SelectItem key={serviceLine} value={serviceLine}>
                {serviceLine}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </TableCell>
      <TableCell>
        <Input
          value={draft.budget}
          onChange={(event) => updateField("budget", event.target.value)}
          placeholder="e.g. £40k"
          className="h-8"
        />
      </TableCell>
      <TableCell>
        <Input
          value={draft.timeline}
          onChange={(event) => updateField("timeline", event.target.value)}
          placeholder="e.g. ASAP"
          className="h-8"
        />
      </TableCell>
      <TableCell>
        <div className="flex items-center gap-1">
          <Button size="icon" variant="ghost" className="size-8" onClick={handleSave} disabled={isSaving}>
            <Check />
          </Button>
          <Button size="icon" variant="ghost" className="size-8" onClick={onCancel} disabled={isSaving}>
            <X />
          </Button>
        </div>
      </TableCell>
    </TableRow>
  )
}
