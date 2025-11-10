import { useState, useMemo } from 'react'
import {
  useReactTable,
  getCoreRowModel,
  getFilteredRowModel,
  getSortedRowModel,
  getPaginationRowModel,
  flexRender,
  type ColumnDef,
  type SortingState,
  type ColumnFiltersState,
} from '@tanstack/react-table'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { EmptyState } from '@/components/common/EmptyState'
import { InfoModal } from '@/components/common/InfoModal'
import { SearchX, Filter } from 'lucide-react'
import type { Field } from '@/types/api'

interface FieldExplorerProps {
  fields: Field[]
  onFieldClick?: (field: Field) => void
  isLoading?: boolean
}

export function FieldExplorer({ fields, onFieldClick, isLoading = false }: FieldExplorerProps) {
  const [sorting, setSorting] = useState<SortingState>([])
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([])
  const [globalFilter, setGlobalFilter] = useState('')

  const columns = useMemo<ColumnDef<Field>[]>(
    () => [
      {
        accessorKey: 'field_name',
        header: 'Field Name',
        cell: ({ row }) => {
          const field = row.original
          return (
            <div className="space-y-1 min-w-[200px]">
              <div className="font-medium">{field.field_name}</div>
              <div className="text-xs text-muted-foreground">{field.field_path}</div>
              {/* Mobile: Show type and PII inline */}
              <div className="flex gap-2 md:hidden mt-2">
                <Badge variant="outline">{field.data_type}</Badge>
                {field.is_pii && <Badge variant="destructive">PII</Badge>}
              </div>
            </div>
          )
        },
      },
      {
        accessorKey: 'data_type',
        header: 'Type',
        cell: ({ row }) => (
          <Badge variant="outline">{row.original.data_type}</Badge>
        ),
        meta: {
          className: 'hidden md:table-cell',
        },
      },
      {
        accessorKey: 'semantic_type',
        header: 'Semantic Type',
        cell: ({ row }) => {
          const semanticType = row.original.semantic_type
          return semanticType ? (
            <Badge variant="secondary">{semanticType}</Badge>
          ) : (
            <span className="text-muted-foreground">-</span>
          )
        },
        meta: {
          className: 'hidden lg:table-cell',
        },
      },
      {
        accessorKey: 'is_pii',
        header: 'PII',
        cell: ({ row }) => {
          const isPii = row.original.is_pii
          return isPii ? (
            <Badge variant="destructive">PII</Badge>
          ) : (
            <Badge variant="outline">No</Badge>
          )
        },
        meta: {
          className: 'hidden md:table-cell',
        },
      },
      {
        accessorKey: 'null_percentage',
        header: 'Null %',
        cell: ({ row }) => {
          const nullPct = row.original.null_percentage ?? 0
          const color =
            nullPct > 50
              ? 'text-destructive'
              : nullPct > 20
              ? 'text-yellow-600'
              : 'text-muted-foreground'
          return <span className={color}>{nullPct.toFixed(1)}%</span>
        },
        meta: {
          className: 'hidden lg:table-cell',
        },
      },
      {
        accessorKey: 'distinct_count',
        header: 'Distinct',
        cell: ({ row }) => row.original.distinct_count.toLocaleString(),
        meta: {
          className: 'hidden lg:table-cell',
        },
      },
      {
        id: 'actions',
        header: '',
        cell: ({ row }) => (
          <Button
            variant="ghost"
            size="sm"
            onClick={() => onFieldClick?.(row.original)}
            className="whitespace-nowrap"
          >
            <span className="hidden sm:inline">Details →</span>
            <span className="sm:hidden">→</span>
          </Button>
        ),
      },
    ],
    [onFieldClick]
  )

  const table = useReactTable({
    data: fields,
    columns,
    state: {
      sorting,
      columnFilters,
      globalFilter,
    },
    onSortingChange: setSorting,
    onColumnFiltersChange: setColumnFilters,
    onGlobalFilterChange: setGlobalFilter,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    initialState: {
      pagination: {
        pageSize: 20,
      },
    },
  })

  const hasFilters = globalFilter || columnFilters.length > 0
  const filteredRowCount = table.getFilteredRowModel().rows.length

  if (isLoading) {
    return (
      <div className="space-y-4">
        {/* Search and Filters Skeleton */}
        <div className="flex items-center gap-2">
          <Skeleton className="h-10 w-full max-w-sm" />
          <div className="flex-1" />
          <Skeleton className="h-4 w-16" />
        </div>

        {/* Table Skeleton */}
        <div className="rounded-md border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead><Skeleton className="h-4 w-24" /></TableHead>
                <TableHead><Skeleton className="h-4 w-16" /></TableHead>
                <TableHead><Skeleton className="h-4 w-28" /></TableHead>
                <TableHead><Skeleton className="h-4 w-12" /></TableHead>
                <TableHead><Skeleton className="h-4 w-16" /></TableHead>
                <TableHead><Skeleton className="h-4 w-20" /></TableHead>
                <TableHead><Skeleton className="h-4 w-12" /></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {[...Array(10)].map((_, i) => (
                <TableRow key={i}>
                  <TableCell>
                    <div className="space-y-1">
                      <Skeleton className="h-4 w-32" />
                      <Skeleton className="h-3 w-48" />
                    </div>
                  </TableCell>
                  <TableCell><Skeleton className="h-5 w-16" /></TableCell>
                  <TableCell><Skeleton className="h-5 w-20" /></TableCell>
                  <TableCell><Skeleton className="h-5 w-12" /></TableCell>
                  <TableCell><Skeleton className="h-4 w-12" /></TableCell>
                  <TableCell><Skeleton className="h-4 w-16" /></TableCell>
                  <TableCell><Skeleton className="h-8 w-20" /></TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>

        {/* Pagination Skeleton */}
        <div className="flex items-center justify-between">
          <Skeleton className="h-4 w-24" />
          <div className="flex items-center gap-2">
            <Skeleton className="h-9 w-20" />
            <Skeleton className="h-9 w-16" />
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* Search and Filters */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center gap-2">
        <Input
          placeholder="Search fields..."
          value={globalFilter}
          onChange={(e) => setGlobalFilter(e.target.value)}
          className="w-full sm:max-w-sm"
        />
        <div className="flex-1" />
        <InfoModal title="Field Explorer Features">
          <div className="space-y-4">
            <p>The Field Explorer provides powerful tools to navigate and understand your data dictionary:</p>

            <div className="space-y-3">
              <div>
                <h4 className="font-medium mb-1">Field Columns</h4>
                <ul className="list-disc list-inside space-y-1 text-sm">
                  <li><strong>Field Name</strong> - The technical name and nested path of the field</li>
                  <li><strong>Type</strong> - Basic data type (string, number, boolean, object, array, etc.)</li>
                  <li><strong>Semantic Type</strong> - Business meaning like email, phone, date, currency</li>
                  <li><strong>PII</strong> - Whether the field contains Personally Identifiable Information</li>
                  <li><strong>Null %</strong> - Percentage of null/missing values (color-coded by severity)</li>
                  <li><strong>Distinct</strong> - Number of unique values in the field</li>
                </ul>
              </div>

              <div>
                <h4 className="font-medium mb-1">Sorting & Filtering</h4>
                <ul className="list-disc list-inside space-y-1 text-sm">
                  <li>Click column headers to sort ascending/descending</li>
                  <li>Use the search box to find fields across all properties</li>
                  <li>Results update instantly as you type</li>
                </ul>
              </div>

              <div>
                <h4 className="font-medium mb-1">Field Details</h4>
                <p className="text-sm">
                  Click the "Details" button on any row to view comprehensive information including
                  statistics, sample values, and field annotations.
                </p>
              </div>

              <div className="bg-muted p-3 rounded-md">
                <p className="font-medium mb-1">Color Coding</p>
                <p className="text-sm">
                  Null percentages are color-coded: red (&gt;50%), yellow (&gt;20%), or default (&lt;20%)
                  to help you quickly identify data quality issues.
                </p>
              </div>
            </div>
          </div>
        </InfoModal>
        <div className="text-sm text-muted-foreground">
          {filteredRowCount} field{filteredRowCount !== 1 ? 's' : ''}
        </div>
      </div>

      {/* Table or Empty State */}
      {filteredRowCount === 0 ? (
        <EmptyState
          icon={hasFilters ? <SearchX size={48} strokeWidth={1.5} /> : <Filter size={48} strokeWidth={1.5} />}
          title={hasFilters ? 'No fields found' : 'No fields available'}
          description={
            hasFilters
              ? 'No fields match your search criteria. Try adjusting your filters or search terms.'
              : 'This dictionary doesn\'t contain any fields matching your filters.'
          }
          action={
            hasFilters
              ? {
                  label: 'Clear filters',
                  onClick: () => {
                    setGlobalFilter('')
                    setColumnFilters([])
                  },
                }
              : undefined
          }
        />
      ) : (
        <>
          {/* Table - Horizontal scroll on mobile */}
          <div className="rounded-md border overflow-x-auto">
            <Table>
              <TableHeader>
                {table.getHeaderGroups().map((headerGroup) => (
                  <TableRow key={headerGroup.id}>
                    {headerGroup.headers.map((header) => {
                      const meta = header.column.columnDef.meta as { className?: string } | undefined
                      return (
                        <TableHead key={header.id} className={meta?.className}>
                          {header.isPlaceholder ? null : (
                            <div
                              className={
                                header.column.getCanSort()
                                  ? 'cursor-pointer select-none'
                                  : ''
                              }
                              onClick={header.column.getToggleSortingHandler()}
                            >
                              {flexRender(
                                header.column.columnDef.header,
                                header.getContext()
                              )}
                              {{
                                asc: ' ↑',
                                desc: ' ↓',
                              }[header.column.getIsSorted() as string] ?? null}
                            </div>
                          )}
                        </TableHead>
                      )
                    })}
                  </TableRow>
                ))}
              </TableHeader>
              <TableBody>
                {table.getRowModel().rows.map((row) => (
                  <TableRow
                    key={row.id}
                    data-state={row.getIsSelected() && 'selected'}
                  >
                    {row.getVisibleCells().map((cell) => {
                      const meta = cell.column.columnDef.meta as { className?: string } | undefined
                      return (
                        <TableCell key={cell.id} className={meta?.className}>
                          {flexRender(
                            cell.column.columnDef.cell,
                            cell.getContext()
                          )}
                        </TableCell>
                      )
                    })}
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>

          {/* Pagination */}
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
            <div className="text-sm text-muted-foreground">
              Page {table.getState().pagination.pageIndex + 1} of{' '}
              {table.getPageCount()}
            </div>
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => table.previousPage()}
                disabled={!table.getCanPreviousPage()}
              >
                <span className="hidden sm:inline">Previous</span>
                <span className="sm:hidden">Prev</span>
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => table.nextPage()}
                disabled={!table.getCanNextPage()}
              >
                Next
              </Button>
            </div>
          </div>
        </>
      )}
    </div>
  )
}
