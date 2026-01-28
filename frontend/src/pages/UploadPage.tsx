import { useCallback, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useDropzone } from 'react-dropzone'
import { Upload, File, X, ArrowRight, AlertCircle } from 'lucide-react'
import toast from 'react-hot-toast'
import { Card, CardHeader, CardBody, CardFooter } from '../components/ui/Card'
import Button from '../components/ui/Button'
import { useAppStore } from '../store/appStore'
import { uploadFiles } from '../lib/api'
import { cn, formatFileSize, isValidFileType } from '../lib/utils'

const MAX_FILE_SIZE = 50 * 1024 * 1024 // 50MB

export default function UploadPage() {
  const navigate = useNavigate()
  const { sessionId, setDocuments, setCurrentStep } = useAppStore()
  
  const [files, setFiles] = useState<File[]>([])
  const [uploading, setUploading] = useState(false)
  const [errors, setErrors] = useState<string[]>([])

  const onDrop = useCallback((acceptedFiles: File[], rejectedFiles: unknown[]) => {
    const newErrors: string[] = []
    
    const validFiles = acceptedFiles.filter(file => {
      if (!isValidFileType(file.name)) {
        newErrors.push(`${file.name}: Invalid file type`)
        return false
      }
      if (file.size > MAX_FILE_SIZE) {
        newErrors.push(`${file.name}: File too large (max 50MB)`)
        return false
      }
      return true
    })
    
    setErrors(newErrors)
    setFiles(prev => [...prev, ...validFiles])
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/vnd.openxmlformats-officedocument.presentationml.presentation': ['.pptx'],
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'image/png': ['.png'],
      'image/jpeg': ['.jpg', '.jpeg'],
    },
    maxSize: MAX_FILE_SIZE,
  })

  const removeFile = (index: number) => {
    setFiles(prev => prev.filter((_, i) => i !== index))
  }

  const handleUpload = async () => {
    if (!sessionId || files.length === 0) return

    setUploading(true)

    try {
      const result = await uploadFiles(sessionId, files)
      setDocuments(result.documents)
      setCurrentStep(2)
      toast.success(`Uploaded ${result.total} files`)
      navigate('/processing')
    } catch (err) {
      toast.error('Failed to upload files')
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="max-w-2xl mx-auto">
      <Card>
        <CardHeader>
          <div className="flex items-center gap-3">
            <div className="p-2 bg-primary-100 rounded-lg">
              <Upload className="h-6 w-6 text-primary-600" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-gray-900">
                Upload Documents
              </h2>
              <p className="text-sm text-gray-500">
                Upload your lecture materials for processing
              </p>
            </div>
          </div>
        </CardHeader>

        <CardBody className="space-y-4">
          {/* Dropzone */}
          <div
            {...getRootProps()}
            className={cn(
              'border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors',
              isDragActive 
                ? 'border-primary-500 bg-primary-50' 
                : 'border-gray-300 hover:border-primary-400 hover:bg-gray-50'
            )}
          >
            <input {...getInputProps()} />
            <Upload className="h-12 w-12 mx-auto text-gray-400 mb-4" />
            {isDragActive ? (
              <p className="text-primary-600 font-medium">Drop files here...</p>
            ) : (
              <>
                <p className="text-gray-600 font-medium mb-1">
                  Drag & drop files here, or click to browse
                </p>
                <p className="text-sm text-gray-500">
                  Supports PPTX, PDF, DOCX, PNG, JPG (max 50MB each)
                </p>
              </>
            )}
          </div>

          {/* Error messages */}
          {errors.length > 0 && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-3">
              <div className="flex items-center gap-2 text-red-800 mb-2">
                <AlertCircle className="h-4 w-4" />
                <span className="font-medium text-sm">Some files were rejected</span>
              </div>
              <ul className="text-sm text-red-600 space-y-1">
                {errors.map((error, i) => (
                  <li key={i}>{error}</li>
                ))}
              </ul>
            </div>
          )}

          {/* File list */}
          {files.length > 0 && (
            <div className="space-y-2">
              <h3 className="font-medium text-gray-700">
                Selected Files ({files.length})
              </h3>
              <ul className="space-y-2">
                {files.map((file, index) => (
                  <li 
                    key={`${file.name}-${index}`}
                    className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                  >
                    <div className="flex items-center gap-3">
                      <File className="h-5 w-5 text-gray-500" />
                      <div>
                        <p className="text-sm font-medium text-gray-900">
                          {file.name}
                        </p>
                        <p className="text-xs text-gray-500">
                          {formatFileSize(file.size)}
                        </p>
                      </div>
                    </div>
                    <button
                      onClick={() => removeFile(index)}
                      className="p-1 text-gray-400 hover:text-red-500 transition-colors"
                    >
                      <X className="h-4 w-4" />
                    </button>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </CardBody>

        <CardFooter className="flex justify-between">
          <Button 
            variant="ghost" 
            onClick={() => navigate('/')}
          >
            Back
          </Button>
          <Button 
            onClick={handleUpload}
            disabled={files.length === 0}
            loading={uploading}
          >
            Upload & Process
            <ArrowRight className="ml-2 h-4 w-4" />
          </Button>
        </CardFooter>
      </Card>
    </div>
  )
}
