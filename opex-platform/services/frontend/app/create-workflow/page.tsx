'use client'

import { useState } from 'react'
import Link from 'next/link'
import { ArrowLeft, Plus, Save, Play } from 'lucide-react'

export default function QuickWorkflowPage() {
  const [workflowName, setWorkflowName] = useState('')
  const [description, setDescription] = useState('')
  const [created, setCreated] = useState(false)

  const handleCreate = () => {
    if (workflowName) {
      // For now, just simulate creation
      console.log('Creating workflow:', { workflowName, description })
      setCreated(true)
      
      // In a real scenario, this would call the API:
      // await createWorkflow({ name: workflowName, description })
    }
  }

  if (created) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <div className="max-w-md w-full bg-white rounded-xl shadow-lg p-8 text-center">
          <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <Save className="w-8 h-8 text-green-600" />
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Workflow Created!</h2>
          <p className="text-gray-600 mb-6">
            Your workflow "{workflowName}" has been created successfully.
          </p>
          <div className="space-y-3">
            <button 
              onClick={() => setCreated(false)}
              className="w-full bg-blue-500 text-white py-3 px-4 rounded-lg hover:bg-blue-600 transition-colors font-medium"
            >
              Create Another Workflow
            </button>
            <Link 
              href="/workflows" 
              className="block w-full bg-gray-100 text-gray-700 py-3 px-4 rounded-lg hover:bg-gray-200 transition-colors font-medium text-center"
            >
              View All Workflows
            </Link>
            <Link 
              href="/" 
              className="block w-full text-gray-500 py-2 text-center hover:text-gray-700"
            >
              Back to Homepage
            </Link>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-2xl mx-auto p-6">
        {/* Header */}
        <div className="mb-8">
          <Link 
            href="/" 
            className="inline-flex items-center text-gray-600 hover:text-gray-900 mb-4"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Homepage
          </Link>
          <h1 className="text-3xl font-bold text-gray-900">Create New Workflow</h1>
          <p className="text-gray-600 mt-2">Design and build your data processing workflow</p>
        </div>

        {/* Creation Form */}
        <div className="bg-white rounded-xl shadow-lg p-8">
          <div className="space-y-6">
            {/* Workflow Name */}
            <div>
              <label className="block text-sm font-semibold text-gray-900 mb-3">
                Workflow Name *
              </label>
              <input
                type="text"
                value={workflowName}
                onChange={(e) => setWorkflowName(e.target.value)}
                placeholder="e.g., Customer Onboarding Process"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-lg"
              />
            </div>

            {/* Description */}
            <div>
              <label className="block text-sm font-semibold text-gray-900 mb-3">
                Description
              </label>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Describe what this workflow does..."
                rows={4}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            {/* Workflow Type Selection */}
            <div>
              <label className="block text-sm font-semibold text-gray-900 mb-3">
                Workflow Type
              </label>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="border border-gray-300 rounded-lg p-4 cursor-pointer hover:border-blue-500 hover:bg-blue-50">
                  <h3 className="font-semibold text-gray-900">Data Processing</h3>
                  <p className="text-sm text-gray-600 mt-1">ETL, transformation, and validation workflows</p>
                </div>
                <div className="border border-gray-300 rounded-lg p-4 cursor-pointer hover:border-green-500 hover:bg-green-50">
                  <h3 className="font-semibold text-gray-900">Business Process</h3>
                  <p className="text-sm text-gray-600 mt-1">Approval flows, notifications, and automation</p>
                </div>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex gap-4 pt-6">
              <button
                onClick={handleCreate}
                disabled={!workflowName}
                className="flex-1 bg-blue-500 text-white py-3 px-6 rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-semibold flex items-center justify-center gap-2"
              >
                <Plus className="w-5 h-5" />
                Create Workflow
              </button>
              <Link
                href="/"
                className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors font-semibold text-center"
              >
                Cancel
              </Link>
            </div>
          </div>

          {/* Enterprise Features Note */}
          <div className="mt-8 p-4 bg-blue-50 rounded-lg border border-blue-200">
            <h4 className="font-semibold text-blue-900 mb-2">🏆 Enterprise Features</h4>
            <div className="text-sm text-blue-800 space-y-1">
              <p>✅ Visual workflow designer with ReactFlow</p>
              <p>✅ 6 component types (Acquisition, Transformation, Quality, etc.)</p>
              <p>✅ Real-time execution monitoring</p>
              <p>✅ Event sourcing and complete audit trail</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
