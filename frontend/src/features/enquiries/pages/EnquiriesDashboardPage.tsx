import { useState } from "react"
import { ArrowDownWideNarrow, Clock3 } from "lucide-react"

import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Separator } from "@/components/ui/separator"
import { apiErrorMessage } from "@/lib/apiClient"
import { CreateEnquiryDialog } from "@/features/enquiries/components/CreateEnquiryDialog"
import { EnquiryFilters } from "@/features/enquiries/components/EnquiryFilters"
import { EnquiryTable } from "@/features/enquiries/components/EnquiryTable"
import { useEnquiriesQuery } from "@/features/enquiries/hooks/useEnquiries"
import type {
  EnquiryListQueryParams,
  EnquirySort,
} from "@/features/enquiries/types/enquiryTypes"

export function EnquiriesDashboardPage() {
  const [filters, setFilters] = useState<EnquiryListQueryParams>({ sort: "priority" })
  const enquiriesQuery = useEnquiriesQuery(filters)

  function updateSort(sort: EnquirySort) {
    setFilters((currentFilters) => ({ ...currentFilters, sort }))
  }

  return (
    <div className="flex flex-col gap-6">
      <Card>
        <CardHeader>
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div>
              <CardTitle>Enquiries</CardTitle>
              <CardDescription>Inbound enquiries triaged by priority.</CardDescription>
            </div>
            <CreateEnquiryDialog />
          </div>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap items-center justify-between gap-4">
            <EnquiryFilters
              filters={filters}
              onFiltersChange={setFilters}
            />
            <div className="flex items-center gap-2">
              <Button
                variant={filters.sort === "priority" ? "secondary" : "ghost"}
                size="sm"
                onClick={() => updateSort("priority")}
              >
                <ArrowDownWideNarrow />
                Priority
              </Button>
              <Button
                variant={filters.sort === "date" ? "secondary" : "ghost"}
                size="sm"
                onClick={() => updateSort("date")}
              >
                <Clock3 />
                Newest
              </Button>
            </div>
          </div>
          <Separator className="my-4" />
          {enquiriesQuery.isError ? (
            <p className="text-destructive text-sm">{apiErrorMessage(enquiriesQuery.error)}</p>
          ) : (
            <EnquiryTable
              enquiries={enquiriesQuery.data ?? []}
              isLoading={enquiriesQuery.isLoading}
            />
          )}
        </CardContent>
      </Card>
    </div>
  )
}
