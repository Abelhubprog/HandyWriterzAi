import { Inter } from 'next/font/google'
import './globals.css'
import { ThemeProvider } from '@/contexts/ThemeContext'
import { Toaster } from '@/components/ui/toaster'
import DynamicProvider from '@/lib/dynamic'

const inter = Inter({ subsets: ['latin'] })

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <DynamicProvider>
          <ThemeProvider>
            {children}
            <Toaster />
          </ThemeProvider>
        </DynamicProvider>
      </body>
    </html>
  )
}
