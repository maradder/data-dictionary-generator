import apiClient from './client'
import type {
  Version,
  VersionListItem,
  VersionComparison,
  CompareExportOptions,
} from '@/types/api'

export const versionsApi = {
  // List all versions for a dictionary
  list: async (dictionaryId: string): Promise<VersionListItem[]> => {
    const response = await apiClient.get(
      `/api/v1/versions/${dictionaryId}/versions`
    )
    return response.data
  },

  // Get specific version
  get: async (
    dictionaryId: string,
    versionId: string
  ): Promise<Version> => {
    const response = await apiClient.get(
      `/api/v1/versions/${dictionaryId}/versions/${versionId}`
    )
    return response.data
  },

  // Create new version with file upload
  create: async (
    dictionaryId: string,
    file: File,
    notes?: string,
    generateAiDescriptions = true
  ): Promise<Version> => {
    const formData = new FormData()
    formData.append('file', file)
    if (notes) {
      formData.append('notes', notes)
    }
    formData.append('generate_ai_descriptions', String(generateAiDescriptions))

    const response = await apiClient.post(
      `/api/v1/versions/${dictionaryId}/versions`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: 300000, // 5 minutes
      }
    )
    return response.data
  },

  // Compare two versions
  compare: async (
    dictionaryId: string,
    version1: number,
    version2: number
  ): Promise<VersionComparison> => {
    const response = await apiClient.get(
      `/api/v1/versions/${dictionaryId}/versions/compare`,
      {
        params: {
          version_1: version1,
          version_2: version2,
        },
      }
    )
    return response.data
  },

  // Export version comparison to Excel
  exportComparison: async (
    dictionaryId: string,
    options: CompareExportOptions
  ): Promise<Blob> => {
    const response = await apiClient.get(
      `/api/v1/exports/${dictionaryId}/versions/compare/excel`,
      {
        params: options,
        responseType: 'blob',
      }
    )
    return response.data
  },
}
