import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"

import {
  fetchBatchDetail,
  retryFailedBatchItems,
  uploadEnquiryFile,
} from "@/features/batches/api/batchesApi"

const batchQueryKey = (batchId: number) => ["batches", batchId]

export function useCreateBatchMutation() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (file: File) => uploadEnquiryFile(file),
    onSuccess: (createdBatch) => {
      queryClient.setQueryData(batchQueryKey(createdBatch.batch_id), {
        id: createdBatch.batch_id,
        filename: null,
        status: "processing",
        total: createdBatch.total,
        completed_count: 0,
        failed_count: 0,
        pending_count: createdBatch.total,
        processing_count: 0,
        items: createdBatch.enquiry_ids.map((enquiryId) => ({
          enquiry_id: enquiryId,
          extraction_status: "pending",
          error: null,
        })),
      })
    },
  })
}

export function useBatchDetailQuery(batchId: number | undefined) {
  return useQuery({
    queryKey: batchQueryKey(batchId as number),
    queryFn: () => fetchBatchDetail(batchId as number),
    enabled: batchId !== undefined,
    refetchInterval: (query) => {
      const currentStatus = query.state.data?.status
      if (currentStatus === "completed" || currentStatus === "failed") {
        return false
      }
      return 1500
    },
  })
}

export function useRetryFailedBatchMutation() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (batchId: number) => retryFailedBatchItems(batchId),
    onSuccess: (retryResult) => {
      queryClient.setQueryData(batchQueryKey(retryResult.batch_id), {
        id: retryResult.batch_id,
        filename: null,
        status: "processing",
        total: retryResult.total,
        completed_count: 0,
        failed_count: 0,
        pending_count: retryResult.total,
        processing_count: 0,
        items: retryResult.enquiry_ids.map((enquiryId) => ({
          enquiry_id: enquiryId,
          extraction_status: "pending",
          error: null,
        })),
      })
    },
  })
}
