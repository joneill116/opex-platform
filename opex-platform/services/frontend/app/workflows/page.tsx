'use client'

import { useWorkflows, useCreateWorkflow } from '../../lib/hooks/useWorkflows'
import { useState } from 'react'
import Link from 'next/link'
import { Plus, Edit, Calendar, Layers } from 'lucide-react'

export default function WorkflowsPage() {
  const { data: workflows, isLoading, error } = useWorkflows()
  const createWorkflow = useCreateWorkflow()
  const [newWorkflowName, setNewWorkflowName] = useState('')

  const handleCreate = () => {
    if (newWorkflowName) {
      createWorkflow.mutate({
        name: newWorkflowName,
        severity: 'medium',
        solutions: ['Automated solution'],
      })
      setNewWorkflowName('')
    }
  }

  if (isLoading) return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="text-gray-600">Loading workflows...</div>
    </div>
  )
  
  if (error) return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="text-red-500">Error loading workflows</div>
    </div>
  )

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Workflows</h1>
          <p className="mt-2 text-gray-600">Manage your data processing workflows</p>
        </div>
        
        <div className="mb-6 bg-white p-4 rounded-lg shadow-sm border border-gray-200">
          <div className="flex gap-3">
            <input
              type="text"
              value={newWorkflowName}
              onChange={(e) => setNewWorkflowName(e.target.value)}
              placeholder="Enter workflow name..."
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              onKeyPress={(e) => e.key === 'Enter' && handleCreate()}
            />
            <button
              onClick={handleCreate}
              disabled={createWorkflow.isPending || !newWorkflowName}
              className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2 font-medium"
            >
              <Plus className="w-4 h-4" />
              {createWorkflow.isPending ? 'Creating...' : 'Create Workflow'}
            </button>
          </div>
        </div>

        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {workflows?.map((workflow) => (
            <div key={workflow.id} className="bg-white rounded-lg shadow-sm border border-gray-200 hover:shadow-md transition-shadow">
              <div className="p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-2">{workflow.name}</h3>
                {workflow.description && (
                  <p className="text-gray-600 text-sm mb-4">{workflow.description}</p>
                )}
                
                <div className="space-y-2 mb-4">
                  <div className="flex items-center text-sm text-gray-500">
                    <Layers className="w-4 h-4 mr-2" />
                    <span>{workflow.components.length} components</span>
                  </div>
                  <div className="flex items-center text-sm text-gray-500">
                    <Calendar className="w-4 h-4 mr-2" />
                    <span>{new Date(workflow.created_at).toLocaleDateString()}</span>
                  </div>
                </div>
                
                <div className="flex items-center justify-between">
                  <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                    workflow.status === 'active' 
                      ? 'bg-green-100 text-green-800' 
                      : 'bg-gray-100 text-gray-800'
                  }`}>
                    {workflow.status}
                  </span>
                  
                  <Link
                    href={`/workflows/${workflow.id}/builder`}
                    className="inline-flex items-center gap-2 px-4 py-2 bg-indigo-500 text-white rounded-lg hover:bg-indigo-600 transition-colors text-sm font-medium"
                  >
                    <Edit className="w-4 h-4" />
                    Edit Workflow
                  </Link>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
