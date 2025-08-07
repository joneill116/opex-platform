'use client'

import { Handle, Position } from 'reactflow'
import { ComponentType } from '../lib/types/workflow'
import { COMPONENT_COLORS } from '../lib/constants/componentConfig'
import { 
  Database, 
  Shuffle, 
  CheckCircle, 
  Briefcase, 
  PlusCircle, 
  Upload 
} from 'lucide-react'

interface WorkflowNodeProps {
  data: {
    label: string
    type: ComponentType
    config: Record<string, any>
  }
  selected: boolean
}

const nodeIcons: Record<ComponentType, React.ReactNode> = {
  [ComponentType.ACQUISITION]: <Database className="w-4 h-4" />,
  [ComponentType.TRANSFORMATION]: <Shuffle className="w-4 h-4" />,
  [ComponentType.TECHNICAL_QUALITY]: <CheckCircle className="w-4 h-4" />,
  [ComponentType.BUSINESS_QUALITY]: <Briefcase className="w-4 h-4" />,
  [ComponentType.ENRICHMENT]: <PlusCircle className="w-4 h-4" />,
  [ComponentType.PUBLISH]: <Upload className="w-4 h-4" />,
}

export default function WorkflowNode({ data, selected }: WorkflowNodeProps) {
  const color = COMPONENT_COLORS[data.type] || '#6B7280'
  const icon = nodeIcons[data.type]

  return (
    <div
      className={`px-4 py-3 shadow-lg rounded-lg bg-white border-2 min-w-[200px] ${
        selected ? 'border-blue-500 shadow-xl' : 'border-gray-200'
      } hover:shadow-xl transition-all duration-200`}
      style={{ borderTop: `4px solid ${color}` }}
    >
      <Handle 
        type="target" 
        position={Position.Top} 
        className="w-3 h-3"
        style={{ background: color, border: '2px solid white' }}
      />
      
      <div className="flex items-center gap-3">
        <div 
          className="w-8 h-8 rounded flex items-center justify-center text-white flex-shrink-0"
          style={{ backgroundColor: color }}
        >
          {icon}
        </div>
        <div>
          <div className="font-semibold text-gray-800">{data.label}</div>
          <div className="text-xs text-gray-500 capitalize">{data.type.replace('-', ' ')}</div>
        </div>
      </div>
      
      <Handle 
        type="source" 
        position={Position.Bottom} 
        className="w-3 h-3"
        style={{ background: color, border: '2px solid white' }}
      />
    </div>
  )
}
