import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useDropzone } from 'react-dropzone'
import { useForm } from 'react-hook-form'
import { useCreateDictionary } from '@/hooks/useDictionaries'
import { useUploadProgress } from '@/hooks/useUploadProgress'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { UploadProgress } from '@/components/upload/UploadProgress'
import { InfoModal } from '@/components/common/InfoModal'

interface UploadFormData {
  name: string
  description: string
  generateAiDescriptions: boolean
}

export function DictionaryUploadPage() {
  const navigate = useNavigate()
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [isUploading, setIsUploading] = useState(false)
  const [uploadedDictionaryId, setUploadedDictionaryId] = useState<string | null>(null)
  const createMutation = useCreateDictionary()

  const { register, handleSubmit, formState: { errors } } = useForm<UploadFormData>({
    defaultValues: {
      generateAiDescriptions: true,
    },
  })

  // Upload progress hook
  const uploadProgress = useUploadProgress({
    fileSize: selectedFile?.size || 0,
    isUploading,
    onComplete: () => {
      // Redirect to dictionary detail page after success message is shown
      if (uploadedDictionaryId) {
        navigate(`/dictionaries/${uploadedDictionaryId}`)
      }
    },
  })

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: {
      'application/json': ['.json', '.jsonl', '.ndjson'],
    },
    maxFiles: 1,
    maxSize: 500 * 1024 * 1024, // 500MB
    onDrop: (acceptedFiles) => {
      if (acceptedFiles.length > 0) {
        setSelectedFile(acceptedFiles[0])
      }
    },
  })

  const onSubmit = async (data: UploadFormData) => {
    if (!selectedFile) {
      return
    }

    try {
      // Start upload progress simulation
      setIsUploading(true)

      const result = await createMutation.mutateAsync({
        file: selectedFile,
        name: data.name,
        description: data.description || undefined,
        generateAiDescriptions: data.generateAiDescriptions,
      })

      // Store the dictionary ID for navigation after progress completes
      setUploadedDictionaryId(result.id)

      // Mark upload as complete
      uploadProgress.complete()
    } catch (error: unknown) {
      // Set error state in progress
      const err = error as Error & { response?: { data?: { detail?: string } } }
      const errorMessage = err.response?.data?.detail || 'Failed to create dictionary. Please try again.'
      uploadProgress.setError(errorMessage)
      console.error('Upload failed:', error)
    }
  }

  const handleCancel = () => {
    // Reset states
    setIsUploading(false)
    setUploadedDictionaryId(null)
    uploadProgress.reset()
  }

  const removeFile = () => {
    setSelectedFile(null)
  }

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
  }

  return (
    <div className="max-w-3xl mx-auto space-y-6 px-4 sm:px-0">
      {/* Header */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-bold tracking-tight">Upload Dictionary</h1>
        <p className="text-sm sm:text-base text-muted-foreground">
          Upload a JSON file to create a new data dictionary
        </p>
      </div>

      {/* Show progress when uploading, otherwise show form */}
      {isUploading ? (
        <UploadProgress
          status={uploadProgress.status}
          progress={uploadProgress.progress}
          fileName={selectedFile?.name}
          error={uploadProgress.error || undefined}
          estimatedTimeRemaining={uploadProgress.estimatedTimeRemaining}
          onCancel={uploadProgress.status === 'uploading' ? handleCancel : undefined}
        />
      ) : (
        /* Upload Form */
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          {/* File Upload */}
          <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              Select JSON File
              <InfoModal title="File Format Requirements">
                <div className="space-y-4">
                  <p>
                    Upload your data dictionary in any of the supported JSON formats:
                  </p>
                  <ul className="list-disc list-inside space-y-2">
                    <li>
                      <strong>.json</strong> - Standard JSON format with a single object or array
                    </li>
                    <li>
                      <strong>.jsonl</strong> - JSON Lines format with one JSON object per line
                    </li>
                    <li>
                      <strong>.ndjson</strong> - Newline Delimited JSON, same as JSON Lines
                    </li>
                    <li>
                      <strong>MongoDB Extended JSON</strong> - Automatically detected (supports $oid, $date, $numberLong, $numberDecimal, $binary)
                    </li>
                  </ul>
                  <div className="bg-muted p-3 rounded-md">
                    <p className="font-medium mb-1">File Size Limit</p>
                    <p className="text-sm">Maximum file size: 500MB</p>
                  </div>
                  <p className="text-sm">
                    Your file should contain field definitions with properties like field names,
                    data types, descriptions, and any metadata about your data structure.
                  </p>
                </div>
              </InfoModal>
            </CardTitle>
            <CardDescription>
              Supported formats: .json, .jsonl, .ndjson (max 500MB)
            </CardDescription>
          </CardHeader>
          <CardContent>
            {!selectedFile ? (
              <div
                {...getRootProps()}
                className={`
                  border-2 border-dashed rounded-lg p-8 sm:p-12 text-center cursor-pointer
                  transition-colors
                  ${isDragActive
                    ? 'border-primary bg-primary/5'
                    : 'border-muted-foreground/25 hover:border-primary/50 hover:bg-accent/50'
                  }
                `}
              >
                <input {...getInputProps()} />
                <div className="space-y-4">
                  <div className="text-5xl sm:text-6xl">📄</div>
                  {isDragActive ? (
                    <p className="text-base sm:text-lg font-medium">Drop the file here...</p>
                  ) : (
                    <>
                      <p className="text-base sm:text-lg font-medium">
                        Drag and drop your JSON file here
                      </p>
                      <p className="text-xs sm:text-sm text-muted-foreground">
                        or click to browse your files
                      </p>
                    </>
                  )}
                  <div className="flex justify-center gap-2 flex-wrap">
                    <Badge variant="secondary">.json</Badge>
                    <Badge variant="secondary">.jsonl</Badge>
                    <Badge variant="secondary">.ndjson</Badge>
                  </div>
                </div>
              </div>
            ) : (
              <div className="border rounded-lg p-4 sm:p-6 bg-accent/50">
                <div className="flex items-start justify-between gap-2">
                  <div className="flex items-start gap-3 sm:gap-4 min-w-0 flex-1">
                    <div className="text-3xl sm:text-4xl shrink-0">📄</div>
                    <div className="min-w-0 flex-1">
                      <p className="font-medium break-all">{selectedFile.name}</p>
                      <p className="text-xs sm:text-sm text-muted-foreground">
                        {formatFileSize(selectedFile.size)}
                      </p>
                    </div>
                  </div>
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    onClick={removeFile}
                    className="shrink-0"
                  >
                    Remove
                  </Button>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Dictionary Details */}
        <Card>
          <CardHeader>
            <CardTitle>Dictionary Details</CardTitle>
            <CardDescription>
              Provide information about your data dictionary
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="name">
                Name <span className="text-destructive">*</span>
              </Label>
              <Input
                id="name"
                placeholder="e.g., User Events Data"
                {...register('name', { required: 'Name is required' })}
              />
              {errors.name && (
                <p className="text-sm text-destructive">{errors.name.message}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="description">Description (optional)</Label>
              <textarea
                id="description"
                placeholder="Describe what this data represents..."
                className="flex min-h-[100px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                {...register('description')}
              />
            </div>

            <div className="flex items-start space-x-2">
              <input
                type="checkbox"
                id="generateAiDescriptions"
                className="h-4 w-4 rounded border-input mt-0.5"
                {...register('generateAiDescriptions')}
              />
              <div className="flex items-center gap-2 flex-1">
                <Label htmlFor="generateAiDescriptions" className="font-normal cursor-pointer">
                  Generate AI-powered field descriptions
                </Label>
                <InfoModal title="AI-Powered Descriptions">
                  <div className="space-y-4">
                    <p>
                      When enabled, the system uses artificial intelligence to automatically
                      generate human-readable descriptions for each field in your data dictionary.
                    </p>
                    <div className="bg-muted p-3 rounded-md">
                      <p className="font-medium mb-1">How it works</p>
                      <p className="text-sm">
                        AI analyzes field names, data types, semantic types, and other metadata
                        to create meaningful descriptions that help your team understand the data.
                      </p>
                    </div>
                    <div className="space-y-2">
                      <p className="font-medium">Benefits:</p>
                      <ul className="list-disc list-inside space-y-1 text-sm">
                        <li>Save time on manual documentation</li>
                        <li>Consistent description format across all fields</li>
                        <li>Especially useful for large dictionaries with many technical field names</li>
                        <li>Makes data more accessible to non-technical stakeholders</li>
                      </ul>
                    </div>
                    <p className="text-sm text-muted-foreground">
                      Note: You can always edit generated descriptions later if needed.
                    </p>
                  </div>
                </InfoModal>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Actions */}
        <div className="flex flex-col sm:flex-row gap-4">
          <Button
            type="submit"
            disabled={!selectedFile}
            className="flex-1"
          >
            Create Dictionary
          </Button>
          <Button
            type="button"
            variant="outline"
            onClick={() => navigate('/')}
            className="sm:w-auto"
          >
            Cancel
          </Button>
        </div>
      </form>
      )}
    </div>
  )
}
