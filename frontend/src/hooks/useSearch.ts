import { useQuery } from '@tanstack/react-query'
import { useEffect, useState } from 'react'
import { searchApi } from '@/api/search'
import type { FieldSearchParams, Field, PaginatedResponse } from '@/types/api'

const DEBOUNCE_MS = 300

export function useFieldSearch(params: FieldSearchParams) {
  return useQuery<PaginatedResponse<Field>>({
    queryKey: ['search', 'fields', params],
    queryFn: () => searchApi.searchFields(params),
    enabled: Boolean(params.query || params.data_type || params.semantic_type || params.is_pii !== undefined || params.dictionary_id),
    staleTime: 30000, // 30 seconds
  })
}

export function useDebouncedFieldSearch(
  query: string,
  filters: Omit<FieldSearchParams, 'query' | 'limit' | 'offset'>,
  pagination: { limit: number; offset: number }
) {
  const [debouncedQuery, setDebouncedQuery] = useState(query)

  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedQuery(query)
    }, DEBOUNCE_MS)

    return () => clearTimeout(timer)
  }, [query])

  return useFieldSearch({
    query: debouncedQuery || undefined,
    ...filters,
    ...pagination,
  })
}
