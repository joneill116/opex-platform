import { useComponentTypes, ComponentTypeInfo } from '../lib/hooks/useComponentTypes'
import { ComponentType } from '../lib/types/workflow'
import { 
  Database, 
  Shuffle, 
  CheckCircle, 
  Briefcase, 
  PlusCircle, 
  Upload 
} from 'lucide-react'

const componentIcons: Record<ComponentType, React.ReactNode> = {
  [ComponentType.ACQUISITION]: <Database className="w-5 h-5" />,
  [ComponentType.TRANSFORMATION]: <Shuffle className="w-5 h-5" />,
  [ComponentType.TECHNICAL_QUALITY]: <CheckCircle className="w-5 h-5" />,
  [ComponentType.BUSINESS_QUALITY]: <Briefcase className="w-5 h-5" />,
  [ComponentType.ENRICHMENT]: <PlusCircle className="w-5 h-5" />,
  [ComponentType.PUBLISH]: <Upload className="w-5 h-5" />,
}

export default function ComponentPalette() {
  const { data: componentTypes, isLoading } = useComponentTypes()

  const onDragStart = (event: React.DragEvent, type: ComponentType, name: string) => {
    event.dataTransfer.setData('componentType', type)
    event.dataTransfer.setData('componentName', name)
    event.dataTransfer.effectAllowed = 'move'
  }

  if (isLoading) return <div className="w-64 bg-gray-50 p-4">Loading components...</div>

  return (
    <div className="w-64 bg-gray-50 h-screen flex flex-col">
      <div className="p-4 border-b bg-white">
        <h2 className="text-lg font-semibold text-gray-800">Components</h2>
      </div>
      
      <div className="flex-1 overflow-y-auto p-4">
        <div className="space-y-2">
          {componentTypes?.types.map((type: ComponentTypeInfo) => (
            <div
              key={type.type}
              draggable
              onDragStart={(e) => onDragStart(e, type.type as ComponentType, type.name)}
              className="group p-3 bg-white rounded-lg shadow-sm cursor-move hover:shadow-md transition-all duration-200 border border-gray-200"
              style={{ borderLeft: `4px solid ${type.color}` }}
            >
              <div className="flex items-center space-x-3">
                <div 
                  className="w-10 h-10 rounded-lg flex items-center justify-center text-white"
                  style={{ backgroundColor: type.color }}
                >
                  {componentIcons[type.type as ComponentType]}
                </div>
                <div className="flex-1">
                  <div className="font-medium text-gray-900">{type.name}</div>
                  <div className="text-xs text-gray-500">{type.description}</div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
