'use client'

import { useState, useEffect } from 'react'
import { X, Save, AlertTriangle, Info, Settings, CheckCircle } from 'lucide-react'
import { ComponentType } from '../lib/types/workflow'
import { COMPONENT_COLORS } from '../lib/constants/componentConfig'

interface ComponentConfigPanelProps {
  nodeId: string
  componentType: ComponentType
  config: Record<string, any>
  onConfigUpdate: (nodeId: string, config: Record<string, any>) => void
  onClose: () => void
}

interface ConfigField {
  key: string
  label: string
  type: 'text' | 'number' | 'select' | 'boolean' | 'textarea' | 'array'
  required?: boolean
  options?: string[]
  placeholder?: string
  description?: string
  validation?: {
    min?: number
    max?: number
    pattern?: string
    message?: string
  }
}

interface ComponentConfigDefinition {
  name: string
  description: string
  fields: ConfigField[]
  expectations: {
    input: string[]
    output: string[]
    performance: string
    reliability: string
  }
}

// Enterprise-level component configuration definitions
const COMPONENT_CONFIG_DEFINITIONS: Record<ComponentType, ComponentConfigDefinition> = {
  [ComponentType.ACQUISITION]: {
    name: 'Data Acquisition',
    description: 'Acquire data from external sources with enterprise reliability patterns',
    fields: [
      {
        key: 'source_type',
        label: 'Source Type',
        type: 'select',
        required: true,
        options: ['API', 'Database', 'File', 'Message Queue', 'WebSocket', 'FTP'],
        description: 'Type of data source to connect to'
      },
      {
        key: 'connection_string',
        label: 'Connection String/URL',
        type: 'text',
        required: true,
        placeholder: 'e.g., https://api.example.com/v1/data',
        description: 'Connection details for the data source'
      },
      {
        key: 'authentication',
        label: 'Authentication Type',
        type: 'select',
        required: true,
        options: ['None', 'API Key', 'OAuth2', 'Basic Auth', 'JWT', 'Certificate'],
        description: 'Authentication method for secure access'
      },
      {
        key: 'credentials',
        label: 'Credentials',
        type: 'textarea',
        placeholder: 'JSON format: {"api_key": "xxx", "secret": "yyy"}',
        description: 'Authentication credentials (stored securely)'
      },
      {
        key: 'poll_interval',
        label: 'Poll Interval (seconds)',
        type: 'number',
        validation: { min: 1, max: 86400 },
        placeholder: '300',
        description: 'How often to check for new data'
      },
      {
        key: 'batch_size',
        label: 'Batch Size',
        type: 'number',
        validation: { min: 1, max: 10000 },
        placeholder: '1000',
        description: 'Number of records to process at once'
      },
      {
        key: 'retry_attempts',
        label: 'Retry Attempts',
        type: 'number',
        validation: { min: 0, max: 10 },
        placeholder: '3',
        description: 'Number of retry attempts on failure'
      }
    ],
    expectations: {
      input: ['None - This is a source component'],
      output: ['Raw data records', 'Metadata about acquisition'],
      performance: '< 5 seconds per batch',
      reliability: '99.9% uptime with circuit breaker protection'
    }
  },
  [ComponentType.TRANSFORMATION]: {
    name: 'Data Transformation',
    description: 'Transform and manipulate data using configurable rules',
    fields: [
      {
        key: 'transformation_type',
        label: 'Transformation Type',
        type: 'select',
        required: true,
        options: ['Map Fields', 'Filter Records', 'Aggregate', 'Join', 'Custom SQL', 'Python Script'],
        description: 'Type of transformation to apply'
      },
      {
        key: 'transformation_config',
        label: 'Transformation Configuration',
        type: 'textarea',
        required: true,
        placeholder: 'JSON or SQL configuration',
        description: 'Configuration specific to the transformation type'
      },
      {
        key: 'field_mappings',
        label: 'Field Mappings',
        type: 'textarea',
        placeholder: '{"source_field": "target_field"}',
        description: 'Map source fields to target schema'
      },
      {
        key: 'validation_rules',
        label: 'Validation Rules',
        type: 'textarea',
        placeholder: 'JSON array of validation rules',
        description: 'Data validation rules to apply'
      },
      {
        key: 'error_handling',
        label: 'Error Handling',
        type: 'select',
        required: true,
        options: ['Fail Fast', 'Skip Invalid', 'Log and Continue', 'Dead Letter Queue'],
        description: 'How to handle transformation errors'
      }
    ],
    expectations: {
      input: ['Structured data records', 'Schema definition'],
      output: ['Transformed data records', 'Transformation metrics'],
      performance: '< 100ms per record for simple transforms',
      reliability: '99.99% success rate with proper error handling'
    }
  },
  [ComponentType.TECHNICAL_QUALITY]: {
    name: 'Technical Quality Check',
    description: 'Validate data technical quality and completeness',
    fields: [
      {
        key: 'quality_rules',
        label: 'Quality Rules',
        type: 'textarea',
        required: true,
        placeholder: 'JSON array of quality check rules',
        description: 'Technical quality validation rules'
      },
      {
        key: 'completeness_threshold',
        label: 'Completeness Threshold (%)',
        type: 'number',
        validation: { min: 0, max: 100 },
        placeholder: '95',
        description: 'Minimum data completeness percentage'
      },
      {
        key: 'accuracy_checks',
        label: 'Accuracy Checks',
        type: 'textarea',
        placeholder: 'JSON array of accuracy validation rules',
        description: 'Data accuracy validation rules'
      },
      {
        key: 'freshness_threshold',
        label: 'Data Freshness (minutes)',
        type: 'number',
        validation: { min: 1, max: 10080 },
        placeholder: '60',
        description: 'Maximum age of data to be considered fresh'
      },
      {
        key: 'fail_on_quality',
        label: 'Fail on Quality Issues',
        type: 'boolean',
        description: 'Stop processing if quality thresholds not met'
      }
    ],
    expectations: {
      input: ['Data records', 'Quality rule definitions'],
      output: ['Quality metrics', 'Flagged records', 'Quality score'],
      performance: '< 50ms per record for quality checks',
      reliability: 'Must maintain audit trail of all quality assessments'
    }
  },
  [ComponentType.BUSINESS_QUALITY]: {
    name: 'Business Quality Check',
    description: 'Validate data against business rules and requirements',
    fields: [
      {
        key: 'business_rules',
        label: 'Business Rules',
        type: 'textarea',
        required: true,
        placeholder: 'JSON array of business validation rules',
        description: 'Business logic validation rules'
      },
      {
        key: 'reference_data',
        label: 'Reference Data Sources',
        type: 'textarea',
        placeholder: 'JSON array of reference data connections',
        description: 'External reference data for validation'
      },
      {
        key: 'tolerance_level',
        label: 'Tolerance Level',
        type: 'select',
        required: true,
        options: ['Strict', 'Moderate', 'Lenient'],
        description: 'How strict to be with business rule violations'
      },
      {
        key: 'escalation_rules',
        label: 'Escalation Rules',
        type: 'textarea',
        placeholder: 'JSON configuration for escalation',
        description: 'Rules for escalating business quality issues'
      }
    ],
    expectations: {
      input: ['Data records', 'Business rule definitions', 'Reference data'],
      output: ['Business validation results', 'Exception reports'],
      performance: '< 200ms per record for business validation',
      reliability: 'Must ensure business rule consistency and auditability'
    }
  },
  [ComponentType.ENRICHMENT]: {
    name: 'Data Enrichment',
    description: 'Enrich data with additional information and context',
    fields: [
      {
        key: 'enrichment_sources',
        label: 'Enrichment Sources',
        type: 'textarea',
        required: true,
        placeholder: 'JSON array of enrichment data sources',
        description: 'External sources for data enrichment'
      },
      {
        key: 'matching_strategy',
        label: 'Matching Strategy',
        type: 'select',
        required: true,
        options: ['Exact Match', 'Fuzzy Match', 'ML-based', 'Rule-based'],
        description: 'How to match records for enrichment'
      },
      {
        key: 'enrichment_fields',
        label: 'Fields to Enrich',
        type: 'textarea',
        placeholder: 'JSON array of field enrichment configurations',
        description: 'Which fields to enrich and how'
      },
      {
        key: 'fallback_strategy',
        label: 'Fallback Strategy',
        type: 'select',
        required: true,
        options: ['Use Default', 'Skip Field', 'Use Previous', 'Mark as Missing'],
        description: 'What to do when enrichment fails'
      }
    ],
    expectations: {
      input: ['Base data records', 'Enrichment configurations'],
      output: ['Enriched data records', 'Enrichment statistics'],
      performance: '< 500ms per record including external lookups',
      reliability: 'Must handle enrichment source failures gracefully'
    }
  },
  [ComponentType.PUBLISH]: {
    name: 'Data Publication',
    description: 'Publish processed data to target systems',
    fields: [
      {
        key: 'destination_type',
        label: 'Destination Type',
        type: 'select',
        required: true,
        options: ['Database', 'API', 'File System', 'Message Queue', 'Data Lake', 'Dashboard'],
        description: 'Where to publish the processed data'
      },
      {
        key: 'destination_config',
        label: 'Destination Configuration',
        type: 'textarea',
        required: true,
        placeholder: 'JSON configuration for the destination',
        description: 'Connection and formatting details'
      },
      {
        key: 'format',
        label: 'Output Format',
        type: 'select',
        required: true,
        options: ['JSON', 'CSV', 'Parquet', 'Avro', 'XML', 'Custom'],
        description: 'Format for the output data'
      },
      {
        key: 'publishing_strategy',
        label: 'Publishing Strategy',
        type: 'select',
        required: true,
        options: ['Batch', 'Stream', 'Micro-batch', 'Event-driven'],
        description: 'How to publish the data'
      },
      {
        key: 'notification_config',
        label: 'Notifications',
        type: 'textarea',
        placeholder: 'JSON configuration for success/failure notifications',
        description: 'Notification settings for publishing events'
      }
    ],
    expectations: {
      input: ['Processed data records', 'Publishing configurations'],
      output: ['Publishing confirmation', 'Delivery metrics'],
      performance: '< 1 second per batch for most destinations',
      reliability: 'Must ensure at-least-once delivery with idempotency'
    }
  }
}

