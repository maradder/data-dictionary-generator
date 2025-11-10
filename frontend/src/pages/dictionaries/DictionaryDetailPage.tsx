import { useState } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import { useDictionary, useExportDictionaryExcel } from '@/hooks/useDictionaries'
import { useVersions, useVersionComparison } from '@/hooks/useVersions'
import { useVersionFields } from '@/hooks/useFields'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { FieldExplorer } from '@/components/dictionaries/FieldExplorer'
import { FieldDetailPanel } from '@/components/dictionaries/FieldDetailPanel'
import { EmptyState } from '@/components/common/EmptyState'
import {
  VersionSelector,
  VersionComparison,
  VersionTimeline
} from '@/components/versions'
import { formatDistanceToNow } from 'date-fns'
import { Columns3, History } from 'lucide-react'
import type { Field } from '@/types/api'

// Wrapper component for Field Explorer with detail panel
function FieldExplorerWrapper({
  fields,
  dictionaryName,
}: {
  fields: Field[]
  dictionaryName: string
}) {
  const [selectedField, setSelectedField] = useState<Field | null>(null)

  return (
    <>
      <Card>
        <CardHeader>
          <CardTitle>Field Explorer</CardTitle>
          <CardDescription>
            Browse and search through all {fields.length} fields in {dictionaryName}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <FieldExplorer fields={fields} onFieldClick={setSelectedField} />
        </CardContent>
      </Card>

      {/* Field Detail Dialog */}
      <Dialog open={!!selectedField} onOpenChange={() => setSelectedField(null)}>
        <DialogContent className="max-w-3xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Field Details</DialogTitle>
          </DialogHeader>
          {selectedField && <FieldDetailPanel field={selectedField} />}
        </DialogContent>
      </Dialog>
    </>
  )
}

