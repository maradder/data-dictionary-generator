// Core API Types matching backend Pydantic schemas

export interface Dictionary {
  id: string
  name: string
  description: string | null
  source_file_name: string
  source_file_size: number | null
  total_records_analyzed: number | null
  created_at: string
  created_by: string
  updated_at: string
  custom_metadata: Record<string, unknown> | null
  version_count?: number
  field_count?: number
  latest_version?: Version
  versions?: Version[]
}

// Simplified dictionary for list views (from backend DictionaryListItem)
export interface DictionaryListItem {
  id: string
  name: string
  description: string | null
  created_at: string
  created_by: string
  version_count: number
  latest_version_number: number
  field_count: number
}

export interface DictionaryCreate {
  name: string
  description?: string
  generate_ai_descriptions?: boolean
}

export interface DictionaryUpdate {
  name?: string
  description?: string
  metadata?: Record<string, unknown>
}

export interface Version {
  id: string
  dictionary_id: string
  version_number: number
  field_count: number
  created_at: string
  created_by: string | null
  notes: string | null
  source_file_name?: string | null
  source_file_size?: number | null
  total_records_analyzed?: number | null
  metadata?: Record<string, unknown> | null
  // Extended fields when fetched with relationships
  schema_hash?: string
  processing_stats?: Record<string, unknown> | null
  dictionary?: Dictionary
  fields?: Field[]
}

export interface VersionListItem {
  id: string
  version_number: number
  field_count: number
  created_at: string
  created_by: string | null
  notes_preview: string | null
}

export interface VersionCreate {
  notes?: string
  generate_ai_descriptions?: boolean
}

export interface Field {
  id: string
  version_id: string
  field_path: string
  field_name: string
  parent_path: string | null
  nesting_level: number
  position: number
  data_type: string
  semantic_type: string | null
  is_nullable: boolean
  is_array: boolean
  array_item_type: string | null
  sample_values: unknown[] | null
  null_count: number
  null_percentage: number | null
  total_count: number
  distinct_count: number
  cardinality_ratio: number | null
  min_value: number | null
  max_value: number | null
  mean_value: number | null
  median_value: number | null
  std_dev: number | null
  percentile_25: number | null
  percentile_50: number | null
  percentile_75: number | null
  is_pii: boolean
  pii_type: string | null
  confidence_score: number | null
  version?: Version
  annotations?: Annotation[]
}

export interface Annotation {
  id: string
  field_id: string
  description: string | null
  business_name: string | null
  is_ai_generated: boolean
  ai_model_version: string | null
  tags: string[] | null
  business_owner: string | null
  created_at: string
  created_by: string
  updated_at: string
  updated_by: string
  field?: Field
}

export interface AnnotationCreate {
  description?: string
  business_name?: string
  tags?: string[]
  business_owner?: string
}

export interface AnnotationUpdate {
  description?: string
  business_name?: string
  tags?: string[]
  business_owner?: string
}

export interface VersionInfo {
  id: string
  version_number: number
  created_at: string
}

export interface FieldChangeData {
  data_type?: string | null
  semantic_type?: string | null
  is_nullable?: boolean | null
  is_array?: boolean | null
  array_item_type?: string | null
  is_pii?: boolean | null
  pii_type?: string | null
}

export interface ChangeDetail {
  change_type: 'added' | 'removed' | 'modified'
  field_path: string
  version_1_data?: FieldChangeData | null
  version_2_data?: FieldChangeData | null
  is_breaking: boolean
  description?: string | null
}

export interface ChangeSummary {
  fields_added: number
  fields_removed: number
  fields_modified: number
  breaking_changes: number
}

export interface VersionComparison {
  dictionary_id: string
  version_1: VersionInfo
  version_2: VersionInfo
  summary: ChangeSummary
  changes: ChangeDetail[]
}

// Legacy interfaces for compatibility
export interface VersionComparisonSummary {
  version_1: number
  version_2: number
  fields_added: number
  fields_removed: number
  fields_modified: number
  breaking_changes: number
}

export interface FieldChange {
  field_path: string
  change_type: 'added' | 'removed' | 'modified'
  is_breaking: boolean
  old_value?: Field
  new_value?: Field
  modifications?: FieldModification[]
}

export interface FieldModification {
  property: string
  old_value: unknown
  new_value: unknown
  is_breaking: boolean
}

export interface FieldSearchParams {
  query?: string
  data_type?: string
  semantic_type?: string
  is_pii?: boolean
  dictionary_id?: string
  limit?: number
  offset?: number
}

export interface DictionarySearchParams {
  query: string
  limit?: number
  offset?: number
}

export interface PaginationMeta {
  total: number
  limit: number
  offset: number
  has_more: boolean
}

export interface PaginatedResponse<T> {
  data: T[]
  meta: PaginationMeta
}

export interface ExportOptions {
  version_id?: string
  include_statistics?: boolean
  include_annotations?: boolean
  include_pii_info?: boolean
}

export interface CompareExportOptions {
  version_1: number
  version_2: number
}

export interface HealthCheck {
  status: string
  app_name: string
  version: string
  environment: string
}

export interface APIError {
  detail: string | { loc: string[]; msg: string; type: string }[]
}
