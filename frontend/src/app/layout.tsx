import { Inter } from 'next/font/google'
import './globals.css'
import { Providers } from '@/components/providers'
import LayoutManager from '@/components/LayoutManager'

const inter = Inter({ subsets: ['latin'] })

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <Providers>
          <LayoutManager>{children}</LayoutManager>
        </Providers>
      </body>
    </html>
  )
}
