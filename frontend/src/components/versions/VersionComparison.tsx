import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible'
import { ChevronDown, ChevronRight, Plus, Minus, Edit3, AlertTriangle } from 'lucide-react'
import { useState } from 'react'
import type { VersionComparison as VersionComparisonType, ChangeDetail } from '@/types/api'
import { cn } from '@/lib/utils'
import { InfoModal } from '@/components/common/InfoModal'

interface VersionComparisonProps {
  comparison: VersionComparisonType
}

export function VersionComparison({ comparison }: VersionComparisonProps) {
  const { summary, changes, version_1, version_2 } = comparison

  // Group changes by type
  const addedFields = changes.filter((c) => c.change_type === 'added')
  const removedFields = changes.filter((c) => c.change_type === 'removed')
  const modifiedFields = changes.filter((c) => c.change_type === 'modified')

  return (
    <div className="space-y-6">
      {/* Summary Card */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <CardTitle>Comparison Summary</CardTitle>
            <InfoModal title="Understanding Version Comparison">
              <div className="space-y-4">
                <p>
                  Version comparison helps you track changes between different versions of your
                  data dictionary, identifying schema evolution and potential compatibility issues.
                </p>
                <div className="space-y-3">
                  <div>
                    <h4 className="font-medium mb-1 flex items-center gap-2">
                      <Plus className="h-4 w-4 text-green-600" />
                      Fields Added
                    </h4>
                    <p className="text-sm">
                      New fields introduced in the later version. These are non-breaking changes
                      that expand your data structure.
                    </p>
                  </div>
                  <div>
                    <h4 className="font-medium mb-1 flex items-center gap-2">
                      <Minus className="h-4 w-4 text-red-600" />
                      Fields Removed
                    </h4>
                    <p className="text-sm">
                      Fields that existed in the earlier version but are gone in the later version.
                      These are <strong>breaking changes</strong> that may affect systems using this data.
                    </p>
                  </div>
                  <div>
                    <h4 className="font-medium mb-1 flex items-center gap-2">
                      <Edit3 className="h-4 w-4 text-yellow-600" />
                      Fields Modified
                    </h4>
                    <p className="text-sm">
                      Fields where properties changed, such as data type, semantic type, or nullability.
                      Some modifications may be breaking changes.
                    </p>
                  </div>
                  <div>
                    <h4 className="font-medium mb-1 flex items-center gap-2">
                      <AlertTriangle className="h-4 w-4 text-orange-600" />
                      Breaking Changes
                    </h4>
                    <p className="text-sm">
                      Changes that could break existing integrations or applications:
                    </p>
                    <ul className="list-disc list-inside space-y-1 text-sm mt-1 ml-2">
                      <li>Field removals</li>
                      <li>Data type changes</li>
                      <li>Semantic type changes</li>
                      <li>Nullability changes (nullable → non-nullable)</li>
                    </ul>
                  </div>
                </div>
                <div className="bg-orange-50 dark:bg-orange-950 border border-orange-200 dark:border-orange-800 p-3 rounded-md">
                  <p className="font-medium mb-1 text-orange-900 dark:text-orange-100">Important</p>
                  <p className="text-sm text-orange-800 dark:text-orange-200">
                    Always review breaking changes carefully before deploying schema updates to
                    production environments. Consider backward compatibility and migration strategies.
                  </p>
                </div>
              </div>
            </InfoModal>
          </div>
          <CardDescription>
            Version {version_1.version_number} vs Version {version_2.version_number}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-4">
            <div className="space-y-1">
              <p className="text-sm font-medium text-muted-foreground">Fields Added</p>
              <div className="flex items-center gap-2">
                <Plus className="h-4 w-4 text-green-600" />
                <span className="text-2xl font-bold text-green-600">
                  {summary.fields_added}
                </span>
              </div>
            </div>
            <div className="space-y-1">
              <p className="text-sm font-medium text-muted-foreground">Fields Removed</p>
              <div className="flex items-center gap-2">
                <Minus className="h-4 w-4 text-red-600" />
                <span className="text-2xl font-bold text-red-600">
                  {summary.fields_removed}
                </span>
              </div>
            </div>
            <div className="space-y-1">
              <p className="text-sm font-medium text-muted-foreground">Fields Modified</p>
              <div className="flex items-center gap-2">
                <Edit3 className="h-4 w-4 text-yellow-600" />
                <span className="text-2xl font-bold text-yellow-600">
                  {summary.fields_modified}
                </span>
              </div>
            </div>
            <div className="space-y-1">
              <p className="text-sm font-medium text-muted-foreground">Breaking Changes</p>
              <div className="flex items-center gap-2">
                <AlertTriangle className="h-4 w-4 text-orange-600" />
                <span className="text-2xl font-bold text-orange-600">
                  {summary.breaking_changes}
                </span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Added Fields */}
      {addedFields.length > 0 && (
        <FieldChangeSection
          title="Added Fields"
          description={`${addedFields.length} new field${addedFields.length > 1 ? 's' : ''} added in version ${version_2.version_number}`}
          changes={addedFields}
          icon={<Plus className="h-5 w-5 text-green-600" />}
          badgeVariant="success"
        />
      )}

      {/* Removed Fields */}
      {removedFields.length > 0 && (
        <FieldChangeSection
          title="Removed Fields"
          description={`${removedFields.length} field${removedFields.length > 1 ? 's' : ''} removed in version ${version_2.version_number}`}
          changes={removedFields}
          icon={<Minus className="h-5 w-5 text-red-600" />}
          badgeVariant="destructive"
        />
      )}

      {/* Modified Fields */}
      {modifiedFields.length > 0 && (
        <FieldChangeSection
          title="Modified Fields"
          description={`${modifiedFields.length} field${modifiedFields.length > 1 ? 's' : ''} changed in version ${version_2.version_number}`}
          changes={modifiedFields}
          icon={<Edit3 className="h-5 w-5 text-yellow-600" />}
          badgeVariant="warning"
          showModifications
        />
      )}

      {/* No Changes */}
      {changes.length === 0 && (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <p className="text-lg font-medium text-muted-foreground">
              No differences found
            </p>
            <p className="text-sm text-muted-foreground">
              Versions {version_1.version_number} and {version_2.version_number} are identical
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

interface FieldChangeSectionProps {
  title: string
  description: string
  changes: ChangeDetail[]
  icon: React.ReactNode
  badgeVariant: 'success' | 'destructive' | 'warning'
  showModifications?: boolean
}

function FieldChangeSection({
  title,
  description,
  changes,
  icon,
  badgeVariant,
  showModifications = false,
}: FieldChangeSectionProps) {
  const [isOpen, setIsOpen] = useState(true)

  return (
    <Card>
      <Collapsible open={isOpen} onOpenChange={setIsOpen}>
        <CardHeader>
          <CollapsibleTrigger className="flex w-full items-start justify-between hover:opacity-80">
            <div className="flex items-center gap-2">
              {icon}
              <div className="text-left">
                <CardTitle>{title}</CardTitle>
                <CardDescription>{description}</CardDescription>
              </div>
            </div>
            {isOpen ? (
              <ChevronDown className="h-5 w-5 text-muted-foreground" />
            ) : (
              <ChevronRight className="h-5 w-5 text-muted-foreground" />
            )}
          </CollapsibleTrigger>
        </CardHeader>
        <CollapsibleContent>
          <CardContent>
            <div className="rounded-md border">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Field Path</TableHead>
                    <TableHead>Data Type</TableHead>
                    {showModifications && <TableHead>Changes</TableHead>}
                    <TableHead>Status</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {changes.map((change, index) => (
                    <TableRow
                      key={index}
                      className={cn(
                        'transition-colors',
                        badgeVariant === 'success' && 'bg-green-50 hover:bg-green-100',
                        badgeVariant === 'destructive' && 'bg-red-50 hover:bg-red-100',
                        badgeVariant === 'warning' && 'bg-yellow-50 hover:bg-yellow-100'
                      )}
                    >
                      <TableCell className="font-mono text-sm">
                        {change.field_path}
                      </TableCell>
                      <TableCell>
                        {showModifications ? (
                          <div className="space-y-1">
                            {change.version_1_data && (
                              <div className="text-sm">
                                <span className="text-muted-foreground line-through">
                                  {change.version_1_data.data_type}
                                </span>
                              </div>
                            )}
                            {change.version_2_data && (
                              <div className="text-sm font-medium">
                                {change.version_2_data.data_type}
                              </div>
                            )}
                          </div>
                        ) : (
                          <span className="text-sm">
                            {change.version_2_data?.data_type || change.version_1_data?.data_type}
                          </span>
                        )}
                      </TableCell>
                      {showModifications && (
                        <TableCell>
                          {change.description ? (
                            <span className="text-xs text-muted-foreground">
                              {change.description}
                            </span>
                          ) : (
                            <span className="text-xs text-muted-foreground">-</span>
                          )}
                        </TableCell>
                      )}
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <Badge
                            variant={
                              badgeVariant === 'success'
                                ? 'default'
                                : badgeVariant === 'destructive'
                                  ? 'destructive'
                                  : 'secondary'
                            }
                            className={cn(
                              badgeVariant === 'success' && 'bg-green-600 hover:bg-green-700',
                              badgeVariant === 'warning' && 'bg-yellow-600 hover:bg-yellow-700'
                            )}
                          >
                            {change.change_type}
                          </Badge>
                          {change.is_breaking && (
                            <Badge variant="outline" className="border-orange-600 text-orange-600">
                              Breaking
                            </Badge>
                          )}
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          </CardContent>
        </CollapsibleContent>
      </Collapsible>
    </Card>
  )
}
