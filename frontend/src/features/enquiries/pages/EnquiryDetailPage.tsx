import { useState } from "react"
import { useParams } from "react-router-dom"
import { RotateCcw, Sparkles } from "lucide-react"

import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Skeleton } from "@/components/ui/skeleton"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { apiErrorMessage } from "@/lib/apiClient"
import {
  EnquiryStatusBadge,
  ExtractionStatusBadge,
  GenuineBadge,
  PriorityBadge,
} from "@/features/enquiries/components/badges"
import { formatBudget, formatDateTime } from "@/features/enquiries/components/formatting"
import {
  useEnquiryDetailQuery,
  usePatchEnquiryMutation,
  useReExtractEnquiryMutation,
  useResetEnquiryOverridesMutation,
} from "@/features/enquiries/hooks/useEnquiries"
import type {
  EnquiryDetail,
  EnquiryStatus,
  ExtractionRun,
  ServiceLine,
} from "@/features/enquiries/types/enquiryTypes"

const serviceLines: ServiceLine[] = ["ai", "blockchain", "web", "mobile", "game", "other"]
const enquiryStatuses: EnquiryStatus[] = ["new", "contacted", "qualified", "dropped"]

interface OverrideFormState {
  status: EnquiryStatus
  company: string
  contact_name: string
  contact_email: string
  service_line: ServiceLine | "unset"
  budget: string
  timeline: string
  summary: string
  is_genuine: "true" | "false" | "unset"
}

function initialFormState(enquiry: EnquiryDetail): OverrideFormState {
  const effective = enquiry.effective
  return {
    status: enquiry.status,
    company: effective.company ?? "",
    contact_name: effective.contact_name ?? "",
    contact_email: effective.contact_email ?? "",
    service_line: effective.service_line ?? "unset",
    budget: effective.budget_raw ?? "",
    timeline: effective.timeline ?? "",
    summary: effective.summary ?? "",
    is_genuine: effective.is_genuine === null ? "unset" : String(effective.is_genuine),
  }
}

function buildOverrideDiff(formState: OverrideFormState, extraction: ExtractionRun | null) {
  const overrides: Record<string, unknown> = {}
  const extractedCompany = extraction?.company ?? null
  const extractedContactName = extraction?.contact_name ?? null
  const extractedContactEmail = extraction?.contact_email ?? null
  const extractedServiceLine = extraction?.service_line ?? null
  const extractedBudgetRaw = extraction?.budget_raw ?? null
  const extractedTimeline = extraction?.timeline ?? null
  const extractedSummary = extraction?.summary ?? null
  const extractedIsGenuine = extraction?.is_genuine ?? null

  if (formState.company.trim() !== (extractedCompany ?? "")) {
    overrides.company = formState.company.trim() || null
  }
  if (formState.contact_name.trim() !== (extractedContactName ?? "")) {
    overrides.contact_name = formState.contact_name.trim() || null
  }
  if (formState.contact_email.trim() !== (extractedContactEmail ?? "")) {
    overrides.contact_email = formState.contact_email.trim() || null
  }
  if (formState.service_line !== (extractedServiceLine ?? "unset")) {
    overrides.service_line = formState.service_line === "unset" ? null : formState.service_line
  }
  if (formState.budget.trim() !== (extractedBudgetRaw ?? "")) {
    overrides.budget = formState.budget.trim() || null
  }
  if (formState.timeline.trim() !== (extractedTimeline ?? "")) {
    overrides.timeline = formState.timeline.trim() || null
  }
  if (formState.summary.trim() !== (extractedSummary ?? "")) {
    overrides.summary = formState.summary.trim() || null
  }
  const normalizedIsGenuine =
    formState.is_genuine === "unset" ? null : formState.is_genuine === "true"
  if (normalizedIsGenuine !== extractedIsGenuine) {
    overrides.is_genuine = normalizedIsGenuine
  }

  return overrides
}

function EnquiryDetailSkeleton() {
  return (
    <div className="space-y-6">
      <Skeleton className="h-9 w-72" />
      <div className="grid gap-6 md:grid-cols-2">
        <Skeleton className="h-40 w-full" />
        <Skeleton className="h-40 w-full" />
      </div>
    </div>
  )
}

function EffectiveValue({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div>
      <dt className="text-muted-foreground text-xs font-medium uppercase tracking-wide">{label}</dt>
      <dd className="mt-1 text-sm">{value}</dd>
    </div>
  )
}

