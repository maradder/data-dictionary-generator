import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

/**
 * Demo component to test ErrorBoundary functionality
 * This component intentionally throws errors when the button is clicked
 *
 * Usage: Wrap this component with ErrorBoundary to see error handling in action
 */
export function ErrorBoundaryDemo() {
  const [shouldThrow, setShouldThrow] = useState(false)

  if (shouldThrow) {
    // This will trigger the ErrorBoundary
    throw new Error('Demo error: This is an intentional error to test the ErrorBoundary!')
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>ErrorBoundary Test Component</CardTitle>
        <CardDescription>
          Click the button below to trigger an error and see the ErrorBoundary in action
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Button
          onClick={() => setShouldThrow(true)}
          variant="destructive"
        >
          Trigger Error
        </Button>
      </CardContent>
    </Card>
  )
}
