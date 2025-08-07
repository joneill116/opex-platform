'use client'

import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'
import { useMemo } from 'react'

export function Providers({ children }: { children: React.ReactNode }) {
  // Optimize QueryClient creation with useMemo for performance
  const queryClient = useMemo(
    () => new QueryClient({
      defaultOptions: {
        queries: {
          staleTime: 5 * 60 * 1000, // 5 minutes - optimized for workflow data
          gcTime: 10 * 60 * 1000, // 10 minutes (replaces cacheTime in React Query v5)
          refetchOnWindowFocus: false,
          refetchOnMount: false,
          retry: 3,
          retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000)
        },
        mutations: {
          retry: 1
        }
      },
    }),
    []
  )

  return (
    <QueryClientProvider client={queryClient}>
      {children}
      {process.env.NODE_ENV === 'development' && (
        <ReactQueryDevtools initialIsOpen={false} />
      )}
    </QueryClientProvider>
  )
}
