import apiClient from './client'
import type {
  Dictionary,
  DictionaryListItem,
  DictionaryUpdate,
  PaginatedResponse,
  ExportOptions,
} from '@/types/api'

export const dictionariesApi = {
  // List all dictionaries with pagination
  list: async (params?: {
    limit?: number
    offset?: number
  }): Promise<PaginatedResponse<DictionaryListItem>> => {
    const response = await apiClient.get('/api/v1/dictionaries/', { params })
    return response.data
  },

  // Get single dictionary by ID
  get: async (
    id: string,
    includeVersions = false
  ): Promise<Dictionary> => {
    const response = await apiClient.get(`/api/v1/dictionaries/${id}`, {
      params: { include_versions: includeVersions },
    })
    return response.data
  },

  // Create new dictionary with file upload
  create: async (
    file: File,
    name: string,
    description?: string,
    generateAiDescriptions = true
  ): Promise<Dictionary> => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('name', name)
    if (description) {
      formData.append('description', description)
    }
    formData.append('generate_ai_descriptions', String(generateAiDescriptions))

    const response = await apiClient.post(
      '/api/v1/dictionaries/',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: 300000, // 5 minutes for large files
      }
    )
    return response.data
  },

  // Update dictionary metadata
  update: async (
    id: string,
    data: DictionaryUpdate
  ): Promise<Dictionary> => {
    const response = await apiClient.put(
      `/api/v1/dictionaries/${id}`,
      data
    )
    return response.data
  },

  // Delete dictionary
  delete: async (id: string): Promise<void> => {
    await apiClient.delete(`/api/v1/dictionaries/${id}`)
  },

  // Export dictionary to Excel
  exportExcel: async (
    id: string,
    options?: ExportOptions
  ): Promise<Blob> => {
    const response = await apiClient.get(
      `/api/v1/exports/${id}/excel`,
      {
        params: options,
        responseType: 'blob',
      }
    )
    return response.data
  },

  // Export dictionary to JSON
  exportJson: async (
    id: string,
    options?: ExportOptions
  ): Promise<Record<string, unknown>> => {
    const response = await apiClient.get(
      `/api/v1/exports/${id}/json`,
      {
        params: options,
      }
    )
    return response.data
  },

  // Batch export multiple dictionaries to Excel
  batchExportExcel: async (
    dictionaryIds: string[],
    options?: Omit<ExportOptions, 'version_id'>
  ): Promise<Blob> => {
    const response = await apiClient.post(
      '/api/v1/exports/batch/excel',
      {
        dictionary_ids: dictionaryIds,
        include_statistics: options?.include_statistics ?? true,
        include_annotations: options?.include_annotations ?? true,
        include_pii_info: options?.include_pii_info ?? true,
      },
      {
        responseType: 'blob',
      }
    )
    return response.data
  },
}
