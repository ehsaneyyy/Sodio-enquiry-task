import { useEffect, useState } from "react"

import { BatchProgressCard } from "@/features/batches/components/BatchProgressCard"
import { BatchUploadCard } from "@/features/batches/components/BatchUploadCard"

const TRACKED_BATCH_IDS_KEY = "sodio.trackedBatchIds"

function readTrackedBatchIds(): number[] {
  try {
    const rawValue = localStorage.getItem(TRACKED_BATCH_IDS_KEY)
    if (!rawValue) {
      return []
    }
    const parsedValue = JSON.parse(rawValue)
    if (Array.isArray(parsedValue)) {
      return parsedValue.filter((value): value is number => typeof value === "number")
    }
  } catch {
    return []
  }
  return []
}

export function BatchesPage() {
  const [trackedBatchIds, setTrackedBatchIds] = useState<number[]>(readTrackedBatchIds)

  useEffect(() => {
    localStorage.setItem(TRACKED_BATCH_IDS_KEY, JSON.stringify(trackedBatchIds))
  }, [trackedBatchIds])

  function handleBatchCreated(batchId: number) {
    setTrackedBatchIds((currentIds) => [batchId, ...currentIds.filter((id) => id !== batchId)])
  }

  return (
    <div className="flex flex-col gap-6">
      <BatchUploadCard onBatchCreated={handleBatchCreated} />
      <div className="flex flex-col gap-4">
        {trackedBatchIds.map((batchId) => (
          <BatchProgressCard key={batchId} batchId={batchId} />
        ))}
      </div>
    </div>
  )
}