export default function ComponentConfigPanel({ 
  nodeId, 
  componentType, 
  config, 
  onConfigUpdate, 
  onClose 
}: ComponentConfigPanelProps) {
  const [localConfig, setLocalConfig] = useState<Record<string, any>>(config || {})
  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({})
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false)

  const configDefinition = COMPONENT_CONFIG_DEFINITIONS[componentType]

  useEffect(() => {
    setLocalConfig(config || {})
    setHasUnsavedChanges(false)
  }, [config, nodeId])

  const validateField = (field: ConfigField, value: any): string | null => {
    if (field.required && (!value || value === '')) {
      return `${field.label} is required`
    }

    if (field.validation) {
      if (field.type === 'number' && value) {
        const numValue = Number(value)
        if (field.validation.min !== undefined && numValue < field.validation.min) {
          return `${field.label} must be at least ${field.validation.min}`
        }
        if (field.validation.max !== undefined && numValue > field.validation.max) {
          return `${field.label} must be at most ${field.validation.max}`
        }
      }

      if (field.validation.pattern && value) {
        const regex = new RegExp(field.validation.pattern)
        if (!regex.test(value)) {
          return field.validation.message || `${field.label} format is invalid`
        }
      }
    }

    return null
  }

  const handleFieldChange = (fieldKey: string, value: any) => {
    const field = configDefinition.fields.find(f => f.key === fieldKey)
    if (!field) return

    setLocalConfig(prev => ({ ...prev, [fieldKey]: value }))
    setHasUnsavedChanges(true)

    // Validate field
    const error = validateField(field, value)
    setValidationErrors(prev => ({
      ...prev,
      [fieldKey]: error || ''
    }))
  }

  const handleSave = () => {
    // Validate all fields
    const errors: Record<string, string> = {}
    let hasErrors = false

    configDefinition.fields.forEach(field => {
      const error = validateField(field, localConfig[field.key])
      if (error) {
        errors[field.key] = error
        hasErrors = true
      }
    })

    if (hasErrors) {
      setValidationErrors(errors)
      return
    }

    onConfigUpdate(nodeId, localConfig)
    setHasUnsavedChanges(false)
  }

  const renderField = (field: ConfigField) => {
    const value = localConfig[field.key] || ''
    const error = validationErrors[field.key]

    switch (field.type) {
      case 'text':
        return (
          <input
            type="text"
            value={value}
            onChange={(e) => handleFieldChange(field.key, e.target.value)}
            placeholder={field.placeholder}
            className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
              error ? 'border-red-500' : 'border-gray-300'
            }`}
          />
        )

      case 'number':
        return (
          <input
            type="number"
            value={value}
            onChange={(e) => handleFieldChange(field.key, Number(e.target.value))}
            placeholder={field.placeholder}
            min={field.validation?.min}
            max={field.validation?.max}
            className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
              error ? 'border-red-500' : 'border-gray-300'
            }`}
          />
        )

      case 'select':
        return (
          <select
            value={value}
            onChange={(e) => handleFieldChange(field.key, e.target.value)}
            className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
              error ? 'border-red-500' : 'border-gray-300'
            }`}
          >
            <option value="">Select {field.label}</option>
            {field.options?.map(option => (
              <option key={option} value={option}>{option}</option>
            ))}
          </select>
        )

      case 'boolean':
        return (
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={value || false}
              onChange={(e) => handleFieldChange(field.key, e.target.checked)}
              className="mr-2"
            />
            Enable {field.label}
          </label>
        )

      case 'textarea':
        return (
          <textarea
            value={value}
            onChange={(e) => handleFieldChange(field.key, e.target.value)}
            placeholder={field.placeholder}
            rows={4}
            className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 resize-vertical ${
              error ? 'border-red-500' : 'border-gray-300'
            }`}
          />
        )

      default:
        return null
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b">
          <div className="flex items-center gap-3">
            <Settings className="w-6 h-6 text-blue-500" />
            <div>
              <h2 className="text-xl font-semibold text-gray-800">
                Configure {configDefinition.name}
              </h2>
              <p className="text-sm text-gray-600">{configDefinition.description}</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Content */}
        <div className="overflow-y-auto" style={{ maxHeight: 'calc(90vh - 140px)' }}>
          <div className="p-6">
            {/* Configuration Fields */}
            <div className="space-y-6">
              <h3 className="text-lg font-medium text-gray-800 flex items-center gap-2">
                <Settings className="w-5 h-5" />
                Configuration
              </h3>
              
              {configDefinition.fields.map(field => (
                <div key={field.key} className="space-y-2">
                  <label className="flex items-center gap-2 text-sm font-medium text-gray-700">
                    {field.label}
                    {field.required && <span className="text-red-500">*</span>}
                    {field.description && (
                      <div className="group relative">
                        <Info className="w-4 h-4 text-gray-400 cursor-help" />
                        <div className="absolute left-0 top-6 hidden group-hover:block bg-gray-800 text-white text-xs rounded py-2 px-3 max-w-xs z-10">
                          {field.description}
                        </div>
                      </div>
                    )}
                  </label>
                  
                  {renderField(field)}
                  
                  {validationErrors[field.key] && (
                    <div className="flex items-center gap-2 text-red-500 text-sm">
                      <AlertTriangle className="w-4 h-4" />
                      {validationErrors[field.key]}
                    </div>
                  )}
                </div>
              ))}
            </div>

            {/* Expectations Section */}
            <div className="mt-8 space-y-4">
              <h3 className="text-lg font-medium text-gray-800 flex items-center gap-2">
                <CheckCircle className="w-5 h-5" />
                Component Expectations
              </h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="bg-blue-50 p-4 rounded-lg">
                  <h4 className="font-medium text-blue-800 mb-2">Expected Input</h4>
                  <ul className="text-sm text-blue-700 space-y-1">
                    {configDefinition.expectations.input.map((input, index) => (
                      <li key={index}>• {input}</li>
                    ))}
                  </ul>
                </div>
                
                <div className="bg-green-50 p-4 rounded-lg">
                  <h4 className="font-medium text-green-800 mb-2">Expected Output</h4>
                  <ul className="text-sm text-green-700 space-y-1">
                    {configDefinition.expectations.output.map((output, index) => (
                      <li key={index}>• {output}</li>
                    ))}
                  </ul>
                </div>
                
                <div className="bg-yellow-50 p-4 rounded-lg">
                  <h4 className="font-medium text-yellow-800 mb-2">Performance</h4>
                  <p className="text-sm text-yellow-700">{configDefinition.expectations.performance}</p>
                </div>
                
                <div className="bg-purple-50 p-4 rounded-lg">
                  <h4 className="font-medium text-purple-800 mb-2">Reliability</h4>
                  <p className="text-sm text-purple-700">{configDefinition.expectations.reliability}</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between p-6 border-t bg-gray-50">
          <div className="text-sm text-gray-500">
            {hasUnsavedChanges && (
              <span className="flex items-center gap-1 text-orange-600">
                <AlertTriangle className="w-4 h-4" />
                You have unsaved changes
              </span>
            )}
          </div>
          
          <div className="flex items-center gap-3">
            <button
              onClick={onClose}
              className="px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors"
            >
              Cancel
            </button>
            <button
              onClick={handleSave}
              disabled={Object.values(validationErrors).some(error => error)}
              className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
            >
              <Save className="w-4 h-4" />
              Save Configuration
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
