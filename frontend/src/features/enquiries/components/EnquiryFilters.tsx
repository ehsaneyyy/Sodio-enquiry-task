import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import type {
  EnquiryListQueryParams,
  EnquiryStatus,
  Priority,
  ServiceLine,
} from "@/features/enquiries/types/enquiryTypes"

const serviceLines: ServiceLine[] = ["ai", "blockchain", "web", "mobile", "game", "other"]
const priorities: Priority[] = ["high", "medium", "low"]
const enquiryStatuses: EnquiryStatus[] = ["new", "contacted", "qualified", "dropped"]

function FilterSelect({
  placeholder,
  value,
  onValueChange,
  options,
}: {
  placeholder: string
  value: string | undefined
  onValueChange: (value: string) => void
  options: string[]
}) {
  return (
    <Select value={value} onValueChange={onValueChange}>
      <SelectTrigger className="w-40">
        <SelectValue placeholder={placeholder} />
      </SelectTrigger>
      <SelectContent>
        {options.map((option) => (
          <SelectItem key={option} value={option}>
            {option}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  )
}

export function EnquiryFilters({
  filters,
  onFiltersChange,
}: {
  filters: EnquiryListQueryParams
  onFiltersChange: (filters: EnquiryListQueryParams) => void
}) {
  return (
    <div className="flex flex-wrap items-center gap-2">
      <FilterSelect
        placeholder="Service line"
        value={filters.service_line ?? undefined}
        onValueChange={(value) => onFiltersChange({ ...filters, service_line: value as ServiceLine })}
        options={serviceLines}
      />
      <FilterSelect
        placeholder="Priority"
        value={filters.priority ?? undefined}
        onValueChange={(value) => onFiltersChange({ ...filters, priority: value as Priority })}
        options={priorities}
      />
      <FilterSelect
        placeholder="Status"
        value={filters.status ?? undefined}
        onValueChange={(value) => onFiltersChange({ ...filters, status: value as EnquiryStatus })}
        options={enquiryStatuses}
      />
    </div>
  )
}
