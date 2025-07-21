import { useState, useEffect, useCallback } from 'react';
import { walletProviderManager, type EthereumProvider } from '@/lib/walletProvider';

export interface WalletState {
  isConnected: boolean;
  address: string | null;
  provider: EthereumProvider | null;
  availableProviders: string[];
  activeProviderName: string | null;
  isConnecting: boolean;
  error: string | null;
}

export const useWallet = () => {
  const [state, setState] = useState<WalletState>({
    isConnected: false,
    address: null,
    provider: null,
    availableProviders: [],
    activeProviderName: null,
    isConnecting: false,
    error: null
  });

  useEffect(() => {
    const availableProviders = walletProviderManager.getAvailableProviders();
    const provider = walletProviderManager.getProvider();
    
    setState(prev => ({
      ...prev,
      availableProviders,
      provider,
      activeProviderName: availableProviders[0] || null
    }));

    // Check if already connected
    if (provider) {
      checkConnection(provider);
    }
  }, []);

  const checkConnection = async (provider: EthereumProvider) => {
    try {
      const accounts = await provider.request({ method: 'eth_accounts' });
      if (accounts.length > 0) {
        setState(prev => ({
          ...prev,
          isConnected: true,
          address: accounts[0],
          error: null
        }));
      }
    } catch (error) {
      console.error('Error checking wallet connection:', error);
    }
  };

  const connect = useCallback(async (providerName?: string) => {
    setState(prev => ({ ...prev, isConnecting: true, error: null }));

    try {
      const provider = walletProviderManager.getProvider(providerName);
      
      if (!provider) {
        throw new Error('No wallet provider available');
      }

      const accounts = await provider.request({
        method: 'eth_requestAccounts'
      });

      if (accounts.length > 0) {
        setState(prev => ({
          ...prev,
          isConnected: true,
          address: accounts[0],
          provider,
          activeProviderName: providerName || prev.activeProviderName,
          isConnecting: false,
          error: null
        }));

        // Set up event listeners
        provider.on('accountsChanged', handleAccountsChanged);
        provider.on('chainChanged', handleChainChanged);
      }
    } catch (error: any) {
      setState(prev => ({
        ...prev,
        isConnecting: false,
        error: error.message || 'Failed to connect wallet'
      }));
    }
  }, []);

  const disconnect = useCallback(async () => {
    const { provider } = state;
    
    if (provider) {
      // Remove event listeners
      provider.removeListener('accountsChanged', handleAccountsChanged);
      provider.removeListener('chainChanged', handleChainChanged);
    }

    setState(prev => ({
      ...prev,
      isConnected: false,
      address: null,
      error: null
    }));
  }, [state.provider]);

  const switchProvider = useCallback(async (providerName: string) => {
    if (walletProviderManager.switchProvider(providerName)) {
      await disconnect();
      await connect(providerName);
    }
  }, [connect, disconnect]);

  const handleAccountsChanged = useCallback((accounts: string[]) => {
    if (accounts.length === 0) {
      disconnect();
    } else {
      setState(prev => ({
        ...prev,
        address: accounts[0]
      }));
    }
  }, [disconnect]);

  const handleChainChanged = useCallback((chainId: string) => {
    // Refresh the page to avoid any issues
    window.location.reload();
  }, []);

  const sendTransaction = useCallback(async (transactionParams: any) => {
    const { provider } = state;
    
    if (!provider || !state.isConnected) {
      throw new Error('Wallet not connected');
    }

    try {
      const txHash = await provider.request({
        method: 'eth_sendTransaction',
        params: [transactionParams]
      });
      return txHash;
    } catch (error: any) {
      throw new Error(error.message || 'Transaction failed');
    }
  }, [state.provider, state.isConnected]);

  return {
    ...state,
    connect,
    disconnect,
    switchProvider,
    sendTransaction
  };
};