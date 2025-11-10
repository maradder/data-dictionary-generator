import { useState } from 'react'
import { Button } from '@/components/ui/button'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Label } from '@/components/ui/label'
import { GitCompare } from 'lucide-react'
import type { Version, VersionListItem } from '@/types/api'

interface VersionSelectorProps {
  versions: (Version | VersionListItem)[]
  onCompare: (version1: number, version2: number) => void
  isLoading?: boolean
}

export function VersionSelector({
  versions,
  onCompare,
  isLoading = false,
}: VersionSelectorProps) {
  const [version1, setVersion1] = useState<string>('')
  const [version2, setVersion2] = useState<string>('')

  // Sort versions by version number descending
  const sortedVersions = [...versions].sort(
    (a, b) => b.version_number - a.version_number
  )

  const handleCompare = () => {
    if (version1 && version2) {
      onCompare(parseInt(version1), parseInt(version2))
    }
  }

  const isValid = version1 && version2 && version1 !== version2

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center gap-2">
          <GitCompare className="h-5 w-5" />
          <CardTitle>Compare Versions</CardTitle>
        </div>
        <CardDescription>
          Select two versions to compare their differences side by side
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid gap-6 md:grid-cols-3">
          {/* Version 1 Selector */}
          <div className="space-y-2">
            <Label htmlFor="version1">Base Version</Label>
            <Select value={version1} onValueChange={setVersion1}>
              <SelectTrigger id="version1">
                <SelectValue placeholder="Select version..." />
              </SelectTrigger>
              <SelectContent>
                {sortedVersions.map((version) => (
                  <SelectItem
                    key={version.id}
                    value={version.version_number.toString()}
                    disabled={version.version_number.toString() === version2}
                  >
                    Version {version.version_number}
                    {'notes' in version && version.notes && ` - ${version.notes.substring(0, 30)}${version.notes.length > 30 ? '...' : ''}`}
                    {'notes_preview' in version && version.notes_preview && ` - ${version.notes_preview.substring(0, 30)}${version.notes_preview.length > 30 ? '...' : ''}`}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <p className="text-xs text-muted-foreground">
              {version1 && `${sortedVersions.find(v => v.version_number.toString() === version1)?.field_count || 0} fields`}
            </p>
          </div>

          {/* Compare Button */}
          <div className="flex items-end">
            <Button
              onClick={handleCompare}
              disabled={!isValid || isLoading}
              className="w-full"
            >
              {isLoading ? 'Comparing...' : 'Compare'}
            </Button>
          </div>

          {/* Version 2 Selector */}
          <div className="space-y-2">
            <Label htmlFor="version2">Compare Version</Label>
            <Select value={version2} onValueChange={setVersion2}>
              <SelectTrigger id="version2">
                <SelectValue placeholder="Select version..." />
              </SelectTrigger>
              <SelectContent>
                {sortedVersions.map((version) => (
                  <SelectItem
                    key={version.id}
                    value={version.version_number.toString()}
                    disabled={version.version_number.toString() === version1}
                  >
                    Version {version.version_number}
                    {'notes' in version && version.notes && ` - ${version.notes.substring(0, 30)}${version.notes.length > 30 ? '...' : ''}`}
                    {'notes_preview' in version && version.notes_preview && ` - ${version.notes_preview.substring(0, 30)}${version.notes_preview.length > 30 ? '...' : ''}`}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <p className="text-xs text-muted-foreground">
              {version2 && `${sortedVersions.find(v => v.version_number.toString() === version2)?.field_count || 0} fields`}
            </p>
          </div>
        </div>

        {/* Validation Messages */}
        {version1 && version2 && version1 === version2 && (
          <div className="mt-4 rounded-md bg-destructive/10 p-3 text-sm text-destructive">
            Please select two different versions to compare
          </div>
        )}
      </CardContent>
    </Card>
  )
}
