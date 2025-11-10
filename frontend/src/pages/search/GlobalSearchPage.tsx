import { useState, useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { Search, Filter, X } from 'lucide-react'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { EmptyState } from '@/components/common/EmptyState'
import { useDebouncedFieldSearch } from '@/hooks/useSearch'
import { useDictionaries } from '@/hooks/useDictionaries'
import type { Field, FieldSearchParams } from '@/types/api'

export function GlobalSearchPage() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()

  // Search state
  const [searchQuery, setSearchQuery] = useState('')
  const [filters, setFilters] = useState<Omit<FieldSearchParams, 'query' | 'limit' | 'offset'>>({})
  const [pagination, setPagination] = useState({ limit: 20, offset: 0 })
  const [showFilters, setShowFilters] = useState(false)

  // Initialize search query from URL parameter
  useEffect(() => {
    const queryParam = searchParams.get('q')
    if (queryParam) {
      setSearchQuery(queryParam)
    }
  }, [searchParams])

  // Fetch dictionaries for filter dropdown
  const { data: dictionariesData } = useDictionaries(100, 0)

  // Debounced search query
  const { data, isLoading, error } = useDebouncedFieldSearch(searchQuery, filters, pagination)

  const handleSearch = (query: string) => {
    setSearchQuery(query)
    setPagination({ ...pagination, offset: 0 }) // Reset to first page
  }

  const handleFilterChange = (key: keyof typeof filters, value: string | boolean | undefined) => {
    setFilters((prev) => ({
      ...prev,
      [key]: value === 'all' ? undefined : value,
    }))
    setPagination({ ...pagination, offset: 0 }) // Reset to first page
  }

  const clearFilters = () => {
    setFilters({})
    setPagination({ ...pagination, offset: 0 })
  }

  const hasActiveFilters = Object.values(filters).some((v) => v !== undefined)

  const handleFieldClick = (field: Field) => {
    // Navigate to the dictionary detail page with the field selected
    // We need to get the dictionary_id from the field's version
    navigate(`/dictionaries/${field.version_id}?field=${field.id}`)
  }

  const handleNextPage = () => {
    if (data?.meta.has_more) {
      setPagination((prev) => ({ ...prev, offset: prev.offset + prev.limit }))
    }
  }

  const handlePrevPage = () => {
    setPagination((prev) => ({ ...prev, offset: Math.max(0, prev.offset - prev.limit) }))
  }

  const currentPage = Math.floor(pagination.offset / pagination.limit) + 1
  const totalPages = data ? Math.ceil(data.meta.total / pagination.limit) : 0

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-bold tracking-tight">Global Field Search</h1>
        <p className="text-sm sm:text-base text-muted-foreground mt-2">
          Search for fields across all data dictionaries
        </p>
      </div>

      {/* Search Bar */}
      <Card>
        <CardContent className="pt-6">
          <div className="space-y-4">
            <div className="flex flex-col sm:flex-row gap-2">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  type="text"
                  placeholder="Search by field name or path..."
                  value={searchQuery}
                  onChange={(e) => handleSearch(e.target.value)}
                  className="pl-9"
                />
              </div>
              <Button
                variant={showFilters ? 'secondary' : 'outline'}
                onClick={() => setShowFilters(!showFilters)}
                className="w-full sm:w-auto"
              >
                <Filter className="h-4 w-4 mr-2" />
                Filters
                {hasActiveFilters && (
                  <Badge variant="secondary" className="ml-2">
                    {Object.values(filters).filter((v) => v !== undefined).length}
                  </Badge>
                )}
              </Button>
            </div>

            {/* Filters Panel */}
            {showFilters && (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 p-4 bg-muted/50 rounded-lg">
                <div className="space-y-2">
                  <label className="text-sm font-medium">Data Type</label>
                  <Select
                    value={filters.data_type || 'all'}
                    onValueChange={(value) => handleFilterChange('data_type', value)}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="All types" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All types</SelectItem>
                      <SelectItem value="string">String</SelectItem>
                      <SelectItem value="integer">Integer</SelectItem>
                      <SelectItem value="float">Float</SelectItem>
                      <SelectItem value="boolean">Boolean</SelectItem>
                      <SelectItem value="object">Object</SelectItem>
                      <SelectItem value="array">Array</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium">Semantic Type</label>
                  <Select
                    value={filters.semantic_type || 'all'}
                    onValueChange={(value) => handleFilterChange('semantic_type', value)}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="All types" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All types</SelectItem>
                      <SelectItem value="email">Email</SelectItem>
                      <SelectItem value="phone">Phone</SelectItem>
                      <SelectItem value="url">URL</SelectItem>
                      <SelectItem value="date">Date</SelectItem>
                      <SelectItem value="datetime">DateTime</SelectItem>
                      <SelectItem value="uuid">UUID</SelectItem>
                      <SelectItem value="ip_address">IP Address</SelectItem>
                      <SelectItem value="currency">Currency</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium">PII Status</label>
                  <Select
                    value={
                      filters.is_pii === undefined
                        ? 'all'
                        : filters.is_pii
                        ? 'true'
                        : 'false'
                    }
                    onValueChange={(value) =>
                      handleFilterChange(
                        'is_pii',
                        value === 'all' ? undefined : value === 'true'
                      )
                    }
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="All fields" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All fields</SelectItem>
                      <SelectItem value="true">PII only</SelectItem>
                      <SelectItem value="false">Non-PII only</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium">Dictionary</label>
                  <Select
                    value={filters.dictionary_id || 'all'}
                    onValueChange={(value) => handleFilterChange('dictionary_id', value)}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="All dictionaries" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All dictionaries</SelectItem>
                      {dictionariesData?.data.map((dict) => (
                        <SelectItem key={dict.id} value={dict.id}>
                          {dict.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                {hasActiveFilters && (
                  <div className="flex items-end">
                    <Button
                      variant="ghost"
                      onClick={clearFilters}
                      className="w-full"
                    >
                      <X className="h-4 w-4 mr-2" />
                      Clear Filters
                    </Button>
                  </div>
                )}
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Results */}
      <div className="space-y-4">
        {/* Results Header */}
        {data && (
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2">
            <p className="text-sm text-muted-foreground">
              Found {data.meta.total} field{data.meta.total !== 1 ? 's' : ''}
              {searchQuery && ` for "${searchQuery}"`}
            </p>
            {totalPages > 1 && (
              <p className="text-sm text-muted-foreground">
                Page {currentPage} of {totalPages}
              </p>
            )}
          </div>
        )}

        {/* Loading State */}
        {isLoading && (
          <div className="space-y-4">
            {[...Array(5)].map((_, i) => (
              <Card key={i}>
                <CardHeader>
                  <Skeleton className="h-6 w-1/3" />
                  <Skeleton className="h-4 w-1/2 mt-2" />
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <Skeleton className="h-4 w-full" />
                    <Skeleton className="h-4 w-2/3" />
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}

        {/* Error State */}
        {error && (
          <Card>
            <CardContent className="pt-6">
              <div className="text-center text-destructive">
                <p className="font-medium">Error loading search results</p>
                <p className="text-sm mt-1">{error.message}</p>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Empty State */}
        {!isLoading && !error && data && data.data.length === 0 && (
          <EmptyState
            icon={<Search className="h-12 w-12" />}
            title="No fields found"
            description={
              searchQuery || hasActiveFilters
                ? 'Try adjusting your search or filters'
                : 'Enter a search query or select filters to begin'
            }
          />
        )}

        {/* Results List */}
        {!isLoading && !error && data && data.data.length > 0 && (
          <>
            <div className="space-y-3">
              {data.data.map((field) => (
                <Card
                  key={field.id}
                  className="cursor-pointer hover:border-primary transition-colors"
                  onClick={() => handleFieldClick(field)}
                >
                  <CardHeader className="pb-3">
                    <div className="flex flex-col sm:flex-row items-start justify-between gap-3">
                      <div className="space-y-1 flex-1 min-w-0">
                        <CardTitle className="text-base sm:text-lg break-words">{field.field_name}</CardTitle>
                        <CardDescription className="text-xs font-mono break-all">
                          {field.field_path}
                        </CardDescription>
                      </div>
                      <div className="flex gap-2 flex-wrap">
                        <Badge variant="outline">{field.data_type}</Badge>
                        {field.semantic_type && (
                          <Badge variant="secondary">{field.semantic_type}</Badge>
                        )}
                        {field.is_pii && <Badge variant="destructive">PII</Badge>}
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    {/* Statistics */}
                    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 text-sm">
                      <div>
                        <p className="text-muted-foreground">Null %</p>
                        <p className="font-medium">{field.null_percentage?.toFixed(1) ?? '0'}%</p>
                      </div>
                      <div>
                        <p className="text-muted-foreground">Total Count</p>
                        <p className="font-medium">{field.total_count.toLocaleString()}</p>
                      </div>
                      <div>
                        <p className="text-muted-foreground">Distinct</p>
                        <p className="font-medium">{field.distinct_count.toLocaleString()}</p>
                      </div>
                      <div>
                        <p className="text-muted-foreground">Cardinality</p>
                        <p className="font-medium">{field.cardinality_ratio?.toFixed(2) ?? 'N/A'}</p>
                      </div>
                    </div>

                    {/* Sample Values */}
                    {field.sample_values && field.sample_values.length > 0 && (
                      <div>
                        <p className="text-sm text-muted-foreground mb-2">Sample Values:</p>
                        <div className="flex flex-wrap gap-2">
                          {field.sample_values.slice(0, 5).map((value, idx) => (
                            <Badge key={idx} variant="outline" className="font-mono text-xs">
                              {String(value)}
                            </Badge>
                          ))}
                          {field.sample_values.length > 5 && (
                            <Badge variant="outline" className="text-xs">
                              +{field.sample_values.length - 5} more
                            </Badge>
                          )}
                        </div>
                      </div>
                    )}

                    {/* Annotation */}
                    {field.annotations && field.annotations.length > 0 && field.annotations[0].description && (
                      <div className="pt-2 border-t">
                        <p className="text-sm text-muted-foreground line-clamp-2">
                          {field.annotations[0].description}
                        </p>
                      </div>
                    )}
                  </CardContent>
                </Card>
              ))}
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-4">
                <Button
                  variant="outline"
                  onClick={handlePrevPage}
                  disabled={pagination.offset === 0}
                  className="w-full sm:w-auto"
                >
                  <span className="hidden sm:inline">Previous</span>
                  <span className="sm:hidden">Prev</span>
                </Button>
                <div className="text-xs sm:text-sm text-muted-foreground text-center">
                  Showing {pagination.offset + 1} to{' '}
                  {Math.min(pagination.offset + pagination.limit, data.meta.total)} of{' '}
                  {data.meta.total}
                </div>
                <Button
                  variant="outline"
                  onClick={handleNextPage}
                  disabled={!data.meta.has_more}
                  className="w-full sm:w-auto"
                >
                  Next
                </Button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  )
}
