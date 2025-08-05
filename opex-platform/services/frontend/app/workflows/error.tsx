'use client'
 
export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  return (
    <div style={{ padding: 40 }}>
      <h2>Something went wrong while loading the workflows!</h2>
      <pre>Error: {error.message}</pre>
      <button onClick={() => reset()}>
        Try again
      </button>
    </div>
  )
}
