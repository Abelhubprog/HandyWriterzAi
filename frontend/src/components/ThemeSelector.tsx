'use client'

import { Monitor, Sun, Moon } from 'lucide-react'
import { useTheme } from '@/contexts/ThemeContext'

interface ThemeOption {
  id: 'system' | 'light' | 'dark'
  label: string
  icon: React.ComponentType<{ className?: string }>
}

const themeOptions: ThemeOption[] = [
  {
    id: 'system',
    label: 'System Mode',
    icon: Monitor
  },
  {
    id: 'light',
    label: 'Light Mode',
    icon: Sun
  },
  {
    id: 'dark',
    label: 'Dark Mode',
    icon: Moon
  }
]

export function ThemeSelector() {
  const { theme, setTheme } = useTheme()

  return (
    <div className="space-y-4">
      <div>
        <h3 className="text-base font-medium text-gray-900 dark:text-gray-100 mb-1">
          Theme
        </h3>
      </div>
      
      <div className="grid grid-cols-3 gap-3">
        {themeOptions.map((option) => {
          const Icon = option.icon
          const isActive = theme === option.id
          
          return (
            <button
              key={option.id}
              onClick={() => setTheme(option.id)}
              aria-pressed={isActive}
              className={`relative flex flex-col items-center justify-center p-4 py-6 rounded-xl border transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 dark:focus:ring-offset-gray-800 ${
                isActive
                  ? 'border-blue-500 bg-blue-50 dark:bg-blue-950/50 shadow-sm'
                  : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600 bg-white dark:bg-gray-800/50 hover:bg-gray-50 dark:hover:bg-gray-800'
              }`}
            >
              <Icon className={`w-5 h-5 mb-3 ${
                isActive 
                  ? 'text-blue-600 dark:text-blue-400' 
                  : 'text-gray-500 dark:text-gray-400'
              }`} />
              
              <span className={`text-sm font-medium text-center ${
                isActive 
                  ? 'text-blue-900 dark:text-blue-100' 
                  : 'text-gray-700 dark:text-gray-300'
              }`}>
                {option.label}
              </span>
              
              {isActive && (
                <div className="absolute top-3 right-3">
                  <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                </div>
              )}
            </button>
          )
        })}
      </div>
    </div>
  )
}