import { apiClient } from './client'

export interface DatabaseStats {
  database_type: 'sqlite' | 'postgresql'
  database_size?: number
  database_size_mb?: number
  database_path?: string
  table_counts: {
    dictionaries: number
    versions: number
    fields: number
    annotations: number
  }
  total_records: number
  last_updated: string | null
}

export interface DatabaseHealth {
  status: 'healthy' | 'unhealthy'
  connection: boolean
  integrity?: boolean
  checked_at: string
  error?: string
}

export interface TableStats {
  name: string
  row_count: number
  size_bytes?: number
  size_mb?: number
  indexes?: number
  last_vacuum?: string
}

export const databaseApi = {
  getStats: async (): Promise<DatabaseStats> => {
    const response = await apiClient.get('/api/v1/database/stats')
    return response.data
  },

  getHealth: async (): Promise<DatabaseHealth> => {
    const response = await apiClient.get('/api/v1/database/health')
    return response.data
  },

  getTableStats: async (): Promise<TableStats[]> => {
    const response = await apiClient.get('/api/v1/database/tables')
    return response.data
  },

  clearDatabase: async (confirm: string) => {
    const response = await apiClient.post(`/api/v1/database/clear?confirm=${confirm}`)
    return response.data
  },

  downloadBackup: async (): Promise<Blob> => {
    const response = await apiClient.get('/api/v1/database/backup/download', {
      responseType: 'blob',
    })
    return response.data
  },

  importBackup: async (file: File, conflictMode: 'skip' | 'overwrite' | 'fail' = 'skip') => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('conflict_mode', conflictMode)

    const response = await apiClient.post('/api/v1/dictionaries/import', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      timeout: 300000, // 5 minutes for large files
    })
    return response.data
  },
}
