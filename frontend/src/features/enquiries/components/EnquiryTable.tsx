import { Link } from "react-router-dom"

import { Skeleton } from "@/components/ui/skeleton"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import {
  EnquiryStatusBadge,
  ExtractionStatusBadge,
  GenuineBadge,
  PriorityBadge,
} from "@/features/enquiries/components/badges"
import { formatBudget, formatDateTime } from "@/features/enquiries/components/formatting"
import type { EnquiryListItem } from "@/features/enquiries/types/enquiryTypes"

function EnquiryTableSkeleton() {
  return (
    <div className="space-y-3">
      <Skeleton className="h-10 w-full" />
      <Skeleton className="h-10 w-full" />
      <Skeleton className="h-10 w-full" />
      <Skeleton className="h-10 w-full" />
    </div>
  )
}

function EmptyEnquiriesState() {
  return (
    <div className="flex flex-col items-center justify-center gap-2 py-16 text-center">
      <p className="text-muted-foreground text-sm">No enquiries match the current filters.</p>
      <p className="text-muted-foreground text-xs">Add one manually or upload a batch file to get started.</p>
    </div>
  )
}

export function EnquiryTable({
  enquiries,
  isLoading,
}: {
  enquiries: EnquiryListItem[]
  isLoading: boolean
}) {
  if (isLoading) {
    return <EnquiryTableSkeleton />
  }

  if (enquiries.length === 0) {
    return <EmptyEnquiriesState />
  }

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Company</TableHead>
          <TableHead>Contact</TableHead>
          <TableHead>Priority</TableHead>
          <TableHead>Status</TableHead>
          <TableHead>Extraction</TableHead>
          <TableHead>Service</TableHead>
          <TableHead>Budget</TableHead>
          <TableHead>Timeline</TableHead>
          <TableHead>Received</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {enquiries.map((enquiry) => (
          <TableRow key={enquiry.id}>
            <TableCell>
              <Link to={`/enquiries/${enquiry.id}`} className="font-medium hover:underline">
                {enquiry.company ?? "—"}
              </Link>
            </TableCell>
            <TableCell>
              <div className="text-sm">{enquiry.contact_name ?? "—"}</div>
              {enquiry.contact_email ? (
                <div className="text-muted-foreground text-xs">{enquiry.contact_email}</div>
              ) : null}
            </TableCell>
            <TableCell>
              <PriorityBadge priority={enquiry.priority} />
            </TableCell>
            <TableCell>
              <EnquiryStatusBadge status={enquiry.status} />
            </TableCell>
            <TableCell>
              <div className="flex items-center gap-2">
                <ExtractionStatusBadge extractionStatus={enquiry.extraction_status} />
                <GenuineBadge isGenuine={enquiry.is_genuine} />
              </div>
            </TableCell>
            <TableCell className="text-muted-foreground">{enquiry.service_line ?? "—"}</TableCell>
            <TableCell>
              {formatBudget(enquiry.budget_min, enquiry.budget_max, enquiry.budget_currency)}
              {enquiry.budget_raw ? (
                <div className="text-muted-foreground max-w-48 truncate text-xs" title={enquiry.budget_raw}>
                  {enquiry.budget_raw}
                </div>
              ) : null}
            </TableCell>
            <TableCell className="text-muted-foreground">{enquiry.timeline ?? "—"}</TableCell>
            <TableCell className="text-muted-foreground">{formatDateTime(enquiry.created_at)}</TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  )
}
