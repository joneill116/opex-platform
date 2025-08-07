'use client'

import { useState, useCallback } from 'react'
import Link from 'next/link'
import { ArrowLeft, Plus, Save, Play } from 'lucide-react'
import { Workflow, WorkflowStatus } from '../../lib/types/workflow'
import dynamic from 'next/dynamic'

// ===== CLEAN ARCHITECTURE: Martin Fowler Principles =====

/**
 * Lazy-loaded WorkflowBuilder with proper error boundaries
 * Follows the Single Responsibility Principle
 */
const WorkflowBuilder = dynamic(
  () => import('../../components/WorkflowBuilder'),
  {
    loading: () => <LoadingSpinner />,
    ssr: false
  }
)

// ===== PURE COMPONENTS (Following Martin Fowler's Component Design) =====

interface LoadingSpinnerProps {
  message?: string
}

/**
 * Pure loading component - Single Responsibility
 */
const LoadingSpinner = ({ message = "Loading workflow builder..." }: LoadingSpinnerProps) => (
  <div className="flex items-center justify-center h-full">
    <div className="text-center">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto mb-4" />
      <p className="text-gray-600">{message}</p>
    </div>
  </div>
)

interface ActionButtonProps {
  onClick: () => void
  className: string
  children: React.ReactNode
  disabled?: boolean
  type?: 'button' | 'submit'
}

/**
 * Reusable button component - DRY Principle
 */
const ActionButton = ({ onClick, className, children, disabled = false, type = 'button' }: ActionButtonProps) => (
  <button
    type={type}
    onClick={onClick}
    disabled={disabled}
    className={className}
  >
    {children}
  </button>
)

interface WorkflowBuilderHeaderProps {
  workflowName: string
  onBack: () => void
  onSave: () => void
  onRun: () => void
}

/**
 * Workflow builder header - Extracted for reusability
 */
const WorkflowBuilderHeader = ({ workflowName, onBack, onSave, onRun }: WorkflowBuilderHeaderProps) => (
  <div className="bg-white border-b border-gray-200 px-6 py-4">
    <div className="flex items-center justify-between">
      <div className="flex items-center space-x-4">
        <ActionButton
          onClick={onBack}
          className="text-gray-500 hover:text-gray-700 transition-colors"
        >
          <ArrowLeft className="w-6 h-6" />
        </ActionButton>
        <div>
          <h1 className="text-xl font-semibold text-gray-900">{workflowName}</h1>
          <p className="text-sm text-gray-500">Visual workflow builder</p>
        </div>
      </div>
      <div className="flex items-center space-x-3">
        <ActionButton
          onClick={onSave}
          className="flex items-center px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
        >
          <Save className="w-4 h-4 mr-2" />
          Save
        </ActionButton>
        <ActionButton
          onClick={onRun}
          className="flex items-center px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 transition-colors"
        >
          <Play className="w-4 h-4 mr-2" />
          Run Workflow
        </ActionButton>
      </div>
    </div>
  </div>
)

interface WorkflowFormProps {
  workflowName: string
  description: string
  onWorkflowNameChange: (name: string) => void
  onDescriptionChange: (desc: string) => void
  onStartBuilding: () => void
  onCancel: () => void
}

/**
 * Extracted form component - Separation of Concerns
 */
