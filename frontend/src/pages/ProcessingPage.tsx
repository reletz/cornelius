import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Loader2, CheckCircle, XCircle, ArrowRight, RefreshCw } from 'lucide-react'
import toast from 'react-hot-toast'
import { Card, CardHeader, CardBody, CardFooter } from '../components/ui/Card'
import Button from '../components/ui/Button'
import ProgressBar from '../components/ui/ProgressBar'
import { useAppStore } from '../store/appStore'
import { listDocuments } from '../lib/api'
import { cn } from '../lib/utils'

export default function ProcessingPage() {
  const navigate = useNavigate()
  const { sessionId, documents, setDocuments, setCurrentStep } = useAppStore()
  
  const [polling, setPolling] = useState(true)

  useEffect(() => {
    if (!sessionId || !polling) return

    const pollDocuments = async () => {
      try {
        const result = await listDocuments(sessionId)
        setDocuments(result.documents)
        
        // Check if all done
        const allDone = result.documents.every(
          (doc: { status: string }) => doc.status === 'extracted' || doc.status === 'failed'
        )
        
        if (allDone) {
          setPolling(false)
        }
      } catch (err) {
        console.error('Failed to poll documents:', err)
      }
    }

    const interval = setInterval(pollDocuments, 2000)
    pollDocuments() // Initial call

    return () => clearInterval(interval)
  }, [sessionId, polling, setDocuments])

  const extractedCount = documents.filter(d => d.status === 'extracted').length
  const failedCount = documents.filter(d => d.status === 'failed').length
  const processingCount = documents.filter(d => d.status === 'processing' || d.status === 'uploaded').length
  const progress = documents.length > 0 
    ? ((extractedCount + failedCount) / documents.length) * 100 
    : 0

  const allDone = processingCount === 0 && documents.length > 0
  const hasExtracted = extractedCount > 0

  const handleContinue = () => {
    if (!hasExtracted) {
      toast.error('No documents were processed successfully')
      return
    }
    setCurrentStep(3)
    navigate('/clustering')
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'extracted':
        return <CheckCircle className="h-5 w-5 text-green-500" />
      case 'failed':
        return <XCircle className="h-5 w-5 text-red-500" />
      default:
        return <Loader2 className="h-5 w-5 text-primary-500 animate-spin" />
    }
  }

  const getStatusText = (status: string) => {
    switch (status) {
      case 'uploaded':
        return 'Queued'
      case 'processing':
        return 'Processing...'
      case 'extracted':
        return 'Completed'
      case 'failed':
        return 'Failed'
      default:
        return status
    }
  }

  return (
    <div className="max-w-2xl mx-auto">
      <Card>
        <CardHeader>
          <div className="flex items-center gap-3">
            <div className={cn(
              "p-2 rounded-lg",
              allDone ? "bg-green-100" : "bg-primary-100"
            )}>
              {allDone ? (
                <CheckCircle className="h-6 w-6 text-green-600" />
              ) : (
                <Loader2 className="h-6 w-6 text-primary-600 animate-spin" />
              )}
            </div>
            <div>
              <h2 className="text-lg font-semibold text-gray-900">
                {allDone ? 'Processing Complete' : 'Processing Documents'}
              </h2>
              <p className="text-sm text-gray-500">
                {allDone 
                  ? `${extractedCount} of ${documents.length} documents processed successfully`
                  : 'Extracting text from your documents...'
                }
              </p>
            </div>
          </div>
        </CardHeader>

        <CardBody className="space-y-6">
          {/* Progress */}
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Overall Progress</span>
              <span className="text-gray-900 font-medium">
                {extractedCount + failedCount} / {documents.length}
              </span>
            </div>
            <ProgressBar value={progress} />
          </div>

          {/* Document list */}
          <div className="space-y-2">
            <h3 className="font-medium text-gray-700">Documents</h3>
            <ul className="space-y-2">
              {documents.map((doc) => (
                <li 
                  key={doc.id}
                  className={cn(
                    "flex items-center justify-between p-3 rounded-lg",
                    doc.status === 'failed' ? "bg-red-50" : "bg-gray-50"
                  )}
                >
                  <div className="flex items-center gap-3">
                    {getStatusIcon(doc.status)}
                    <div>
                      <p className="text-sm font-medium text-gray-900">
                        {doc.filename}
                      </p>
                      {doc.errorMessage && (
                        <p className="text-xs text-red-600">
                          {doc.errorMessage}
                        </p>
                      )}
                    </div>
                  </div>
                  <span className={cn(
                    "text-sm",
                    doc.status === 'extracted' && "text-green-600",
                    doc.status === 'failed' && "text-red-600",
                    (doc.status === 'processing' || doc.status === 'uploaded') && "text-gray-500"
                  )}>
                    {getStatusText(doc.status)}
                  </span>
                </li>
              ))}
            </ul>
          </div>

          {/* Stats */}
          {allDone && (
            <div className="grid grid-cols-3 gap-4">
              <div className="text-center p-3 bg-green-50 rounded-lg">
                <p className="text-2xl font-bold text-green-600">{extractedCount}</p>
                <p className="text-sm text-green-700">Successful</p>
              </div>
              <div className="text-center p-3 bg-red-50 rounded-lg">
                <p className="text-2xl font-bold text-red-600">{failedCount}</p>
                <p className="text-sm text-red-700">Failed</p>
              </div>
              <div className="text-center p-3 bg-gray-100 rounded-lg">
                <p className="text-2xl font-bold text-gray-600">{documents.length}</p>
                <p className="text-sm text-gray-700">Total</p>
              </div>
            </div>
          )}
        </CardBody>

        <CardFooter className="flex justify-between">
          <Button 
            variant="ghost" 
            onClick={() => navigate('/upload')}
          >
            Back
          </Button>
          <div className="flex gap-2">
            {!allDone && (
              <Button 
                variant="secondary"
                onClick={() => setPolling(true)}
              >
                <RefreshCw className="mr-2 h-4 w-4" />
                Refresh
              </Button>
            )}
            <Button 
              onClick={handleContinue}
              disabled={!allDone || !hasExtracted}
            >
              Continue to Clustering
              <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          </div>
        </CardFooter>
      </Card>
    </div>
  )
}
