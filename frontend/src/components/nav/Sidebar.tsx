"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";

const routes = [
  { href: "/app/dashboard", label: "Dashboard" },
  { href: "/app/settings/general", label: "General" },
  { href: "/app/settings/billing", label: "Billing" },
  { href: "/app/settings/usage", label: "Usage" },
  { href: "/app/settings/security", label: "Security" },
  { href: "/app/profile", label: "Profile" },
];

export default function Sidebar() {
  const pathname = usePathname();

  if (pathname === "/app/chat") {
    return null;
  }

  return (
    <div className="hidden border-r bg-muted/40 md:block">
      <div className="flex h-full max-h-screen flex-col gap-2">
        <div className="flex h-14 items-center border-b px-4 lg:h-[60px] lg:px-6">
          <Link href="/" className="flex items-center gap-2 font-semibold">
            <span>HandyWriterz</span>
          </Link>
        </div>
        <div className="flex-1">
          <nav className="grid items-start px-2 text-sm font-medium lg:px-4">
            {routes.map((route) => (
              <Link
                key={route.href}
                href={route.href}
                className={cn(
                  "flex items-center gap-3 rounded-lg px-3 py-2 text-muted-foreground transition-all hover:text-primary",
                  { "bg-muted text-primary": pathname === route.href }
                )}
              >
                {route.label}
              </Link>
            ))}
          </nav>
        </div>
      </div>
    </div>
  );
}
