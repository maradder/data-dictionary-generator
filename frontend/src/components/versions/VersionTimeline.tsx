import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import { formatDistanceToNow, format } from 'date-fns'
import { User, Calendar, Database } from 'lucide-react'
import type { VersionListItem } from '@/types/api'

interface VersionTimelineProps {
  versions: VersionListItem[]
  latestVersionId?: string
  onVersionClick?: (versionId: string) => void
  isLoading?: boolean
}

function getInitials(email: string | null): string {
  if (!email) return '?'
  const parts = email.split('@')[0].split('.')
  if (parts.length >= 2) {
    return (parts[0][0] + parts[1][0]).toUpperCase()
  }
  return email.substring(0, 2).toUpperCase()
}

function VersionTimelineItem({
  version,
  isLatest,
  onClick,
}: {
  version: VersionListItem
  isLatest: boolean
  onClick?: () => void
}) {
  return (
    <div className="relative pl-8 pb-8 group">
      {/* Timeline dot and line */}
      <div className="absolute left-0 top-0 flex flex-col items-center">
        <div
          className={`w-4 h-4 rounded-full border-2 ${
            isLatest
              ? 'bg-primary border-primary'
              : 'bg-background border-muted-foreground'
          }`}
        />
        <div className="w-0.5 h-full bg-border group-last:hidden" />
      </div>

      {/* Version Card */}
      <Card
        className={`cursor-pointer hover:shadow-md transition-shadow ${
          isLatest ? 'border-primary' : ''
        }`}
        onClick={onClick}
      >
        <CardHeader className="pb-3">
          <div className="flex items-start justify-between">
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <CardTitle className="text-lg">
                  Version {version.version_number}
                </CardTitle>
                {isLatest && (
                  <Badge variant="default" className="ml-2">
                    Latest
                  </Badge>
                )}
              </div>
              <CardDescription className="flex items-center gap-2">
                <Calendar className="h-3 w-3" />
                {format(new Date(version.created_at), 'PPP')} (
                {formatDistanceToNow(new Date(version.created_at), {
                  addSuffix: true,
                })}
                )
              </CardDescription>
            </div>

            <Avatar className="h-8 w-8">
              <AvatarFallback className="text-xs">
                {getInitials(version.created_by)}
              </AvatarFallback>
            </Avatar>
          </div>
        </CardHeader>

        <CardContent className="space-y-3">
          {/* Creator Info */}
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <User className="h-3.5 w-3.5" />
            <span>{version.created_by || 'Unknown'}</span>
          </div>

          <Separator />

          {/* Stats Grid */}
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1">
              <div className="flex items-center gap-2 text-xs text-muted-foreground">
                <Database className="h-3.5 w-3.5" />
                <span>Fields</span>
              </div>
              <p className="text-lg font-semibold">{version.field_count}</p>
            </div>

            {/* Additional metadata can be added here */}
          </div>

          {/* Notes Preview */}
          {version.notes_preview && (
            <>
              <Separator />
              <div className="space-y-1">
                <p className="text-xs font-medium text-muted-foreground">
                  Release Notes
                </p>
                <p className="text-sm text-muted-foreground line-clamp-2">
                  {version.notes_preview}
                </p>
              </div>
            </>
          )}

          {/* Actions */}
          <div className="pt-2">
            <Button
              variant="outline"
              size="sm"
              className="w-full"
              onClick={(e) => {
                e.stopPropagation()
                onClick?.()
              }}
            >
              View Details
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export function VersionTimelineSkeleton() {
  return (
    <div className="space-y-4">
      {[...Array(3)].map((_, i) => (
        <div key={i} className="relative pl-8">
          <div className="absolute left-0 top-0 flex flex-col items-center">
            <Skeleton className="w-4 h-4 rounded-full" />
            <div className="w-0.5 h-full bg-border" />
          </div>
          <Card>
            <CardHeader className="pb-3">
              <div className="flex items-start justify-between">
                <div className="space-y-2 flex-1">
                  <Skeleton className="h-6 w-32" />
                  <Skeleton className="h-4 w-48" />
                </div>
                <Skeleton className="h-8 w-8 rounded-full" />
              </div>
            </CardHeader>
            <CardContent className="space-y-3">
              <Skeleton className="h-4 w-full" />
              <Separator />
              <div className="grid grid-cols-2 gap-4">
                <Skeleton className="h-12 w-full" />
                <Skeleton className="h-12 w-full" />
              </div>
            </CardContent>
          </Card>
        </div>
      ))}
    </div>
  )
}

export function VersionTimeline({
  versions,
  latestVersionId,
  onVersionClick,
  isLoading,
}: VersionTimelineProps) {
  if (isLoading) {
    return <VersionTimelineSkeleton />
  }

  if (versions.length === 0) {
    return null
  }

  // Sort versions by version number descending (newest first)
  const sortedVersions = [...versions].sort(
    (a, b) => b.version_number - a.version_number
  )

  return (
    <div className="space-y-0">
      {sortedVersions.map((version) => (
        <VersionTimelineItem
          key={version.id}
          version={version}
          isLatest={version.id === latestVersionId}
          onClick={() => onVersionClick?.(version.id)}
        />
      ))}
    </div>
  )
}
