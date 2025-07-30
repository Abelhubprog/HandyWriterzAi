'use client'

import { usePathname } from 'next/navigation'
import Sidebar from '@/components/nav/Sidebar'
import React from 'react'

export default function LayoutManager({
  children,
}: {
  children: React.ReactNode
}) {
  const pathname = usePathname()
  const isLandingPage = pathname === '/'

  if (isLandingPage) {
    return <>{children}</>
  }

  return (
    <div className="grid min-h-screen w-full md:grid-cols-[220px_1fr] lg:grid-cols-[280px_1fr]">
      <Sidebar />
      <div className="flex flex-col">
        <main className="flex flex-1 flex-col gap-4 p-4 lg:gap-6 lg:p-6">
          {children}
        </main>
      </div>
    </div>
  )
}
