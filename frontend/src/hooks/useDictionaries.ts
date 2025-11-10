import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { dictionariesApi } from '@/api'
import type { DictionaryUpdate } from '@/types/api'
import toast from 'react-hot-toast'

// Query Keys
export const dictionaryKeys = {
  all: ['dictionaries'] as const,
  lists: () => [...dictionaryKeys.all, 'list'] as const,
  list: (filters: { limit?: number; offset?: number }) =>
    [...dictionaryKeys.lists(), filters] as const,
  details: () => [...dictionaryKeys.all, 'detail'] as const,
  detail: (id: string, includeVersions?: boolean) =>
    [...dictionaryKeys.details(), id, includeVersions] as const,
}

// List dictionaries hook
export function useDictionaries(limit = 20, offset = 0) {
  return useQuery({
    queryKey: dictionaryKeys.list({ limit, offset }),
    queryFn: () => dictionariesApi.list({ limit, offset }),
  })
}

// Get single dictionary hook
export function useDictionary(id: string, includeVersions = false) {
  return useQuery({
    queryKey: dictionaryKeys.detail(id, includeVersions),
    queryFn: () => dictionariesApi.get(id, includeVersions),
    enabled: !!id,
  })
}

// Create dictionary mutation
export function useCreateDictionary() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({
      file,
      name,
      description,
      generateAiDescriptions = true,
    }: {
      file: File
      name: string
      description?: string
      generateAiDescriptions?: boolean
    }) => dictionariesApi.create(file, name, description, generateAiDescriptions),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: dictionaryKeys.lists() })
      toast.success(`Dictionary "${data.name}" created successfully`)
    },
    onError: (error: Error & { response?: { data?: { detail?: string } } }) => {
      const message = error.response?.data?.detail || 'Failed to create dictionary'
      toast.error(message)
    },
  })
}

// Update dictionary mutation
export function useUpdateDictionary() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({
      id,
      data,
    }: {
      id: string
      data: DictionaryUpdate
    }) => dictionariesApi.update(id, data),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: dictionaryKeys.detail(data.id) })
      queryClient.invalidateQueries({ queryKey: dictionaryKeys.lists() })
      toast.success('Dictionary updated successfully')
    },
    onError: (error: Error & { response?: { data?: { detail?: string } } }) => {
      const message = error.response?.data?.detail || 'Failed to update dictionary'
      toast.error(message)
    },
  })
}

// Delete dictionary mutation
export function useDeleteDictionary() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: string) => dictionariesApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: dictionaryKeys.lists() })
      toast.success('Dictionary deleted successfully')
    },
    onError: (error: Error & { response?: { data?: { detail?: string } } }) => {
      const message = error.response?.data?.detail || 'Failed to delete dictionary'
      toast.error(message)
    },
  })
}

// Export to Excel mutation
export function useExportDictionaryExcel() {
  return useMutation({
    mutationFn: ({
      id,
      options,
    }: {
      id: string
      options?: {
        version_id?: string
        include_statistics?: boolean
        include_annotations?: boolean
        include_pii_info?: boolean
      }
    }) => dictionariesApi.exportExcel(id, options),
    onSuccess: (blob, variables) => {
      // Create download link
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `dictionary-${variables.id}.xlsx`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
      toast.success('Excel export downloaded successfully')
    },
    onError: (error: Error & { response?: { data?: { detail?: string } } }) => {
      const message = error.response?.data?.detail || 'Failed to export to Excel'
      toast.error(message)
    },
  })
}
