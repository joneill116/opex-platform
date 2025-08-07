/**
 * Next.js App Router Loading Component
 * Provides loading state for page transitions
 * Implements Martin Fowler's Loading State pattern
 */
export default function Loading() {
  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
          <div className="text-center">
            <div className="mx-auto mb-4">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
            </div>
            <h2 className="text-lg font-medium text-gray-900 mb-2">
              Loading...
            </h2>
            <p className="text-sm text-gray-600">
              Please wait while we load your content.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
