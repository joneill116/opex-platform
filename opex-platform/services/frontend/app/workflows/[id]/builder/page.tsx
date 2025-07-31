'use client'

// Test different import methods
import { useQuery } from '@tanstack/react-query'
import WorkflowBuilder from '@/components/WorkflowBuilder'
import { useWorkflow } from '@/lib/hooks/useWorkflows'

interface PageProps {
  params: { id: string }
}

export default function WorkflowBuilderPage({ params }: PageProps) {
  // Test direct useQuery first
  const testQuery = useQuery({
    queryKey: ['test'],
    queryFn: async () => ({ test: 'working' }),
  })

  console.log('Test query:', testQuery)
  console.log('useQuery type:', typeof useQuery)
  
  const { data: workflow, isLoading } = useWorkflow(params.id)

  if (isLoading) {
    return <div className="flex items-center justify-center h-screen">Loading workflow...</div>
  }

  if (!workflow) {
    return <div className="flex items-center justify-center h-screen">Workflow not found</div>
  }

  return <WorkflowBuilder workflow={workflow} />
}