function ExtractionHistoryList({ extractionHistory }: { extractionHistory: ExtractionRun[] }) {
  if (extractionHistory.length === 0) {
    return <p className="text-muted-foreground text-sm">No extraction runs yet.</p>
  }

  return (
    <div className="space-y-4">
      {[...extractionHistory].reverse().map((extraction) => (
        <Card key={extraction.id}>
          <CardContent>
            <div className="flex flex-wrap items-center justify-between gap-2">
              <p className="text-sm font-medium">
                {extraction.model ?? "Unknown model"}
                {extraction.prompt_version ? ` · ${extraction.prompt_version}` : ""}
              </p>
              <p className="text-muted-foreground text-xs">{formatDateTime(extraction.created_at)}</p>
            </div>
            {extraction.error ? (
              <p className="text-destructive mt-3 text-sm">{extraction.error}</p>
            ) : (
              <dl className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
                <EffectiveValue label="Company" value={extraction.company ?? "—"} />
                <EffectiveValue label="Contact" value={extraction.contact_name ?? "—"} />
                <EffectiveValue label="Email" value={extraction.contact_email ?? "—"} />
                <EffectiveValue label="Service" value={extraction.service_line ?? "—"} />
                <EffectiveValue
                  label="Budget"
                  value={formatBudget(extraction.budget_min, extraction.budget_max, extraction.budget_currency)}
                />
                <EffectiveValue label="Timeline" value={extraction.timeline ?? "—"} />
                <EffectiveValue label="Urgency" value={extraction.timeline_urgency ?? "—"} />
                <EffectiveValue label="Genuine" value={extraction.is_genuine === null ? "—" : extraction.is_genuine ? "Yes" : "No"} />
              </dl>
              {extraction.summary ? (
                <p className="text-muted-foreground mt-4 border-t pt-3 text-sm">{extraction.summary}</p>
              ) : null}
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}

function EnquiryOverridesPanel({ enquiry }: { enquiry: EnquiryDetail }) {
  const [formState, setFormState] = useState<OverrideFormState>(() => initialFormState(enquiry))
  const patchEnquiryMutation = usePatchEnquiryMutation()
  const resetOverridesMutation = useResetEnquiryOverridesMutation()

  function updateField<K extends keyof OverrideFormState>(field: K, value: OverrideFormState[K]) {
    setFormState((currentForm) => ({ ...currentForm, [field]: value }))
  }

  function handleSave() {
    const payload: { status?: EnquiryStatus; overrides?: Record<string, unknown> } = {}
    if (formState.status !== enquiry.status) {
      payload.status = formState.status
    }
    const overrideDiff = buildOverrideDiff(formState, enquiry.latest_extraction)
    if (Object.keys(overrideDiff).length > 0) {
      payload.overrides = overrideDiff
    }
    patchEnquiryMutation.mutate({ enquiryId: enquiry.id, payload })
  }

  function handleResetOverrides() {
    resetOverridesMutation.mutate(enquiry.id, {
      onSuccess: () => setFormState(initialFormState(enquiry)),
    })
  }

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div className="space-y-2">
          <Label htmlFor="override-status">Status</Label>
          <Select
            value={formState.status}
            onValueChange={(value) => updateField("status", value as EnquiryStatus)}
          >
            <SelectTrigger className="w-full">
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
        </div>
        <div className="space-y-2">
          <Label htmlFor="override-service-line">Service line</Label>
          <Select
            value={formState.service_line}
            onValueChange={(value) => updateField("service_line", value as ServiceLine | "unset")}
          >
            <SelectTrigger className="w-full">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="unset">Unset</SelectItem>
              {serviceLines.map((serviceLine) => (
                <SelectItem key={serviceLine} value={serviceLine}>
                  {serviceLine}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        <div className="space-y-2">
          <Label htmlFor="override-company">Company</Label>
          <Input
            id="override-company"
            value={formState.company}
            onChange={(event) => updateField("company", event.target.value)}
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="override-contact-name">Contact name</Label>
          <Input
            id="override-contact-name"
            value={formState.contact_name}
            onChange={(event) => updateField("contact_name", event.target.value)}
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="override-contact-email">Contact email</Label>
          <Input
            id="override-contact-email"
            value={formState.contact_email}
            onChange={(event) => updateField("contact_email", event.target.value)}
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="override-budget">Budget</Label>
          <Input
            id="override-budget"
            placeholder="e.g. around £40,000"
            value={formState.budget}
            onChange={(event) => updateField("budget", event.target.value)}
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="override-timeline">Timeline</Label>
          <Input
            id="override-timeline"
            value={formState.timeline}
            onChange={(event) => updateField("timeline", event.target.value)}
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="override-is-genuine">Genuine</Label>
          <Select
            value={formState.is_genuine}
            onValueChange={(value) => updateField("is_genuine", value as OverrideFormState["is_genuine"])}
          >
            <SelectTrigger className="w-full">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="true">True</SelectItem>
              <SelectItem value="false">False</SelectItem>
              <SelectItem value="unset">Unset</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>
      <div className="space-y-2">
        <Label htmlFor="override-summary">Summary</Label>
        <Textarea
          id="override-summary"
          value={formState.summary}
          onChange={(event) => updateField("summary", event.target.value)}
        />
      </div>
      {patchEnquiryMutation.isError ? (
        <p className="text-destructive text-sm">{apiErrorMessage(patchEnquiryMutation.error)}</p>
      ) : null}
      <div className="flex items-center gap-2">
        <Button onClick={handleSave} disabled={patchEnquiryMutation.isPending}>
          {patchEnquiryMutation.isPending ? "Saving…" : "Save changes"}
        </Button>
        <Button
          variant="outline"
          onClick={handleResetOverrides}
          disabled={resetOverridesMutation.isPending || enquiry.overridden_fields.length === 0}
        >
          <RotateCcw />
          Reset overrides
        </Button>
      </div>
    </div>
  )
}

export function EnquiryDetailPage() {
  const { enquiryId } = useParams<{ enquiryId: string }>()
  const enquiryIdNumber = enquiryId ? Number(enquiryId) : undefined
  const enquiryQuery = useEnquiryDetailQuery(enquiryIdNumber)
  const reExtractMutation = useReExtractEnquiryMutation()

  if (enquiryQuery.isLoading) {
    return <EnquiryDetailSkeleton />
  }

  if (enquiryQuery.isError || !enquiryQuery.data) {
    return (
      <p className="text-destructive">
        {enquiryQuery.isError
          ? apiErrorMessage(enquiryQuery.error)
          : "Enquiry not found."}
      </p>
    )
  }

  const enquiry = enquiryQuery.data

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div className="space-y-2">
          <div className="flex flex-wrap items-center gap-2">
            <h1 className="text-2xl font-semibold">{enquiry.effective.company ?? "Unnamed enquiry"}</h1>
            <PriorityBadge priority={enquiry.priority} />
            <EnquiryStatusBadge status={enquiry.status} />
            <ExtractionStatusBadge extractionStatus={enquiry.extraction_status} />
            <GenuineBadge isGenuine={enquiry.effective.is_genuine} />
          </div>
          <p className="text-muted-foreground text-sm">
            Received {formatDateTime(enquiry.created_at)} · {enquiry.source}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            onClick={() => reExtractMutation.mutate(enquiry.id)}
            disabled={reExtractMutation.isPending || enquiry.extraction_status === "processing"}
          >
            <Sparkles />
            {reExtractMutation.isPending ? "Extracting…" : "Re-extract"}
          </Button>
        </div>
      </div>

      {enquiry.extraction_error ? (
        <Card className="border-destructive/50">
          <CardContent>
            <p className="text-destructive text-sm">Extraction failed: {enquiry.extraction_error}</p>
          </CardContent>
        </Card>
      ) : null}

      <Tabs defaultValue="overview">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="history">
            Extraction history ({enquiry.extraction_history.length})
          </TabsTrigger>
          <TabsTrigger value="overrides">
            Overrides{enquiry.overridden_fields.length > 0 ? ` (${enquiry.overridden_fields.length})` : ""}
          </TabsTrigger>
        </TabsList>

        <TabsContent value="overview">
          <div className="grid gap-6 lg:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Extracted details</CardTitle>
                <CardDescription>
                  Effective values shown after applying any manual overrides.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <dl className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                  <EffectiveValue label="Company" value={enquiry.effective.company ?? "—"} />
                  <EffectiveValue label="Contact" value={enquiry.effective.contact_name ?? "—"} />
                  <EffectiveValue label="Email" value={enquiry.effective.contact_email ?? "—"} />
                  <EffectiveValue label="Service" value={enquiry.effective.service_line ?? "—"} />
                  <EffectiveValue
                    label="Budget"
                    value={formatBudget(enquiry.effective.budget_min, enquiry.effective.budget_max, enquiry.effective.budget_currency)}
                  />
                  <EffectiveValue label="Timeline" value={enquiry.effective.timeline ?? "—"} />
                  <EffectiveValue label="Urgency" value={enquiry.latest_extraction?.timeline_urgency ?? "—"} />
                  <EffectiveValue
                    label="Genuine"
                    value={
                      enquiry.effective.is_genuine === null
                        ? "—"
                        : enquiry.effective.is_genuine
                          ? "Yes"
                          : "No"
                    }
                  />
                </dl>
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle>Raw enquiry</CardTitle>
              </CardHeader>
              <CardContent>
                <pre className="bg-muted max-h-96 overflow-y-auto whitespace-pre-wrap rounded-md p-4 text-xs">
                  {enquiry.original_text}
                </pre>
              </CardContent>
            </Card>
          </div>
          {enquiry.effective.budget_raw ? (
            <Card>
              <CardHeader>
                <CardTitle>Budget context</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground text-sm">{enquiry.effective.budget_raw}</p>
              </CardContent>
            </Card>
          ) : null}
          {enquiry.effective.summary ? (
            <Card>
              <CardHeader>
                <CardTitle>Summary</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground text-sm">{enquiry.effective.summary}</p>
              </CardContent>
            </Card>
          ) : null}
        </TabsContent>

        <TabsContent value="history">
          <ExtractionHistoryList extractionHistory={enquiry.extraction_history} />
        </TabsContent>

        <TabsContent value="overrides">
          <Card>
            <CardHeader>
              <CardTitle>Manual overrides</CardTitle>
              <CardDescription>
                Changes are stored as overrides on top of the extracted values.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <EnquiryOverridesPanel key={enquiry.id} enquiry={enquiry} />
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
