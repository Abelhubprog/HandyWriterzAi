'use client';
// Force update to clear any caching issues

import React, { Component, ErrorInfo, ReactNode } from 'react';
import { AlertCircle, RefreshCw, Home, Bug } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
  resetOnPropsChange?: boolean;
  resetKeys?: Array<string | number>;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
  eventId: string | null;
}

export class ErrorBoundary extends Component<Props, State> {
  private resetTimeoutId: number | null = null;

  constructor(props: Props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
      eventId: null,
    };
  }

  static getDerivedStateFromError(error: Error): Partial<State> {
    return {
      hasError: true,
      error,
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    this.setState({
      error,
      errorInfo,
    });

    // Log to external service
    this.logErrorToService(error, errorInfo);
    
    // Call custom error handler
    this.props.onError?.(error, errorInfo);
  }

  componentDidUpdate(prevProps: Props) {
    const { resetKeys } = this.props;
    const { hasError } = this.state;

    if (hasError && prevProps.resetKeys !== resetKeys) {
      if (resetKeys?.some((key, index) => key !== prevProps.resetKeys?.[index])) {
        this.resetErrorBoundary();
      }
    }
  }

  logErrorToService = async (error: Error, errorInfo: ErrorInfo) => {
    try {
      // Log to your error tracking service (e.g., Sentry)
      const errorData = {
        message: error.message,
        stack: error.stack,
        componentStack: errorInfo.componentStack,
        timestamp: new Date().toISOString(),
        userAgent: navigator.userAgent,
        url: window.location.href,
      };

      // Send to your logging endpoint
      await fetch('/api/errors', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(errorData),
      });
    } catch (logError) {
      console.error('Failed to log error:', logError);
    }
  };

  resetErrorBoundary = () => {
    if (this.resetTimeoutId) {
      clearTimeout(this.resetTimeoutId);
    }

    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
      eventId: null,
    });
  };

  handleRetry = () => {
    this.resetErrorBoundary();
  };

  handleReload = () => {
    window.location.reload();
  };

  handleGoHome = () => {
    window.location.href = '/';
  };

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 p-4">
          <Card className="max-w-2xl w-full">
            <CardHeader className="text-center">
              <div className="flex justify-center mb-4">
                <AlertCircle className="h-12 w-12 text-red-500" />
              </div>
              <CardTitle className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                Something went wrong
              </CardTitle>
            </CardHeader>
            
            <CardContent className="space-y-6">
              <div className="text-center text-gray-600 dark:text-gray-400">
                <p className="mb-2">
                  We apologize for the inconvenience. An unexpected error has occurred.
                </p>
                <p className="text-sm">
                  Our team has been notified and is working to fix this issue.
                </p>
              </div>

              {process.env.NODE_ENV === 'development' && this.state.error && (
                <details className="bg-gray-100 dark:bg-gray-800 rounded-lg p-4">
                  <summary className="cursor-pointer font-medium text-gray-900 dark:text-gray-100 flex items-center gap-2">
                    <Bug className="h-4 w-4" />
                    Error Details (Development Mode)
                  </summary>
                  <div className="mt-4 space-y-2">
                    <div>
                      <strong className="text-red-600 dark:text-red-400">Error:</strong>
                      <pre className="text-sm text-gray-700 dark:text-gray-300 mt-1 whitespace-pre-wrap">
                        {this.state.error.message}
                      </pre>
                    </div>
                    {this.state.error.stack && (
                      <div>
                        <strong className="text-red-600 dark:text-red-400">Stack Trace:</strong>
                        <pre className="text-xs text-gray-600 dark:text-gray-400 mt-1 whitespace-pre-wrap overflow-x-auto">
                          {this.state.error.stack}
                        </pre>
                      </div>
                    )}
                    {this.state.errorInfo?.componentStack && (
                      <div>
                        <strong className="text-red-600 dark:text-red-400">Component Stack:</strong>
                        <pre className="text-xs text-gray-600 dark:text-gray-400 mt-1 whitespace-pre-wrap overflow-x-auto">
                          {this.state.errorInfo.componentStack}
                        </pre>
                      </div>
                    )}
                  </div>
                </details>
              )}

              <div className="flex flex-col sm:flex-row gap-3 justify-center">
                <Button
                  onClick={this.handleRetry}
                  className="flex items-center gap-2"
                  variant="default"
                >
                  <RefreshCw className="h-4 w-4" />
                  Try Again
                </Button>
                
                <Button
                  onClick={this.handleReload}
                  className="flex items-center gap-2"
                  variant="outline"
                >
                  <RefreshCw className="h-4 w-4" />
                  Reload Page
                </Button>
                
                <Button
                  onClick={this.handleGoHome}
                  className="flex items-center gap-2"
                  variant="outline"
                >
                  <Home className="h-4 w-4" />
                  Go Home
                </Button>
              </div>

              {this.state.eventId && (
                <div className="text-center text-xs text-gray-500 dark:text-gray-400">
                  Error ID: {this.state.eventId}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      );
    }

    return this.props.children;
  }
}

// HOC for wrapping components with error boundary
export function withErrorBoundary<T extends Record<string, unknown>>(
  Component: React.ComponentType<T>,
  errorBoundaryProps?: Omit<Props, 'children'>
) {
  const WrappedComponent = (props: T) => (
    <ErrorBoundary {...errorBoundaryProps}>
      <Component {...props} />
    </ErrorBoundary>
  );

  WrappedComponent.displayName = `withErrorBoundary(${Component.displayName || Component.name})`;

  return WrappedComponent;
}

// Hook for handling errors in functional components
export function useErrorHandler() {
  return React.useCallback((error: Error, errorInfo?: ErrorInfo) => {
    console.error('Error caught by useErrorHandler:', error, errorInfo);
    
    // Log to external service
    fetch('/api/errors', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message: error.message,
        stack: error.stack,
        timestamp: new Date().toISOString(),
        userAgent: navigator.userAgent,
        url: window.location.href,
      }),
    }).catch(console.error);
  }, []);
}