export function DictionaryDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { data: dictionary, isLoading, error } = useDictionary(id!, true)
  const { data: versions } = useVersions(id!)
  const exportMutation = useExportDictionaryExcel()

  // Fetch fields for the latest version
  const latestVersionId = dictionary?.latest_version?.id
  const { data: fieldsData, isLoading: isLoadingFields } = useVersionFields(
    id!,
    latestVersionId!,
    1000,
    0
  )

  // Version comparison state
  const [comparisonVersions, setComparisonVersions] = useState<{
    version1: number
    version2: number
  } | null>(null)

  const { data: comparisonData, isLoading: isComparing } = useVersionComparison(
    id!,
    comparisonVersions?.version1,
    comparisonVersions?.version2
  )

  const handleCompare = (version1: number, version2: number) => {
    setComparisonVersions({ version1, version2 })
  }

  if (isLoading) {
    return (
      <div className="space-y-6">
        {/* Header Skeleton */}
        <div className="flex items-start justify-between">
          <div className="space-y-2">
            <div className="flex items-center gap-3">
              <Skeleton className="h-9 w-20" />
              <Skeleton className="h-9 w-64" />
            </div>
            <Skeleton className="h-4 w-96" />
          </div>
          <div className="flex gap-2">
            <Skeleton className="h-10 w-32" />
            <Skeleton className="h-10 w-32" />
          </div>
        </div>

        {/* Quick Stats Skeleton */}
        <div className="grid gap-4 md:grid-cols-4">
          {[...Array(4)].map((_, i) => (
            <Card key={i}>
              <CardHeader className="pb-3">
                <Skeleton className="h-4 w-24 mb-2" />
                <Skeleton className="h-9 w-16" />
              </CardHeader>
            </Card>
          ))}
        </div>

        {/* Tabs Skeleton */}
        <div className="space-y-4">
          <div className="flex gap-2">
            <Skeleton className="h-10 w-24" />
            <Skeleton className="h-10 w-24" />
            <Skeleton className="h-10 w-24" />
          </div>

          {/* Tab Content Skeleton */}
          <Card>
            <CardHeader>
              <Skeleton className="h-6 w-48" />
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-4 md:grid-cols-2">
                {[...Array(6)].map((_, i) => (
                  <div key={i} className="space-y-2">
                    <Skeleton className="h-4 w-24" />
                    <Skeleton className="h-5 w-full" />
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    )
  }

  if (error || !dictionary) {
    return (
      <div className="flex flex-col items-center justify-center h-64 space-y-4">
        <p className="text-destructive">Failed to load dictionary</p>
        <Link to="/">
          <Button variant="outline">Back to Dictionaries</Button>
        </Link>
      </div>
    )
  }

  const handleExport = () => {
    exportMutation.mutate({
      id: dictionary.id,
      options: {
        include_statistics: true,
        include_annotations: true,
        include_pii_info: true,
      },
    })
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col lg:flex-row items-start lg:items-start justify-between gap-4">
        <div className="space-y-1 flex-1 min-w-0">
          <div className="flex items-center gap-3">
            <Link to="/">
              <Button variant="ghost" size="sm">
                ← Back
              </Button>
            </Link>
            <h1 className="text-2xl sm:text-3xl font-bold tracking-tight break-words">{dictionary.name}</h1>
          </div>
          <p className="text-sm sm:text-base text-muted-foreground">
            {dictionary.description || 'No description provided'}
          </p>
        </div>
        <div className="flex flex-col sm:flex-row gap-2 w-full lg:w-auto">
          <Button
            variant="outline"
            onClick={handleExport}
            disabled={exportMutation.isPending}
            className="w-full sm:w-auto"
          >
            {exportMutation.isPending ? 'Exporting...' : '📥 Export Excel'}
          </Button>
          <Link to={`/dictionaries/${id}/upload-version`} className="w-full sm:w-auto">
            <Button className="w-full sm:w-auto">⬆️ New Version</Button>
          </Link>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid gap-4 grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="pb-3">
            <CardDescription className="text-xs sm:text-sm">Total Fields</CardDescription>
            <CardTitle className="text-2xl sm:text-3xl">{dictionary.field_count || 0}</CardTitle>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader className="pb-3">
            <CardDescription className="text-xs sm:text-sm">Records Analyzed</CardDescription>
            <CardTitle className="text-2xl sm:text-3xl">
              {dictionary.total_records_analyzed?.toLocaleString() || '0'}
            </CardTitle>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader className="pb-3">
            <CardDescription className="text-xs sm:text-sm">Versions</CardDescription>
            <CardTitle className="text-2xl sm:text-3xl">{dictionary.version_count || 0}</CardTitle>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader className="pb-3">
            <CardDescription className="text-xs sm:text-sm">File Size</CardDescription>
            <CardTitle className="text-2xl sm:text-3xl">
              {dictionary.source_file_size
                ? (dictionary.source_file_size / (1024 * 1024)).toFixed(2) + ' MB'
                : 'N/A'}
            </CardTitle>
          </CardHeader>
        </Card>
      </div>

      {/* Tabs */}
      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="overview" className="text-xs sm:text-sm">Overview</TabsTrigger>
          <TabsTrigger value="fields" className="text-xs sm:text-sm">
            <span className="hidden sm:inline">Fields </span>
            <span className="sm:hidden">Fields </span>
            {fieldsData?.meta.total !== undefined ? `(${fieldsData.meta.total})` : `(${dictionary.field_count || 0})`}
          </TabsTrigger>
          <TabsTrigger value="versions" className="text-xs sm:text-sm">
            <span className="hidden sm:inline">Versions </span>
            <span className="sm:hidden">Ver. </span>
            ({dictionary.version_count || 0})
          </TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Dictionary Information</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-4 grid-cols-1 sm:grid-cols-2">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Name</p>
                  <p className="text-base break-words">{dictionary.name}</p>
                </div>
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Source File</p>
                  <p className="text-base break-all">{dictionary.source_file_name}</p>
                </div>
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Created By</p>
                  <p className="text-base">{dictionary.created_by}</p>
                </div>
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Created</p>
                  <p className="text-base">
                    {formatDistanceToNow(new Date(dictionary.created_at), {
                      addSuffix: true,
                    })}
                  </p>
                </div>
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Last Updated</p>
                  <p className="text-base">
                    {formatDistanceToNow(new Date(dictionary.updated_at), {
                      addSuffix: true,
                    })}
                  </p>
                </div>
              </div>

              {dictionary.description && (
                <div>
                  <p className="text-sm font-medium text-muted-foreground mb-2">
                    Description
                  </p>
                  <p className="text-base">{dictionary.description}</p>
                </div>
              )}
            </CardContent>
          </Card>

          {dictionary.latest_version && (
            <Card>
              <CardHeader>
                <CardTitle>Latest Version</CardTitle>
                <CardDescription>
                  Version {dictionary.latest_version.version_number}
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid gap-4 grid-cols-1 sm:grid-cols-2">
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">Version Number</p>
                    <p className="text-base">{dictionary.latest_version.version_number}</p>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">Created</p>
                    <p className="text-base">
                      {formatDistanceToNow(new Date(dictionary.latest_version.created_at), {
                        addSuffix: true,
                      })}
                    </p>
                  </div>
                </div>
                {dictionary.latest_version.notes && (
                  <div>
                    <p className="text-sm font-medium text-muted-foreground mb-2">
                      Release Notes
                    </p>
                    <p className="text-base">{dictionary.latest_version.notes}</p>
                  </div>
                )}
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* Fields Tab */}
        <TabsContent value="fields">
          {isLoadingFields ? (
            <Card>
              <CardHeader>
                <Skeleton className="h-6 w-32" />
                <Skeleton className="h-4 w-64" />
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {[...Array(10)].map((_, i) => (
                    <Skeleton key={i} className="h-12 w-full" />
                  ))}
                </div>
              </CardContent>
            </Card>
          ) : fieldsData?.data && fieldsData.data.length > 0 ? (
            <FieldExplorerWrapper
              fields={fieldsData.data}
              dictionaryName={dictionary.name}
            />
          ) : (
            <EmptyState
              icon={<Columns3 size={64} strokeWidth={1.5} />}
              title="No fields available"
              description="This dictionary doesn't have any fields yet. Upload a version with data to see field information and statistics."
              action={{
                label: 'Upload a version',
                onClick: () => navigate(`/dictionaries/${id}/upload-version`),
              }}
            />
          )}
        </TabsContent>

        {/* Versions Tab */}
        <TabsContent value="versions" className="space-y-4">
          {versions && versions.length > 0 ? (
            <>
              {/* Version Comparison Selector */}
              {versions.length >= 2 && (
                <VersionSelector
                  versions={versions}
                  onCompare={handleCompare}
                  isLoading={isComparing}
                />
              )}

              {/* Comparison Results */}
              {comparisonData && (
                <VersionComparison comparison={comparisonData} />
              )}

              {/* Version Timeline */}
              <div>
                <div className="mb-4">
                  <h3 className="text-lg font-semibold">Version History</h3>
                  <p className="text-sm text-muted-foreground">
                    All versions of this dictionary ordered by creation date
                  </p>
                </div>
                <VersionTimeline
                  versions={versions}
                  latestVersionId={dictionary.latest_version?.id}
                  onVersionClick={(versionId) => {
                    // Handle version click - could navigate to version details page
                    console.log('Version clicked:', versionId)
                  }}
                />
              </div>
            </>
          ) : (
            <EmptyState
              icon={<History size={64} strokeWidth={1.5} />}
              title="No versions yet"
              description="This dictionary doesn't have any versions. Upload a new version to start tracking changes and maintaining history."
              action={{
                label: 'Upload first version',
                onClick: () => navigate(`/dictionaries/${id}/upload-version`),
              }}
            />
          )}
        </TabsContent>
      </Tabs>
    </div>
  )
}
