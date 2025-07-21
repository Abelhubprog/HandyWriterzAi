'use client'

import {
  DynamicContextProvider,
} from '@dynamic-labs/sdk-react-core'
import { EthereumWalletConnectors } from '@dynamic-labs/ethereum'
import { SolanaWalletConnectors } from '@dynamic-labs/solana'
import { useRouter } from 'next/navigation'

export function Providers({ children }: { children: React.ReactNode }) {
  const router = useRouter()
  return (
    <>
      {process.env.NEXT_PUBLIC_DYNAMIC_ENV_ID ? (
        <DynamicContextProvider
          settings={{
            environmentId: process.env.NEXT_PUBLIC_DYNAMIC_ENV_ID,
            walletConnectors: [
              EthereumWalletConnectors,
              SolanaWalletConnectors,
            ],
            events: {
              onAuthSuccess: () => {
                router.push('/dashboard')
              },
            },
          }}
        >
          {children}
        </DynamicContextProvider>
      ) : (
        children
      )}
    </>
  )
}
