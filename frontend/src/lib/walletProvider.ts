/**
 * Wallet Provider Conflict Resolution
 * Handles multiple wallet extension conflicts by detecting and prioritizing providers
 */

export interface EthereumProvider {
  isMetaMask?: boolean;
  isDynamic?: boolean;
  isCoinbaseWallet?: boolean;
  request: (args: any) => Promise<any>;
  on: (event: string, handler: any) => void;
  removeListener: (event: string, handler: any) => void;
}

class WalletProviderManager {
  private providers: Map<string, EthereumProvider> = new Map();
  private activeProvider: EthereumProvider | null = null;

  constructor() {
    this.detectProviders();
  }

  private detectProviders() {
    const win = window as any;
    
    // Store original ethereum provider if exists
    if (win.ethereum) {
      this.providers.set('default', win.ethereum);
    }

    // Check for specific wallet providers
    if (win.ethereum?.isMetaMask) {
      this.providers.set('metamask', win.ethereum);
    }
    
    if (win.ethereum?.isDynamic) {
      this.providers.set('dynamic', win.ethereum);
    }
    
    if (win.ethereum?.isCoinbaseWallet) {
      this.providers.set('coinbase', win.ethereum);
    }

    // Check for multiple providers
    if (win.ethereum?.providers?.length > 0) {
      win.ethereum.providers.forEach((provider: EthereumProvider, index: number) => {
        if (provider.isMetaMask) {
          this.providers.set('metamask', provider);
        } else if (provider.isDynamic) {
          this.providers.set('dynamic', provider);
        } else if (provider.isCoinbaseWallet) {
          this.providers.set('coinbase', provider);
        } else {
          this.providers.set(`provider_${index}`, provider);
        }
      });
    }

    // Set priority order (Dynamic > MetaMask > Coinbase > Default)
    this.setActiveProvider();
  }

  private setActiveProvider() {
    const priorityOrder = ['dynamic', 'metamask', 'coinbase', 'default'];
    
    for (const providerName of priorityOrder) {
      if (this.providers.has(providerName)) {
        this.activeProvider = this.providers.get(providerName)!;
        console.log(`Active wallet provider: ${providerName}`);
        break;
      }
    }

    if (!this.activeProvider && this.providers.size > 0) {
      this.activeProvider = Array.from(this.providers.values())[0];
      console.log('Using first available provider');
    }
  }

  getProvider(preferredProvider?: string): EthereumProvider | null {
    if (preferredProvider && this.providers.has(preferredProvider)) {
      return this.providers.get(preferredProvider)!;
    }
    return this.activeProvider;
  }

  getAvailableProviders(): string[] {
    return Array.from(this.providers.keys());
  }

  switchProvider(providerName: string): boolean {
    if (this.providers.has(providerName)) {
      this.activeProvider = this.providers.get(providerName)!;
      console.log(`Switched to provider: ${providerName}`);
      return true;
    }
    return false;
  }

  // Safe ethereum object access
  safeEthereumAccess(callback: (provider: EthereumProvider) => void) {
    try {
      if (this.activeProvider) {
        callback(this.activeProvider);
      } else {
        console.warn('No ethereum provider available');
      }
    } catch (error) {
      console.error('Error accessing ethereum provider:', error);
    }
  }
}

// Singleton instance
export const walletProviderManager = new WalletProviderManager();

// Wallet conflicts are now handled by ethereum-protect.js loaded in index.html