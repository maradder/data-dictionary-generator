# Common Components

This directory contains reusable common components used throughout the application.

## ErrorBoundary

The `ErrorBoundary` component catches React errors in its child component tree and displays a user-friendly error message.

### Features

- **Error Catching**: Catches JavaScript errors anywhere in the child component tree
- **User-Friendly UI**: Displays a polished error message using shadcn/ui components
- **Error Logging**: Logs errors to the console for debugging
- **Reset Functionality**: "Try Again" button to reset the error state
- **Navigation Fallback**: "Go to Home" button for quick recovery
- **Development Details**: Shows component stack trace in development mode
- **Custom Fallback**: Supports custom fallback UI
- **Error Callback**: Optional callback for external error tracking (Sentry, LogRocket, etc.)

### Basic Usage

```tsx
import { ErrorBoundary } from '@/components/common/ErrorBoundary'

function App() {
  return (
    <ErrorBoundary>
      <YourComponent />
    </ErrorBoundary>
  )
}
```

### Advanced Usage

#### With Custom Fallback UI

```tsx
<ErrorBoundary
  fallback={
    <div className="text-center p-8">
      <h2>Oops! Something went wrong</h2>
      <p>Please refresh the page</p>
    </div>
  }
>
  <YourComponent />
</ErrorBoundary>
```

#### With Error Tracking

```tsx
import * as Sentry from '@sentry/react'

<ErrorBoundary
  onError={(error, errorInfo) => {
    // Send to error tracking service
    Sentry.captureException(error, {
      contexts: {
        react: {
          componentStack: errorInfo.componentStack,
        },
      },
    })
  }}
>
  <YourComponent />
</ErrorBoundary>
```

#### Using HOC Pattern

```tsx
import { withErrorBoundary } from '@/components/common/ErrorBoundary'

const SafeComponent = withErrorBoundary(YourComponent, {
  onError: (error, errorInfo) => {
    console.error('Error in SafeComponent:', error)
  }
})
```

### Implementation in App

The ErrorBoundary is implemented at multiple levels in the application:

1. **App Level**: Wraps the entire application to catch top-level errors
2. **Route Level**: Each major route is wrapped to provide granular error handling

```tsx
// App.tsx
function App() {
  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<MainLayout />}>
              <Route
                index
                element={
                  <ErrorBoundary>
                    <DictionariesListPage />
                  </ErrorBoundary>
                }
              />
              {/* More routes... */}
            </Route>
          </Routes>
        </BrowserRouter>
      </QueryClientProvider>
    </ErrorBoundary>
  )
}
```

### Props

| Prop | Type | Required | Description |
|------|------|----------|-------------|
| `children` | `ReactNode` | Yes | The component tree to protect with error boundary |
| `fallback` | `ReactNode` | No | Custom fallback UI to display when error occurs |
| `onError` | `(error: Error, errorInfo: ErrorInfo) => void` | No | Callback fired when error is caught |

### Error UI Components

The ErrorBoundary uses the following shadcn/ui components:

- `Card` - Main container for error UI
- `Alert` - Displays error message with destructive variant
- `Button` - "Try Again" and "Go to Home" actions

### Development vs Production

- **Development**: Shows detailed component stack trace
- **Production**: Hides technical details, shows user-friendly message only

### Testing the ErrorBoundary

Use the `ErrorBoundaryDemo` component to test error boundary functionality:

```tsx
import { ErrorBoundary } from '@/components/common/ErrorBoundary'
import { ErrorBoundaryDemo } from '@/components/common/ErrorBoundaryDemo'

function TestPage() {
  return (
    <ErrorBoundary>
      <ErrorBoundaryDemo />
    </ErrorBoundary>
  )
}
```

### Best Practices

1. **Granular Boundaries**: Use multiple error boundaries to isolate errors to specific parts of the UI
2. **Error Tracking**: Always integrate with an error tracking service in production
3. **User Communication**: Provide clear, actionable messages to users
4. **Recovery Options**: Always provide a way for users to recover (reset, navigate home)
5. **Logging**: Log errors for debugging, but sanitize sensitive data first

### What Error Boundaries Don't Catch

Error boundaries do **not** catch errors for:

- Event handlers (use try-catch instead)
- Asynchronous code (setTimeout, promises)
- Server-side rendering
- Errors thrown in the error boundary itself

For async errors, use try-catch blocks and display errors via state:

```tsx
function MyComponent() {
  const [error, setError] = useState<Error | null>(null)

  const handleAsyncAction = async () => {
    try {
      await someAsyncOperation()
    } catch (err) {
      setError(err as Error)
    }
  }

  if (error) {
    return <div>Error: {error.message}</div>
  }

  return <button onClick={handleAsyncAction}>Click me</button>
}
```

### Related Components

- `Alert` - Used for displaying error messages
- `Card` - Used for error UI container
- `Button` - Used for recovery actions

### References

- [React Error Boundaries Documentation](https://react.dev/reference/react/Component#catching-rendering-errors-with-an-error-boundary)
- [shadcn/ui Alert Component](https://ui.shadcn.com/docs/components/alert)
