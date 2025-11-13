import { useState } from 'react'
import {
  useDatabaseStats,
  useDatabaseHealth,
  useTableStats,
  useClearDatabase,
  useDownloadBackup,
  useImportBackup,
} from '@/hooks/useDatabase'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Progress } from '@/components/ui/progress'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { Database, Download, Upload, Trash2, AlertCircle, CheckCircle, HardDrive } from 'lucide-react'
import { formatDistanceToNow } from 'date-fns'

export function DatabaseManagementPage() {
  const { data: stats, isLoading: statsLoading } = useDatabaseStats()
  const { data: health, isLoading: healthLoading } = useDatabaseHealth()
  const { data: tableStats, isLoading: tablesLoading } = useTableStats()
  const clearMutation = useClearDatabase()
  const downloadMutation = useDownloadBackup()
  const importMutation = useImportBackup()

  // Dialog states
  const [clearDialogOpen, setClearDialogOpen] = useState(false)
  const [importDialogOpen, setImportDialogOpen] = useState(false)
  const [confirmText, setConfirmText] = useState('')
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [conflictMode, setConflictMode] = useState<'skip' | 'overwrite' | 'fail'>('skip')

  const handleClearDatabase = () => {
    if (confirmText === 'DELETE_ALL_DATA') {
      clearMutation.mutate(confirmText, {
        onSuccess: () => {
          setClearDialogOpen(false)
          setConfirmText('')
        },
      })
    }
  }

  const handleDownloadBackup = () => {
    downloadMutation.mutate()
  }

  const handleImportBackup = () => {
    if (selectedFile) {
      importMutation.mutate(
        { file: selectedFile, conflictMode },
        {
          onSuccess: () => {
            setImportDialogOpen(false)
            setSelectedFile(null)
            setConflictMode('skip')
          },
        }
      )
    }
  }

  const formatBytes = (bytes?: number) => {
    if (!bytes) return 'N/A'
    const mb = bytes / (1024 * 1024)
    return `${mb.toFixed(2)} MB`
  }

  if (statsLoading || healthLoading) {
    return (
      <div className="space-y-8">
        <div className="space-y-2">
          <Skeleton className="h-9 w-64" />
          <Skeleton className="h-4 w-96" />
        </div>
        <div className="grid gap-6 grid-cols-1 sm:grid-cols-2 lg:grid-cols-4">
          {[...Array(4)].map((_, i) => (
            <Card key={i}>
              <CardHeader>
                <Skeleton className="h-4 w-24" />
                <Skeleton className="h-8 w-32" />
              </CardHeader>
            </Card>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl sm:text-4xl font-bold tracking-tight">Database Management</h1>
          <p className="text-base sm:text-lg text-muted-foreground mt-2">
            Monitor database health and manage backups
          </p>
        </div>
      </div>

      {/* Health Status Alert */}
      {health && (
        <Alert variant={health.status === 'healthy' ? 'default' : 'destructive'}>
          {health.status === 'healthy' ? (
            <CheckCircle className="h-4 w-4" />
          ) : (
            <AlertCircle className="h-4 w-4" />
          )}
          <AlertTitle>
            Database Status: {health.status === 'healthy' ? 'Healthy' : 'Unhealthy'}
          </AlertTitle>
          <AlertDescription>
            {health.status === 'healthy'
              ? `Connection established. Last checked ${formatDistanceToNow(new Date(health.checked_at), { addSuffix: true })}`
              : health.error || 'Database connection failed'}
          </AlertDescription>
        </Alert>
      )}

      {/* Stats Dashboard */}
      <div className="grid gap-6 grid-cols-1 sm:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Database Type</CardTitle>
            <Database className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold capitalize">{stats?.database_type || 'Unknown'}</div>
            <p className="text-xs text-muted-foreground mt-1">
              {stats?.database_path || 'In-memory'}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Database Size</CardTitle>
            <HardDrive className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {stats?.database_size_mb ? `${stats.database_size_mb.toFixed(2)} MB` : 'N/A'}
            </div>
            <p className="text-xs text-muted-foreground mt-1">Total storage used</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Records</CardTitle>
            <Database className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.total_records.toLocaleString() || 0}</div>
            <p className="text-xs text-muted-foreground mt-1">Across all tables</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Last Updated</CardTitle>
            <Database className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {stats?.last_updated
                ? formatDistanceToNow(new Date(stats.last_updated), { addSuffix: true })
                : 'Never'}
            </div>
            <p className="text-xs text-muted-foreground mt-1">Most recent change</p>
          </CardContent>
        </Card>
      </div>

      {/* Table Counts Grid */}
      {stats?.table_counts && (
        <Card>
          <CardHeader>
            <CardTitle>Record Counts by Table</CardTitle>
            <CardDescription>Distribution of records across database tables</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 grid-cols-2 sm:grid-cols-4">
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Dictionaries</span>
                  <Badge variant="secondary">{stats.table_counts.dictionaries}</Badge>
                </div>
                <Progress
                  value={(stats.table_counts.dictionaries / stats.total_records) * 100}
                  className="h-2"
                />
              </div>
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Versions</span>
                  <Badge variant="secondary">{stats.table_counts.versions}</Badge>
                </div>
                <Progress
                  value={(stats.table_counts.versions / stats.total_records) * 100}
                  className="h-2"
                />
              </div>
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Fields</span>
                  <Badge variant="secondary">{stats.table_counts.fields}</Badge>
                </div>
                <Progress
                  value={(stats.table_counts.fields / stats.total_records) * 100}
                  className="h-2"
                />
              </div>
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Annotations</span>
                  <Badge variant="secondary">{stats.table_counts.annotations}</Badge>
                </div>
                <Progress
                  value={(stats.table_counts.annotations / stats.total_records) * 100}
                  className="h-2"
                />
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Action Cards */}
      <div className="grid gap-6 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Download className="h-5 w-5" />
              Download Backup
            </CardTitle>
            <CardDescription>Export a complete database backup file</CardDescription>
          </CardHeader>
          <CardContent>
            <Button
              onClick={handleDownloadBackup}
              disabled={downloadMutation.isPending}
              className="w-full"
            >
              {downloadMutation.isPending ? 'Downloading...' : 'Download Backup'}
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Upload className="h-5 w-5" />
              Import Backup
            </CardTitle>
            <CardDescription>Restore database from XLSX backup file</CardDescription>
          </CardHeader>
          <CardContent>
            <Button onClick={() => setImportDialogOpen(true)} variant="outline" className="w-full">
              Import Backup
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-destructive">
              <Trash2 className="h-5 w-5" />
              Clear Database
            </CardTitle>
            <CardDescription>Permanently delete all data (cannot be undone)</CardDescription>
          </CardHeader>
          <CardContent>
            <Button
              onClick={() => setClearDialogOpen(true)}
              variant="destructive"
              className="w-full"
            >
              Clear Database
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* Table Statistics */}
      {tableStats && tableStats.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Detailed Table Statistics</CardTitle>
            <CardDescription>
              Comprehensive breakdown of database table information
            </CardDescription>
          </CardHeader>
          <CardContent>
            {tablesLoading ? (
              <div className="space-y-2">
                {[...Array(4)].map((_, i) => (
                  <Skeleton key={i} className="h-12 w-full" />
                ))}
              </div>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Table Name</TableHead>
                    <TableHead className="text-right">Row Count</TableHead>
                    <TableHead className="text-right">Size</TableHead>
                    <TableHead className="text-right">Indexes</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {tableStats.map((table) => (
                    <TableRow key={table.name}>
                      <TableCell className="font-medium">{table.name}</TableCell>
                      <TableCell className="text-right">{table.row_count.toLocaleString()}</TableCell>
                      <TableCell className="text-right">{formatBytes(table.size_bytes)}</TableCell>
                      <TableCell className="text-right">{table.indexes ?? 'N/A'}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>
      )}

      {/* Clear Database Dialog */}
      <Dialog open={clearDialogOpen} onOpenChange={setClearDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle className="text-destructive">Clear Database</DialogTitle>
            <DialogDescription>
              This action cannot be undone. This will permanently delete all dictionaries, versions,
              fields, and annotations from the database.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertTitle>Warning</AlertTitle>
              <AlertDescription>
                Type <strong>DELETE_ALL_DATA</strong> to confirm this action
              </AlertDescription>
            </Alert>
            <div className="space-y-2">
              <Label htmlFor="confirm">Confirmation Text</Label>
              <Input
                id="confirm"
                value={confirmText}
                onChange={(e) => setConfirmText(e.target.value)}
                placeholder="DELETE_ALL_DATA"
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setClearDialogOpen(false)}>
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={handleClearDatabase}
              disabled={confirmText !== 'DELETE_ALL_DATA' || clearMutation.isPending}
            >
              {clearMutation.isPending ? 'Clearing...' : 'Clear Database'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Import Backup Dialog */}
      <Dialog open={importDialogOpen} onOpenChange={setImportDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Import Backup</DialogTitle>
            <DialogDescription>
              Upload an XLSX backup file to restore your data dictionaries
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="file">Backup File (XLSX)</Label>
              <Input
                id="file"
                type="file"
                accept=".xlsx,.xls"
                onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="conflict">Conflict Resolution</Label>
              <Select value={conflictMode} onValueChange={(value: any) => setConflictMode(value)}>
                <SelectTrigger id="conflict">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="skip">Skip existing records</SelectItem>
                  <SelectItem value="overwrite">Overwrite existing records</SelectItem>
                  <SelectItem value="fail">Fail on conflicts</SelectItem>
                </SelectContent>
              </Select>
              <p className="text-xs text-muted-foreground">
                How to handle records that already exist in the database
              </p>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setImportDialogOpen(false)}>
              Cancel
            </Button>
            <Button
              onClick={handleImportBackup}
              disabled={!selectedFile || importMutation.isPending}
            >
              {importMutation.isPending ? 'Importing...' : 'Import Backup'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
