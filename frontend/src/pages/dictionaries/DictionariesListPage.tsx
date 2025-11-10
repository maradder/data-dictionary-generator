import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useDictionaries, useDeleteDictionary } from '@/hooks/useDictionaries'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { EmptyState } from '@/components/common/EmptyState'
import { formatDistanceToNow } from 'date-fns'
import { Database } from 'lucide-react'
import type { DictionaryListItem } from '@/types/api'

export function DictionariesListPage() {
  const navigate = useNavigate()
  const [page, setPage] = useState(0)
  const limit = 12
  const { data, isLoading, error } = useDictionaries(limit, page * limit)
  const deleteMutation = useDeleteDictionary()

  if (isLoading) {
    return (
      <div className="space-y-8">
        {/* Header Skeleton */}
        <div className="flex items-center justify-between">
          <div className="space-y-2">
            <Skeleton className="h-9 w-64" />
            <Skeleton className="h-4 w-96" />
          </div>
          <Skeleton className="h-10 w-32" />
        </div>

        {/* Grid of card skeletons */}
        <div className="grid gap-6 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-3">
          {[...Array(6)].map((_, i) => (
            <Card key={i}>
              <CardHeader>
                <div className="flex items-start justify-between">
                  <Skeleton className="h-7 w-40" />
                  <Skeleton className="h-5 w-8" />
                </div>
                <Skeleton className="h-4 w-full mt-2" />
                <Skeleton className="h-4 w-3/4" />
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <Skeleton className="h-4 w-16" />
                    <Skeleton className="h-4 w-12" />
                  </div>
                  <div className="flex justify-between">
                    <Skeleton className="h-4 w-20" />
                    <Skeleton className="h-4 w-16" />
                  </div>
                  <div className="flex justify-between">
                    <Skeleton className="h-4 w-16" />
                    <Skeleton className="h-4 w-24" />
                  </div>
                </div>
                <div className="flex gap-2">
                  <Skeleton className="h-9 flex-1" />
                  <Skeleton className="h-9 w-9" />
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Pagination Skeleton */}
        <div className="flex items-center justify-between">
          <Skeleton className="h-10 w-24" />
          <Skeleton className="h-5 w-16" />
          <Skeleton className="h-10 w-24" />
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-destructive">Failed to load dictionaries</p>
      </div>
    )
  }

  const dictionaries = data?.data || []
  const hasNext = data?.meta.has_more || false
  const hasPrev = (data?.meta.offset || 0) > 0

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl sm:text-4xl font-bold tracking-tight">Data Dictionaries</h1>
          <p className="text-base sm:text-lg text-muted-foreground mt-2">
            Manage and explore your data dictionaries
          </p>
        </div>
        <Link to="/upload" className="w-full sm:w-auto">
          <Button className="w-full sm:w-auto">
            <span className="mr-2">⬆️</span>
            Upload New
          </Button>
        </Link>
      </div>

      {/* Dictionary Grid */}
      {dictionaries.length === 0 ? (
        <EmptyState
          icon={<Database size={64} strokeWidth={1.5} />}
          title="No data dictionaries yet"
          description="Get started by uploading your first data dictionary. Upload a JSON file to automatically generate comprehensive field documentation."
          action={{
            label: 'Upload your first dictionary',
            onClick: () => navigate('/upload'),
          }}
        />
      ) : (
        <>
          <div className="grid gap-6 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-3">
            {dictionaries.map((dict: DictionaryListItem) => (
              <Card key={dict.id} className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <div className="flex items-start justify-between gap-2">
                    <CardTitle className="text-lg sm:text-xl break-words">{dict.name}</CardTitle>
                    {dict.version_count && (
                      <Badge variant="secondary" className="shrink-0">
                        v{dict.version_count}
                      </Badge>
                    )}
                  </div>
                  <CardDescription className="line-clamp-2 text-sm">
                    {dict.description || 'No description'}
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Fields:</span>
                      <span className="font-medium">{dict.field_count || 0}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Versions:</span>
                      <span className="font-medium">{dict.version_count || 0}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Created:</span>
                      <span className="font-medium text-xs sm:text-sm">
                        {formatDistanceToNow(new Date(dict.created_at), {
                          addSuffix: true,
                        })}
                      </span>
                    </div>
                  </div>

                  <div className="flex gap-2">
                    <Link to={`/dictionaries/${dict.id}`} className="flex-1">
                      <Button variant="default" className="w-full" size="sm">
                        View Details
                      </Button>
                    </Link>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => {
                        if (confirm('Are you sure you want to delete this dictionary?')) {
                          deleteMutation.mutate(dict.id)
                        }
                      }}
                      disabled={deleteMutation.isPending}
                      className="shrink-0"
                    >
                      🗑️
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Pagination */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-2">
            <Button
              variant="outline"
              onClick={() => setPage(p => p - 1)}
              disabled={!hasPrev}
              className="w-full sm:w-auto min-w-[120px]"
            >
              <span className="hidden sm:inline">Previous</span>
              <span className="sm:hidden">Prev</span>
            </Button>
            <p className="text-sm font-medium text-muted-foreground min-w-[80px] text-center">
              Page {page + 1}
            </p>
            <Button
              variant="outline"
              onClick={() => setPage(p => p + 1)}
              disabled={!hasNext}
              className="w-full sm:w-auto min-w-[120px]"
            >
              Next
            </Button>
          </div>
        </>
      )}
    </div>
  )
}
