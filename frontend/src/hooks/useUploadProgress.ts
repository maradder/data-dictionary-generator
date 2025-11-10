import { useState, useEffect, useCallback, useRef } from 'react'
import type { UploadStatus } from '@/components/upload/UploadProgress'

export interface UploadProgressState {
  status: UploadStatus
  progress: number
  estimatedTimeRemaining: number
  error: string | null
}

interface UseUploadProgressOptions {
  fileSize?: number
  isUploading: boolean
  onComplete?: () => void
  onError?: (error: string) => void
}

/**
 * Hook to simulate upload progress stages since backend processes synchronously.
 * Provides realistic feedback for user experience during file upload and processing.
 *
 * Stages:
 * 1. Uploading (0-30%): Based on file size, simulates upload progress
 * 2. Parsing (30-60%): Simulates JSON parsing
 * 3. Analyzing (60-100%): Simulates field analysis and AI description generation
 */
export function useUploadProgress({
  fileSize = 0,
  isUploading,
  onComplete,
  onError,
}: UseUploadProgressOptions) {
  const [state, setState] = useState<UploadProgressState>({
    status: 'uploading',
    progress: 0,
    estimatedTimeRemaining: 0,
    error: null,
  })

  const startTimeRef = useRef<number>(0)
  const progressIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null)
  const hasCompletedRef = useRef(false)

  // Estimate total time based on file size
  const estimateTotalTime = useCallback((size: number): number => {
    // Base time: 2 seconds
    // Additional time based on file size:
    // - Small files (< 1MB): 2-5 seconds
    // - Medium files (1-10MB): 5-15 seconds
    // - Large files (> 10MB): 15-60 seconds
    const mb = size / (1024 * 1024)
    if (mb < 1) {
      return 2000 + Math.random() * 3000
    } else if (mb < 10) {
      return 5000 + (mb * 1000) + Math.random() * 5000
    } else {
      return 15000 + (mb * 500) + Math.random() * 15000
    }
  }, [])

  // Calculate progress for a given stage
  const calculateStageProgress = useCallback((
    elapsedTime: number,
    totalTime: number,
    stageStart: number,
    stageEnd: number
  ): number => {
    const stageProgress = Math.min(elapsedTime / totalTime, 1)
    return stageStart + (stageProgress * (stageEnd - stageStart))
  }, [])

  // Start progress simulation
  useEffect(() => {
    if (!isUploading || hasCompletedRef.current) {
      return
    }

    startTimeRef.current = Date.now()
    const totalTime = estimateTotalTime(fileSize)

    progressIntervalRef.current = setInterval(() => {
      const elapsedTime = Date.now() - startTimeRef.current
      const timeProgress = Math.min(elapsedTime / totalTime, 1)

      let currentProgress: number
      let currentStatus: UploadStatus

      // Stage 1: Uploading (0-30%)
      if (timeProgress < 0.3) {
        currentProgress = calculateStageProgress(elapsedTime, totalTime * 0.3, 0, 30)
        currentStatus = 'uploading'
      }
      // Stage 2: Parsing (30-60%)
      else if (timeProgress < 0.6) {
        currentProgress = calculateStageProgress(
          elapsedTime - (totalTime * 0.3),
          totalTime * 0.3,
          30,
          60
        )
        currentStatus = 'parsing'
      }
      // Stage 3: Analyzing (60-100%)
      else {
        currentProgress = calculateStageProgress(
          elapsedTime - (totalTime * 0.6),
          totalTime * 0.4,
          60,
          100
        )
        currentStatus = 'analyzing'
      }

      const remainingTime = Math.max(0, (totalTime - elapsedTime) / 1000)

      setState({
        status: currentStatus,
        progress: Math.min(currentProgress, 99), // Keep at 99% until actual completion
        estimatedTimeRemaining: remainingTime,
        error: null,
      })
    }, 100) // Update every 100ms for smooth animation

    return () => {
      if (progressIntervalRef.current) {
        clearInterval(progressIntervalRef.current)
      }
    }
  }, [isUploading, fileSize, estimateTotalTime, calculateStageProgress])

  // Mark as complete
  const complete = useCallback(() => {
    if (hasCompletedRef.current) return

    hasCompletedRef.current = true
    if (progressIntervalRef.current) {
      clearInterval(progressIntervalRef.current)
    }

    setState({
      status: 'complete',
      progress: 100,
      estimatedTimeRemaining: 0,
      error: null,
    })

    setTimeout(() => {
      onComplete?.()
    }, 1500) // Wait 1.5s before calling onComplete to show success message
  }, [onComplete])

  // Mark as error
  const setError = useCallback((errorMessage: string) => {
    hasCompletedRef.current = true
    if (progressIntervalRef.current) {
      clearInterval(progressIntervalRef.current)
    }

    setState({
      status: 'error',
      progress: state.progress,
      estimatedTimeRemaining: 0,
      error: errorMessage,
    })

    onError?.(errorMessage)
  }, [state.progress, onError])

  // Reset progress
  const reset = useCallback(() => {
    hasCompletedRef.current = false
    if (progressIntervalRef.current) {
      clearInterval(progressIntervalRef.current)
    }
    setState({
      status: 'uploading',
      progress: 0,
      estimatedTimeRemaining: 0,
      error: null,
    })
  }, [])

  return {
    ...state,
    complete,
    setError,
    reset,
  }
}
