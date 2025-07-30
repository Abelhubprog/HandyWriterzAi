'use client';

import { DynamicContextProvider } from '@dynamic-labs/sdk-react-core';
import { EthereumWalletConnectors } from '@dynamic-labs/ethereum';
import { SolanaWalletConnectors } from '@dynamic-labs/solana';

export default function DynamicProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  const environmentId = process.env.NEXT_PUBLIC_DYNAMIC_ENV_ID;

  if (!environmentId) {
    console.warn('Dynamic.xyz environment ID not configured. Using mock authentication.');
    return <>{children}</>;
  }

  return (
    <DynamicContextProvider
      settings={{
        environmentId,
        walletConnectors: [EthereumWalletConnectors, SolanaWalletConnectors],
        eventsCallbacks: {
          onAuthSuccess: (args) => {
            console.log('Dynamic auth success:', args);
            // Redirect to chat after successful auth
            if (window.location.pathname === '/auth') {
              window.location.href = '/chat';
            }
          },
          onLogout: () => {
            console.log('Dynamic logout');
            // Redirect to home after logout
            if (window.location.pathname !== '/') {
              window.location.href = '/';
            }
          },
        },
        // Enable email and social login
        initialAuthenticationMode: 'connect-only',
        socialProvidersFilter: (providers) => {
          // Enable email, Google, and Twitter
          return providers.filter(p =>
            ['email', 'google', 'twitter'].includes(p.provider)
          );
        },
        // Customize the UI
        cssOverrides: `
          .dynamic-widget-card {
            background-color: #1f2937 !important;
            border: 1px solid #374151 !important;
          }
          .dynamic-widget-card * {
            color: #f3f4f6 !important;
          }
          .dynamic-button-primary {
            background-color: #2563eb !important;
            color: white !important;
          }
          .dynamic-button-primary:hover {
            background-color: #1d4ed8 !important;
          }
        `,
      }}
    >
      {children}
    </DynamicContextProvider>
  );
}
