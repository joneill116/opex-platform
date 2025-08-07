'use client'

import WorkflowBuilder from '../../../../components/WorkflowBuilder'
import { useWorkflow } from '../../../../lib/hooks/useWorkflows'

interface PageProps {
  params: { id: string }
}

export default function WorkflowBuilderPage({ params }: PageProps) {
  const { data: workflow, isLoading } = useWorkflow(params.id)

  if (isLoading) {
    return <div className="flex items-center justify-center h-screen">Loading workflow...</div>
  }

  if (!workflow) {
    return <div className="flex items-center justify-center h-screen">Workflow not found</div>
  }

  return <WorkflowBuilder workflow={workflow} />
}
