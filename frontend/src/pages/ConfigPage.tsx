import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Key, CheckCircle, AlertCircle, ArrowRight } from 'lucide-react'
import toast from 'react-hot-toast'
import { Card, CardHeader, CardBody, CardFooter } from '../components/ui/Card'
import Button from '../components/ui/Button'
import Input from '../components/ui/Input'
import { useAppStore } from '../store/appStore'
import { validateApiKey, createSession } from '../lib/api'

export default function ConfigPage() {
  const navigate = useNavigate()
  const { apiKey, setApiKey, setSessionId, setCurrentStep } = useAppStore()
  
  const [key, setKey] = useState(apiKey || '')
  const [loading, setLoading] = useState(false)
  const [validated, setValidated] = useState(!!apiKey)
  const [error, setError] = useState('')

  const handleValidate = async () => {
    if (!key.trim()) {
      setError('Please enter your OpenRouter API key')
      return
    }
    
    if (loading) return // Prevent double-click

    setLoading(true)
    setError('')

    try {
      const result = await validateApiKey(key.trim())
      
      if (result.valid) {
        setApiKey(key.trim())
        setValidated(true)
        toast.success('API key validated successfully!')
      } else {
        setError(result.message || 'Invalid API key')
      }
    } catch (err) {
      setError('Failed to validate API key. Please check your connection.')
    } finally {
      setLoading(false)
    }
  }

  const handleContinue = async () => {
    if (loading) return // Prevent double-click
    
    setLoading(true)
    
    try {
      const session = await createSession()
      setSessionId(session.id)
      setCurrentStep(1)
      navigate('/upload')
    } catch (err) {
      toast.error('Failed to create session')
    } finally {
      setLoading(false)
    }
  }

  const handleClear = () => {
    setApiKey(null)
    setKey('')
    setValidated(false)
    setError('')
  }

  return (
    <div className="max-w-lg mx-auto">
      <Card>
        <CardHeader>
          <div className="flex items-center gap-3">
            <div className="p-2 bg-primary-100 rounded-lg">
              <Key className="h-6 w-6 text-primary-600" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-gray-900">
                Configure API Key
              </h2>
              <p className="text-sm text-gray-500">
                Enter your OpenRouter API key to get started
              </p>
            </div>
          </div>
        </CardHeader>

        <CardBody className="space-y-4">
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h3 className="font-medium text-blue-800 mb-2">
              🔑 Bring Your Own Key (BYOK)
            </h3>
            <p className="text-sm text-blue-700">
              Your API key is stored locally in your browser and is never sent to our servers.
              We use free models from OpenRouter for processing.
            </p>
          </div>

          <Input
            label="OpenRouter API Key"
            type="password"
            placeholder="sk-or-v1-..."
            value={key}
            onChange={(e) => {
              setKey(e.target.value)
              setValidated(false)
              setError('')
            }}
            error={error}
            helperText="Get your API key from OpenRouter"
            disabled={loading}
          />

          {validated && (
            <div className="flex items-center gap-2 text-green-600 bg-green-50 p-3 rounded-lg">
              <CheckCircle className="h-5 w-5" />
              <span className="text-sm font-medium">API key validated successfully</span>
            </div>
          )}

          {error && (
            <div className="flex items-center gap-2 text-red-600 bg-red-50 p-3 rounded-lg">
              <AlertCircle className="h-5 w-5" />
              <span className="text-sm">{error}</span>
            </div>
          )}
        </CardBody>

        <CardFooter className="flex justify-between">
          {validated ? (
            <>
              <Button variant="ghost" onClick={handleClear}>
                Change Key
              </Button>
              <Button onClick={handleContinue} loading={loading}>
                Continue
                <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </>
          ) : (
            <>
              <a 
                href="https://openrouter.ai/keys" 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-sm text-primary-600 hover:underline"
              >
                Get an API key →
              </a>
              <Button onClick={handleValidate} loading={loading}>
                Validate Key
              </Button>
            </>
          )}
        </CardFooter>
      </Card>
    </div>
  )
}
