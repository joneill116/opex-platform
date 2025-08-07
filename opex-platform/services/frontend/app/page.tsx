import Link from 'next/link'
import { Workflow, Plus, Layers, BarChart3 } from 'lucide-react'

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="flex min-h-screen flex-col items-center justify-center p-24">
        <div className="text-center mb-12">
          <div className="flex items-center justify-center mb-6">
            <Workflow className="h-16 w-16 text-blue-600 mr-4" />
            <h1 className="text-6xl font-bold text-gray-900">OpEx Platform</h1>
          </div>
          <p className="text-2xl text-gray-600 mb-8">Operational Excellence for Financial Operations</p>
          <p className="text-lg text-gray-500">Enterprise-grade workflow orchestration with Martin Fowler patterns</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl w-full">
          {/* Create New Workflow */}
          <Link 
            href="/create-workflow" 
            className="bg-white p-8 rounded-xl shadow-lg hover:shadow-xl transition-shadow border border-gray-200 hover:border-blue-300 group"
          >
            <div className="flex flex-col items-center text-center">
              <div className="bg-blue-100 p-4 rounded-full mb-4 group-hover:bg-blue-200 transition-colors">
                <Plus className="h-8 w-8 text-blue-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Create Workflow</h3>
              <p className="text-gray-600">Design and build new data processing workflows</p>
            </div>
          </Link>

          {/* View All Workflows */}
          <Link 
            href="/workflows" 
            className="bg-white p-8 rounded-xl shadow-lg hover:shadow-xl transition-shadow border border-gray-200 hover:border-green-300 group"
          >
            <div className="flex flex-col items-center text-center">
              <div className="bg-green-100 p-4 rounded-full mb-4 group-hover:bg-green-200 transition-colors">
                <Layers className="h-8 w-8 text-green-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Manage Workflows</h3>
              <p className="text-gray-600">View and edit existing workflow configurations</p>
            </div>
          </Link>

          {/* Analytics Dashboard */}
          <div className="bg-white p-8 rounded-xl shadow-lg border border-gray-200 opacity-75">
            <div className="flex flex-col items-center text-center">
              <div className="bg-purple-100 p-4 rounded-full mb-4">
                <BarChart3 className="h-8 w-8 text-purple-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Analytics</h3>
              <p className="text-gray-600">Performance metrics and workflow insights</p>
              <span className="text-sm text-gray-400 mt-2">Coming Soon</span>
            </div>
          </div>
        </div>

        <div className="mt-12 text-center">
          <div className="bg-white p-6 rounded-lg shadow border border-gray-200">
            <h4 className="font-semibold text-gray-900 mb-2">🏆 Enterprise Features Active</h4>
            <div className="flex flex-wrap justify-center gap-4 text-sm text-gray-600">
              <span>✅ Event Sourcing</span>
              <span>✅ CQRS Architecture</span>
              <span>✅ ReactFlow Builder</span>
              <span>✅ JWT Authentication</span>
              <span>✅ Kong API Gateway</span>
              <span>✅ Distributed Tracing</span>
            </div>
          </div>
        </div>
      </div>
    </main>
  )
}
