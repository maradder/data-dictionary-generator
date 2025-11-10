import { useQuery } from '@tanstack/react-query'
import { fieldsApi } from '@/api'
import type { FieldSearchParams } from '@/types/api'

// Query Keys
export const fieldKeys = {
  all: ['fields'] as const,
  searches: () => [...fieldKeys.all, 'search'] as const,
  search: (params: FieldSearchParams) => [...fieldKeys.searches(), params] as const,
  lists: () => [...fieldKeys.all, 'list'] as const,
  list: (dictionaryId: string, versionId: string, limit?: number, offset?: number) =>
    [...fieldKeys.lists(), dictionaryId, versionId, limit, offset] as const,
}

// Get fields for a specific version
export function useVersionFields(
  dictionaryId: string,
  versionId: string,
  limit = 1000,
  offset = 0
) {
  return useQuery({
    queryKey: fieldKeys.list(dictionaryId, versionId, limit, offset),
    queryFn: () => fieldsApi.listByVersion(dictionaryId, versionId, limit, offset),
    enabled: !!dictionaryId && !!versionId,
  })
}

// Search fields hook
export function useFieldSearch(params: FieldSearchParams) {
  return useQuery({
    queryKey: fieldKeys.search(params),
    queryFn: () => fieldsApi.search(params),
    enabled: !!params.query || !!params.data_type || !!params.semantic_type || params.is_pii !== undefined,
  })
}
