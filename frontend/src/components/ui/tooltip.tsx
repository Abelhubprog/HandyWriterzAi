import React from 'react'

interface TooltipProps {
  content: string
  children: React.ReactNode
  side?: 'top' | 'right' | 'bottom' | 'left'
}

export function Tooltip({ content, children, side = 'right' }: TooltipProps) {
  const sideClasses = {
    top: 'bottom-full mb-2 left-1/2 transform -translate-x-1/2',
    right: 'left-full ml-2 top-1/2 transform -translate-y-1/2',
    bottom: 'top-full mt-2 left-1/2 transform -translate-x-1/2',
    left: 'right-full mr-2 top-1/2 transform -translate-y-1/2'
  }

  return (
    <div className="relative group">
      {children}
      <span
        className={`absolute z-50 px-2 py-1 bg-gray-800 text-white text-xs rounded opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none whitespace-nowrap ${sideClasses[side]}`}
      >
        {content}
      </span>
    </div>
  )
}