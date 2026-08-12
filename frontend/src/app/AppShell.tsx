import { NavLink, Outlet } from "react-router-dom"
import { InboxIcon, LayersIcon } from "lucide-react"

import { cn } from "@/lib/utils"
import { Separator } from "@/components/ui/separator"

const navItems = [
  { to: "/enquiries", label: "Enquiries", icon: InboxIcon },
  { to: "/batches", label: "Batches", icon: LayersIcon },
]

function AppHeader() {
  return (
    <header className="sticky top-0 z-40 border-b bg-background/95 backdrop-blur">
      <div className="mx-auto flex h-14 max-w-6xl items-center gap-6 px-4">
        <NavLink to="/enquiries" className="flex items-center gap-2 text-sm font-semibold">
          <span className="bg-primary text-primary-foreground flex size-7 items-center justify-center rounded-md text-xs font-bold">
            ST
          </span>
          Sodio Triage
        </NavLink>
        <nav className="flex items-center gap-1">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                cn(
                  "text-muted-foreground hover:text-foreground flex items-center gap-2 rounded-md px-3 py-1.5 text-sm font-medium transition-colors",
                  isActive && "bg-accent text-accent-foreground",
                )
              }
            >
              <item.icon className="size-4" />
              {item.label}
            </NavLink>
          ))}
        </nav>
      </div>
    </header>
  )
}

export function AppShell() {
  return (
    <div className="flex min-h-screen flex-col">
      <AppHeader />
      <main className="mx-auto w-full max-w-6xl flex-1 px-4 py-6">
        <Outlet />
      </main>
      <footer className="border-t py-4">
        <div className="mx-auto max-w-6xl px-4">
          <Separator className="mb-4" />
          <p className="text-muted-foreground text-xs">
            Enquiry triage dashboard · backend stub provider by default
          </p>
        </div>
      </footer>
    </div>
  )
}
