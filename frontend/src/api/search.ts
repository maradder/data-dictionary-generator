import apiClient from './client'
import type {
  Dictionary,
  DictionarySearchParams,
  Field,
  FieldSearchParams,
  PaginatedResponse,
} from '@/types/api'

export const searchApi = {
  // Search dictionaries by name
  searchDictionaries: async (
    params: DictionarySearchParams
  ): Promise<PaginatedResponse<Dictionary>> => {
    const response = await apiClient.get('/api/v1/search/dictionaries', {
      params,
    })
    return response.data
  },

  // Search fields across all dictionaries
  searchFields: async (
    params: FieldSearchParams
  ): Promise<PaginatedResponse<Field>> => {
    const response = await apiClient.get('/api/v1/search/fields', {
      params,
    })
    return response.data
  },
}
