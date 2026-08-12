import { createBrowserRouter, Navigate } from "react-router-dom"

import { AppShell } from "@/app/AppShell"
import { BatchesPage } from "@/features/batches/pages/BatchesPage"
import { EnquiriesDashboardPage } from "@/features/enquiries/pages/EnquiriesDashboardPage"
import { EnquiryDetailPage } from "@/features/enquiries/pages/EnquiryDetailPage"

export const appRouter = createBrowserRouter([
  {
    element: <AppShell />,
    children: [
      { index: true, element: <Navigate to="/enquiries" replace /> },
      { path: "enquiries", element: <EnquiriesDashboardPage /> },
      { path: "enquiries/:enquiryId", element: <EnquiryDetailPage /> },
      { path: "batches", element: <BatchesPage /> },
      { path: "*", element: <Navigate to="/enquiries" replace /> },
    ],
  },
])