const WorkflowForm = ({
  workflowName,
  description,
  onWorkflowNameChange,
  onDescriptionChange,
  onStartBuilding,
  onCancel
}: WorkflowFormProps) => (
  <div className="bg-white shadow-sm rounded-lg p-6">
    <form className="space-y-6" onSubmit={(e) => { e.preventDefault(); onStartBuilding(); }}>
      <div>
        <label 
          htmlFor="workflow-name" 
          className="block text-sm font-medium text-gray-700 mb-2"
        >
          Workflow Name
        </label>
        <input
          id="workflow-name"
          type="text"
          value={workflowName}
          onChange={(e) => onWorkflowNameChange(e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
          placeholder="Enter workflow name"
          required
        />
      </div>

      <div>
        <label 
          htmlFor="description" 
          className="block text-sm font-medium text-gray-700 mb-2"
        >
          Description
        </label>
        <textarea
          id="description"
          rows={3}
          value={description}
          onChange={(e) => onDescriptionChange(e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
          placeholder="Describe what this workflow does..."
        />
      </div>

      <div className="flex justify-end space-x-4">
        <ActionButton
          onClick={onCancel}
          className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
        >
          Cancel
        </ActionButton>
        <ActionButton
          onClick={onStartBuilding}
          disabled={!workflowName.trim()}
          className="flex items-center px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          type="submit"
        >
          <Plus className="w-4 h-4 mr-2" />
          Start Building Workflow
        </ActionButton>
      </div>
    </form>
  </div>
)

// ===== BUSINESS LOGIC (Service Layer & Factory Patterns) =====

/**
 * Factory for creating workflows - Factory Pattern
 */
class WorkflowFactory {
  static createEmptyWorkflow(name: string, description: string): Workflow {
    return {
      id: `workflow-${Date.now()}`,
      name: name.trim(),
      description: description.trim(),
      severity: 'medium',
      solutions: [],
      status: WorkflowStatus.DRAFT,
      components: [],
      connections: [],
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      created_by: 'system'
    }
  }
}

/**
 * Workflow service - Service Layer Pattern
 */
class WorkflowService {
  static async saveWorkflow(workflow: Workflow): Promise<void> {
    // TODO: Implement actual save functionality
    console.log('Saving workflow:', workflow.name)
    // Would integrate with API here
  }

  static async runWorkflow(workflow: Workflow): Promise<void> {
    // TODO: Implement actual run functionality
    console.log('Running workflow:', workflow.name)
    // Would integrate with execution engine here
  }
}

// ===== MAIN COMPONENT - CLEAN ARCHITECTURE =====

/**
 * Main component following Martin Fowler's clean architecture principles:
 * - Single Responsibility Principle
 * - Separation of Concerns
 * - Dependency Inversion
 * - Pure Functions
 */
export default function CreateWorkflowPage() {
  // State management
  const [workflowName, setWorkflowName] = useState('New Workflow')
  const [description, setDescription] = useState('')
  const [showBuilder, setShowBuilder] = useState(false)

  // Factory method for creating workflows
  const createWorkflow = useCallback((): Workflow => {
    return WorkflowFactory.createEmptyWorkflow(workflowName, description)
  }, [workflowName, description])

  // Event handlers - Pure functions
  const handleStartBuilding = useCallback(() => {
    if (!workflowName.trim()) return
    setShowBuilder(true)
  }, [workflowName])

  const handleBackToForm = useCallback(() => {
    setShowBuilder(false)
  }, [])

  const handleCancel = useCallback(() => {
    // Navigate back or reset form
    window.history.back()
  }, [])

  const handleSaveWorkflow = useCallback(async () => {
    const workflow = createWorkflow()
    await WorkflowService.saveWorkflow(workflow)
  }, [createWorkflow])

  const handleRunWorkflow = useCallback(async () => {
    const workflow = createWorkflow()
    await WorkflowService.runWorkflow(workflow)
  }, [createWorkflow])

  // Conditional rendering - Strategy Pattern
  if (showBuilder) {
    return (
      <div className="h-screen bg-gray-50">
        <WorkflowBuilderHeader
          workflowName={workflowName}
          onBack={handleBackToForm}
          onSave={handleSaveWorkflow}
          onRun={handleRunWorkflow}
        />
        <div className="h-[calc(100vh-80px)]">
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <div className="bg-blue-50 border-2 border-dashed border-blue-300 rounded-lg p-8 max-w-md mx-auto">
                <h3 className="text-lg font-medium text-blue-900 mb-2">Workflow Builder</h3>
                <p className="text-blue-700 mb-4">The workflow builder component will be loaded here.</p>
                <ActionButton
                  onClick={async () => {
                    // Try to dynamically load the workflow builder
                    try {
                      const module = await import('../../components/WorkflowBuilder')
                      console.log('WorkflowBuilder loaded successfully:', module)
                    } catch (error) {
                      console.error('Failed to load WorkflowBuilder:', error)
                    }
                  }}
                  className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
                >
                  Test Load WorkflowBuilder
                </ActionButton>
              </div>
            </div>
          </div>
        </div>
      </div>
    )
  }

  // Main form view
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-2xl mx-auto p-6">
        {/* Header */}
        <header className="mb-8">
          <Link 
            href="/" 
            className="inline-flex items-center text-gray-600 hover:text-gray-900 mb-4 transition-colors"
          >
            <ArrowLeft className="w-5 h-5 mr-2" />
            Back to Homepage
          </Link>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Create New Workflow</h1>
          <p className="text-gray-600">
            Design your operational excellence workflow with our visual builder
          </p>
        </header>

        {/* Main Form */}
        <main>
          <WorkflowForm
            workflowName={workflowName}
            description={description}
            onWorkflowNameChange={setWorkflowName}
            onDescriptionChange={setDescription}
            onStartBuilding={handleStartBuilding}
            onCancel={handleCancel}
          />
        </main>

        {/* Info Section */}
        <aside className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h3 className="text-lg font-medium text-blue-900 mb-2">
            What's Next?
          </h3>
          <p className="text-blue-700 mb-4">
            After creating your workflow, you'll be taken to our drag-and-drop visual builder where you can:
          </p>
          <ul className="text-blue-700 space-y-1">
            <li>• Add workflow components from our comprehensive palette</li>
            <li>• Connect components to define the execution flow</li>
            <li>• Configure component settings and parameters</li>
            <li>• Test and validate your workflow logic</li>
            <li>• Deploy your workflow for production use</li>
          </ul>
        </aside>
      </div>
    </div>
  )
}
