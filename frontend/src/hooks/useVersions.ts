import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { versionsApi } from '@/api'
import toast from 'react-hot-toast'
import { dictionaryKeys } from './useDictionaries'

// Query Keys
export const versionKeys = {
  all: ['versions'] as const,
  lists: () => [...versionKeys.all, 'list'] as const,
  list: (dictionaryId: string) => [...versionKeys.lists(), dictionaryId] as const,
  details: () => [...versionKeys.all, 'detail'] as const,
  detail: (dictionaryId: string, versionId: string) =>
    [...versionKeys.details(), dictionaryId, versionId] as const,
  comparisons: () => [...versionKeys.all, 'comparison'] as const,
  comparison: (dictionaryId: string, version1: number, version2: number) =>
    [...versionKeys.comparisons(), dictionaryId, version1, version2] as const,
}

// List versions for dictionary
export function useVersions(dictionaryId: string) {
  return useQuery({
    queryKey: versionKeys.list(dictionaryId),
    queryFn: () => versionsApi.list(dictionaryId),
    enabled: !!dictionaryId,
  })
}

// Get specific version
export function useVersion(dictionaryId: string, versionId: string) {
  return useQuery({
    queryKey: versionKeys.detail(dictionaryId, versionId),
    queryFn: () => versionsApi.get(dictionaryId, versionId),
    enabled: !!dictionaryId && !!versionId,
  })
}

// Create new version mutation
export function useCreateVersion() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({
      dictionaryId,
      file,
      notes,
      generateAiDescriptions = true,
    }: {
      dictionaryId: string
      file: File
      notes?: string
      generateAiDescriptions?: boolean
    }) => versionsApi.create(dictionaryId, file, notes, generateAiDescriptions),
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({
        queryKey: versionKeys.list(variables.dictionaryId),
      })
      queryClient.invalidateQueries({
        queryKey: dictionaryKeys.detail(variables.dictionaryId),
      })
      toast.success(`Version ${data.version_number} created successfully`)
    },
    onError: (error: Error & { response?: { data?: { detail?: string } } }) => {
      const message = error.response?.data?.detail || 'Failed to create version'
      toast.error(message)
    },
  })
}

// Compare versions
export function useVersionComparison(
  dictionaryId: string,
  version1?: number,
  version2?: number
) {
  return useQuery({
    queryKey: versionKeys.comparison(dictionaryId, version1!, version2!),
    queryFn: () => versionsApi.compare(dictionaryId, version1!, version2!),
    enabled: !!dictionaryId && version1 !== undefined && version2 !== undefined,
  })
}

// Export comparison to Excel
export function useExportVersionComparison() {
  return useMutation({
    mutationFn: ({
      dictionaryId,
      version1,
      version2,
    }: {
      dictionaryId: string
      version1: number
      version2: number
    }) => versionsApi.exportComparison(dictionaryId, { version_1: version1, version_2: version2 }),
    onSuccess: (blob, variables) => {
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `version-comparison-v${variables.version1}-v${variables.version2}.xlsx`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
      toast.success('Comparison exported successfully')
    },
    onError: (error: Error & { response?: { data?: { detail?: string } } }) => {
      const message = error.response?.data?.detail || 'Failed to export comparison'
      toast.error(message)
    },
  })
}
