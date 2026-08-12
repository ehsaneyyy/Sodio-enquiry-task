import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"

import {
  createEnquiry,
  fetchEnquiries,
  fetchEnquiryDetail,
  patchEnquiry,
  reExtractEnquiry,
  resetEnquiryOverrides,
} from "@/features/enquiries/api/enquiriesApi"
import type {
  CreateEnquiryPayload,
  EnquiryListQueryParams,
  PatchEnquiryPayload,
} from "@/features/enquiries/types/enquiryTypes"

const enquiriesQueryKey = ["enquiries"]

export function useEnquiriesQuery(params: EnquiryListQueryParams) {
  return useQuery({
    queryKey: [...enquiriesQueryKey, params],
    queryFn: () => fetchEnquiries(params),
    placeholderData: (previousData) => previousData,
  })
}

export function useEnquiryDetailQuery(enquiryId: number | undefined) {
  return useQuery({
    queryKey: ["enquiries", enquiryId],
    queryFn: () => fetchEnquiryDetail(enquiryId as number),
    enabled: enquiryId !== undefined,
  })
}

export function useCreateEnquiryMutation() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (payload: CreateEnquiryPayload) => createEnquiry(payload),
    onSuccess: (createdEnquiry) => {
      queryClient.invalidateQueries({ queryKey: enquiriesQueryKey })
      queryClient.setQueryData(["enquiries", createdEnquiry.id], createdEnquiry)
    },
  })
}

export function usePatchEnquiryMutation() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ enquiryId, payload }: { enquiryId: number; payload: PatchEnquiryPayload }) =>
      patchEnquiry(enquiryId, payload),
    onSuccess: (updatedEnquiry) => {
      queryClient.invalidateQueries({ queryKey: enquiriesQueryKey })
      queryClient.setQueryData(["enquiries", updatedEnquiry.id], updatedEnquiry)
    },
  })
}

export function useReExtractEnquiryMutation() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (enquiryId: number) => reExtractEnquiry(enquiryId),
    onSuccess: (updatedEnquiry) => {
      queryClient.invalidateQueries({ queryKey: enquiriesQueryKey })
      queryClient.setQueryData(["enquiries", updatedEnquiry.id], updatedEnquiry)
    },
  })
}

export function useResetEnquiryOverridesMutation() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (enquiryId: number) => resetEnquiryOverrides(enquiryId),
    onSuccess: (updatedEnquiry) => {
      queryClient.invalidateQueries({ queryKey: enquiriesQueryKey })
      queryClient.setQueryData(["enquiries", updatedEnquiry.id], updatedEnquiry)
    },
  })
}
