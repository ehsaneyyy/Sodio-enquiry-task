import { Link } from "react-router-dom"
import { Loader2, RefreshCcw } from "lucide-react"

import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"
import { ExtractionStatusBadge } from "@/features/enquiries/components/badges"
import { useBatchDetailQuery, useRetryFailedBatchMutation } from "@/features/batches/hooks/useBatches"

function BatchProgressSkeleton() {
  return <Skeleton className="h-44 w-full" />
}

export function BatchProgressCard({ batchId }: { batchId: number }) {
  const batchQuery = useBatchDetailQuery(batchId)
  const retryFailedMutation = useRetryFailedBatchMutation()

  if (batchQuery.isLoading) {
    return <BatchProgressSkeleton />
  }

  if (batchQuery.isError || !batchQuery.data) {
    return (
      <Card>
        <CardContent>
          <p className="text-destructive text-sm">
            {batchQuery.isError ? batchQuery.error.message : "Batch not found."}
          </p>
        </CardContent>
      </Card>
    )
  }

  const batch = batchQuery.data
  const isProcessing = batch.status !== "completed" && batch.status !== "failed"

  return (
    <Card>
      <CardHeader>
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <CardTitle className="text-base">
              Batch {batch.id}
              {batch.filename ? ` · ${batch.filename}` : ""}
            </CardTitle>
            <CardDescription>
              {batch.total} enquiries · {batch.completed_count} succeeded · {batch.failed_count} failed
            </CardDescription>
          </div>
          <div className="flex items-center gap-2">
            {isProcessing ? (
              <Badge variant="secondary">
                <Loader2 className="animate-spin" />
                {batch.status}
              </Badge>
            ) : (
              <Badge variant="default">{batch.status}</Badge>
            )}
            {batch.failed_count > 0 && !isProcessing ? (
              <Button
                size="sm"
                variant="outline"
                onClick={() => retryFailedMutation.mutate(batch.id)}
                disabled={retryFailedMutation.isPending}
              >
                <RefreshCcw />
                Retry failed
              </Button>
            ) : null}
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="grid gap-2 sm:grid-cols-2">
          {batch.items.map((item) => (
            <div
              key={item.enquiry_id}
              className="flex items-center justify-between gap-2 rounded-md border px-3 py-2"
            >
              <Link
                to={`/enquiries/${item.enquiry_id}`}
                className="text-sm font-medium hover:underline"
              >
                Enquiry #{item.enquiry_id}
              </Link>
              <ExtractionStatusBadge extractionStatus={item.extraction_status} />
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}
