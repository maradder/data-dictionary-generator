import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'

export type UploadStatus = 'uploading' | 'parsing' | 'analyzing' | 'complete' | 'error'

interface UploadProgressProps {
  status: UploadStatus
  progress: number
  fileName?: string
  error?: string
  estimatedTimeRemaining?: number
  onCancel?: () => void
}

const statusConfig: Record<UploadStatus, { label: string; color: string; description: string }> = {
  uploading: {
    label: 'Uploading',
    color: 'bg-blue-500',
    description: 'Uploading file to server...',
  },
  parsing: {
    label: 'Parsing',
    color: 'bg-purple-500',
    description: 'Parsing JSON structure...',
  },
  analyzing: {
    label: 'Analyzing',
    color: 'bg-amber-500',
    description: 'Analyzing fields and generating insights...',
  },
  complete: {
    label: 'Complete',
    color: 'bg-green-500',
    description: 'Processing complete!',
  },
  error: {
    label: 'Error',
    color: 'bg-red-500',
    description: 'An error occurred during processing',
  },
}

export function UploadProgress({
  status,
  progress,
  fileName,
  error,
  estimatedTimeRemaining,
  onCancel,
}: UploadProgressProps) {
  const config = statusConfig[status]
  const isProcessing = status !== 'complete' && status !== 'error'
  const canCancel = isProcessing && status === 'uploading' && onCancel

  const formatTime = (seconds: number) => {
    if (seconds < 60) {
      return `${Math.round(seconds)}s`
    }
    const minutes = Math.floor(seconds / 60)
    const remainingSeconds = Math.round(seconds % 60)
    return `${minutes}m ${remainingSeconds}s`
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-3">
            <span>Processing Upload</span>
            {isProcessing && (
              <div className="flex space-x-1">
                <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
              </div>
            )}
          </CardTitle>
          <Badge variant={status === 'error' ? 'destructive' : 'default'} className={config.color}>
            {config.label}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* File Name */}
        {fileName && (
          <div className="text-sm text-muted-foreground">
            <span className="font-medium">File:</span> {fileName}
          </div>
        )}

        {/* Progress Bar */}
        <div className="space-y-2">
          <div className="flex justify-between items-center text-sm">
            <span className="text-muted-foreground">{config.description}</span>
            <span className="font-medium">{Math.round(progress)}%</span>
          </div>
          <Progress
            value={progress}
            className={isProcessing ? 'transition-all duration-500' : ''}
          />
        </div>

        {/* Processing Stages */}
        <div className="flex items-center justify-between text-xs pt-2">
          <div className="flex items-center gap-2">
            <div className={`w-3 h-3 rounded-full ${
              status === 'uploading' ? 'bg-blue-500 animate-pulse' :
              ['parsing', 'analyzing', 'complete'].includes(status) ? 'bg-green-500' :
              'bg-gray-300'
            }`} />
            <span className={status === 'uploading' ? 'font-medium' : 'text-muted-foreground'}>
              Upload
            </span>
          </div>

          <div className="flex items-center gap-2">
            <div className={`w-3 h-3 rounded-full ${
              status === 'parsing' ? 'bg-purple-500 animate-pulse' :
              ['analyzing', 'complete'].includes(status) ? 'bg-green-500' :
              'bg-gray-300'
            }`} />
            <span className={status === 'parsing' ? 'font-medium' : 'text-muted-foreground'}>
              Parse
            </span>
          </div>

          <div className="flex items-center gap-2">
            <div className={`w-3 h-3 rounded-full ${
              status === 'analyzing' ? 'bg-amber-500 animate-pulse' :
              status === 'complete' ? 'bg-green-500' :
              'bg-gray-300'
            }`} />
            <span className={status === 'analyzing' ? 'font-medium' : 'text-muted-foreground'}>
              Analyze
            </span>
          </div>

          <div className="flex items-center gap-2">
            <div className={`w-3 h-3 rounded-full ${
              status === 'complete' ? 'bg-green-500' :
              status === 'error' ? 'bg-red-500' :
              'bg-gray-300'
            }`} />
            <span className={status === 'complete' ? 'font-medium' : 'text-muted-foreground'}>
              Complete
            </span>
          </div>
        </div>

        {/* Estimated Time */}
        {isProcessing && estimatedTimeRemaining !== undefined && estimatedTimeRemaining > 0 && (
          <div className="text-xs text-muted-foreground text-center">
            Estimated time remaining: {formatTime(estimatedTimeRemaining)}
          </div>
        )}

        {/* Error Message */}
        {status === 'error' && error && (
          <div className="bg-destructive/10 border border-destructive/20 rounded-md p-3 text-sm text-destructive">
            {error}
          </div>
        )}

        {/* Success Message */}
        {status === 'complete' && (
          <div className="bg-green-500/10 border border-green-500/20 rounded-md p-3 text-sm text-green-700 dark:text-green-400 text-center">
            Dictionary created successfully! Redirecting...
          </div>
        )}

        {/* Cancel Button */}
        {canCancel && (
          <div className="flex justify-center pt-2">
            <Button
              variant="outline"
              size="sm"
              onClick={onCancel}
              className="text-muted-foreground hover:text-destructive"
            >
              Cancel Upload
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
