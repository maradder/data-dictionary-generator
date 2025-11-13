import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { databaseApi } from '@/api/database'
import toast from 'react-hot-toast'

export const databaseKeys = {
  all: ['database'] as const,
  stats: () => [...databaseKeys.all, 'stats'] as const,
  health: () => [...databaseKeys.all, 'health'] as const,
  tables: () => [...databaseKeys.all, 'tables'] as const,
}

export function useDatabaseStats() {
  return useQuery({
    queryKey: databaseKeys.stats(),
    queryFn: () => databaseApi.getStats(),
    refetchInterval: 30000, // Refresh every 30 seconds
  })
}

export function useDatabaseHealth() {
  return useQuery({
    queryKey: databaseKeys.health(),
    queryFn: () => databaseApi.getHealth(),
    refetchInterval: 60000, // Check every minute
  })
}

export function useTableStats() {
  return useQuery({
    queryKey: databaseKeys.tables(),
    queryFn: () => databaseApi.getTableStats(),
  })
}

export function useClearDatabase() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (confirm: string) => databaseApi.clearDatabase(confirm),
    onSuccess: () => {
      // Invalidate all queries since database is cleared
      queryClient.invalidateQueries()
      toast.success('Database cleared successfully')
    },
    onError: (error: Error & { response?: { data?: { detail?: string } } }) => {
      const message = error.response?.data?.detail || 'Failed to clear database'
      toast.error(message)
    },
  })
}

export function useDownloadBackup() {
  return useMutation({
    mutationFn: () => databaseApi.downloadBackup(),
    onSuccess: (blob) => {
      // Create download link
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5)
      link.download = `database-backup-${timestamp}.db`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
      toast.success('Database backup downloaded successfully')
    },
    onError: (error: Error & { response?: { data?: { detail?: string } } }) => {
      const message = error.response?.data?.detail || 'Failed to download backup'
      toast.error(message)
    },
  })
}

export function useImportBackup() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ file, conflictMode }: { file: File; conflictMode?: 'skip' | 'overwrite' | 'fail' }) =>
      databaseApi.importBackup(file, conflictMode),
    onSuccess: () => {
      // Invalidate all dictionary queries
      queryClient.invalidateQueries({ queryKey: ['dictionaries'] })
      queryClient.invalidateQueries({ queryKey: databaseKeys.stats() })
      toast.success('Backup imported successfully')
    },
    onError: (error: Error & { response?: { data?: { detail?: string } } }) => {
      const message = error.response?.data?.detail || 'Failed to import backup'
      toast.error(message)
    },
  })
}
