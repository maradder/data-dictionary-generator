import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import { Skeleton } from '@/components/ui/skeleton'
import { FieldStatistics } from '@/components/fields/FieldStatistics'
import type { Field } from '@/types/api'

interface FieldDetailPanelProps {
  field?: Field
  onClose?: () => void
  isLoading?: boolean
}

export function FieldDetailPanel({ field, onClose, isLoading = false }: FieldDetailPanelProps) {
  if (isLoading || !field) {
    return (
      <div className="space-y-6">
        {/* Header Skeleton */}
        <div className="flex items-start justify-between">
          <div className="space-y-2">
            <Skeleton className="h-8 w-48" />
            <Skeleton className="h-4 w-64" />
          </div>
        </div>

        {/* Type Information Skeleton */}
        <Card>
          <CardHeader>
            <Skeleton className="h-6 w-40" />
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid gap-4 md:grid-cols-2">
              {[...Array(4)].map((_, i) => (
                <div key={i} className="space-y-2">
                  <Skeleton className="h-4 w-24" />
                  <Skeleton className="h-5 w-20" />
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Quality Metrics Skeleton */}
        <Card>
          <CardHeader>
            <Skeleton className="h-6 w-32" />
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <div className="flex justify-between">
                <Skeleton className="h-4 w-32" />
                <Skeleton className="h-4 w-12" />
              </div>
              <Skeleton className="h-2 w-full" />
            </div>
            <div className="grid gap-4 md:grid-cols-2">
              {[...Array(4)].map((_, i) => (
                <div key={i} className="space-y-2">
                  <Skeleton className="h-4 w-24" />
                  <Skeleton className="h-8 w-20" />
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Sample Values Skeleton */}
        <Card>
          <CardHeader>
            <Skeleton className="h-6 w-32" />
            <Skeleton className="h-4 w-full" />
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {[...Array(5)].map((_, i) => (
                <Skeleton key={i} className="h-10 w-full" />
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  const hasStatistics = field.min_value !== null || field.max_value !== null

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between gap-4">
        <div className="space-y-1 min-w-0 flex-1">
          <h2 className="text-xl sm:text-2xl font-bold break-words">{field.field_name}</h2>
          <p className="text-xs sm:text-sm text-muted-foreground break-all">{field.field_path}</p>
        </div>
        {onClose && (
          <button
            onClick={onClose}
            className="text-muted-foreground hover:text-foreground shrink-0"
          >
            ✕
          </button>
        )}
      </div>

      {/* Type Information */}
      <Card>
        <CardHeader>
          <CardTitle>Type Information</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4 grid-cols-1 sm:grid-cols-2">
            <div>
              <p className="text-sm font-medium text-muted-foreground">Data Type</p>
              <Badge variant="outline" className="mt-1">
                {field.data_type}
              </Badge>
            </div>
            {field.semantic_type && (
              <div>
                <p className="text-sm font-medium text-muted-foreground">
                  Semantic Type
                </p>
                <Badge variant="secondary" className="mt-1">
                  {field.semantic_type}
                </Badge>
              </div>
            )}
            <div>
              <p className="text-sm font-medium text-muted-foreground">Nullable</p>
              <p className="text-base">{field.is_nullable ? 'Yes' : 'No'}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">Array</p>
              <p className="text-base">{field.is_array ? 'Yes' : 'No'}</p>
            </div>
            {field.is_array && field.array_item_type && (
              <div>
                <p className="text-sm font-medium text-muted-foreground">
                  Array Item Type
                </p>
                <Badge variant="outline" className="mt-1">
                  {field.array_item_type}
                </Badge>
              </div>
            )}
            <div>
              <p className="text-sm font-medium text-muted-foreground">
                Nesting Level
              </p>
              <p className="text-base">{field.nesting_level}</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* PII Information */}
      {field.is_pii && (
        <Card className="border-destructive">
          <CardHeader>
            <CardTitle className="text-destructive">
              🔒 Personally Identifiable Information
            </CardTitle>
            <CardDescription>
              This field has been identified as containing PII
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-2">
            {field.pii_type && (
              <div>
                <p className="text-sm font-medium text-muted-foreground">PII Type</p>
                <Badge variant="destructive" className="mt-1">
                  {field.pii_type}
                </Badge>
              </div>
            )}
            {field.confidence_score !== null && (
              <div>
                <p className="text-sm font-medium text-muted-foreground">
                  Confidence Score
                </p>
                <p className="text-base">{field.confidence_score.toFixed(1)}%</p>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Quality Metrics */}
      <Card>
        <CardHeader>
          <CardTitle>Data Quality</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-muted-foreground">Null Percentage</span>
              <span className="font-medium">{field.null_percentage?.toFixed(1) ?? '0'}%</span>
            </div>
            <Progress
              value={field.null_percentage ?? 0}
              className="h-2"
            />
          </div>

          <div className="grid gap-4 grid-cols-2 lg:grid-cols-2">
            <div>
              <p className="text-sm font-medium text-muted-foreground">
                Total Count
              </p>
              <p className="text-xl sm:text-2xl font-bold">{field.total_count.toLocaleString()}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">
                Null Count
              </p>
              <p className="text-xl sm:text-2xl font-bold">{field.null_count.toLocaleString()}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">
                Distinct Values
              </p>
              <p className="text-xl sm:text-2xl font-bold">{field.distinct_count.toLocaleString()}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">
                Cardinality Ratio
              </p>
              <p className="text-xl sm:text-2xl font-bold">{field.cardinality_ratio?.toFixed(4) ?? 'N/A'}</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Statistical Analysis (for numeric fields) */}
      {hasStatistics && (
        <Card>
          <CardHeader>
            <CardTitle>Statistical Analysis</CardTitle>
            <CardDescription>Summary statistics for numeric values</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid gap-4 grid-cols-2 md:grid-cols-2">
              {field.min_value !== null && (
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Minimum</p>
                  <p className="text-xl sm:text-2xl font-bold">{field.min_value.toFixed(2)}</p>
                </div>
              )}
              {field.max_value !== null && (
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Maximum</p>
                  <p className="text-xl sm:text-2xl font-bold">{field.max_value.toFixed(2)}</p>
                </div>
              )}
              {field.mean_value !== null && (
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Mean</p>
                  <p className="text-xl sm:text-2xl font-bold">{field.mean_value.toFixed(2)}</p>
                </div>
              )}
              {field.median_value !== null && (
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Median</p>
                  <p className="text-xl sm:text-2xl font-bold">{field.median_value.toFixed(2)}</p>
                </div>
              )}
              {field.std_dev !== null && (
                <div>
                  <p className="text-sm font-medium text-muted-foreground">
                    Std Deviation
                  </p>
                  <p className="text-xl sm:text-2xl font-bold">{field.std_dev.toFixed(2)}</p>
                </div>
              )}
            </div>

            {field.percentile_25 !== null && (
              <div className="space-y-2">
                <p className="text-sm font-medium text-muted-foreground">Percentiles</p>
                <div className="grid gap-2 grid-cols-3">
                  <div className="border rounded-lg p-3">
                    <p className="text-xs text-muted-foreground">25th</p>
                    <p className="text-base sm:text-lg font-semibold">
                      {field.percentile_25.toFixed(2)}
                    </p>
                  </div>
                  <div className="border rounded-lg p-3">
                    <p className="text-xs text-muted-foreground">50th</p>
                    <p className="text-base sm:text-lg font-semibold">
                      {field.percentile_50?.toFixed(2) || 'N/A'}
                    </p>
                  </div>
                  <div className="border rounded-lg p-3">
                    <p className="text-xs text-muted-foreground">75th</p>
                    <p className="text-base sm:text-lg font-semibold">
                      {field.percentile_75?.toFixed(2) || 'N/A'}
                    </p>
                  </div>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Sample Values */}
      {field.sample_values && field.sample_values.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Sample Values</CardTitle>
            <CardDescription>
              Up to 10 unique sample values from the dataset
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {field.sample_values.map((value, index) => (
                <div
                  key={index}
                  className="border rounded-lg p-2 bg-muted/50 font-mono text-sm"
                >
                  {JSON.stringify(value)}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* AI Description */}
      {field.annotations && field.annotations.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Description</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {field.annotations.map((annotation) => (
              <div key={annotation.id}>
                {annotation.is_ai_generated && (
                  <Badge variant="secondary" className="mb-2">
                    🤖 AI Generated
                  </Badge>
                )}
                {annotation.description && (
                  <p className="text-sm">{annotation.description}</p>
                )}
                {annotation.business_name && (
                  <div className="mt-2">
                    <p className="text-xs text-muted-foreground">Business Name</p>
                    <p className="text-sm font-medium">{annotation.business_name}</p>
                  </div>
                )}
                {annotation.tags && annotation.tags.length > 0 && (
                  <div className="mt-2 flex flex-wrap gap-1">
                    {annotation.tags.map((tag) => (
                      <Badge key={tag} variant="outline" className="text-xs">
                        {tag}
                      </Badge>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {/* Statistics Visualizations */}
      {hasStatistics && <FieldStatistics field={field} />}
    </div>
  )
}
