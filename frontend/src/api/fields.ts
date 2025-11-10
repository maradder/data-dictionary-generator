import apiClient from './client'
import type {
  Field,
  FieldSearchParams,
  PaginatedResponse,
} from '@/types/api'

export const fieldsApi = {
  // Search fields across all dictionaries
  search: async (
    params: FieldSearchParams
  ): Promise<PaginatedResponse<Field>> => {
    const response = await apiClient.get('/api/v1/search/fields', { params })
    return response.data
  },

  // Get fields for a specific version
  listByVersion: async (
    dictionaryId: string,
    versionId: string,
    limit = 1000,
    offset = 0
  ): Promise<PaginatedResponse<Field>> => {
    const response = await apiClient.get(
      `/api/v1/versions/${dictionaryId}/versions/${versionId}/fields`,
      {
        params: {
          limit,
          offset,
        },
      }
    )
    return response.data
  },
}
