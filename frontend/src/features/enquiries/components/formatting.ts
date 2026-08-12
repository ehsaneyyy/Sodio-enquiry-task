export function formatBudget(
  budgetMin: number | null,
  budgetMax: number | null,
  budgetCurrency: string | null,
): string {
  if (budgetMin === null && budgetMax === null) {
    return "—"
  }
  const formatter = new Intl.NumberFormat("en-US", {
    style: budgetCurrency ? "currency" : "decimal",
    currency: budgetCurrency ?? undefined,
    maximumFractionDigits: 0,
  })
  const formattedMin = budgetMin !== null ? formatter.format(budgetMin) : null
  const formattedMax = budgetMax !== null ? formatter.format(budgetMax) : null
  if (formattedMin !== null && formattedMax !== null && formattedMin !== formattedMax) {
    return `${formattedMin}–${formattedMax}`
  }
  return formattedMin ?? formattedMax ?? "—"
}

export function formatDateTime(value: string): string {
  return new Intl.DateTimeFormat("en-GB", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value))
}
