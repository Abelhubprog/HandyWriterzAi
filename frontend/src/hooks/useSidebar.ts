import { useState, useEffect } from 'react'

const SIDEBAR_STORAGE_KEY = 'sidebar-collapsed'

export function useSidebar() {
  const [collapsed, setCollapsed] = useState(false)
  const [isMobile, setIsMobile] = useState(false)
  const [showMobileOverlay, setShowMobileOverlay] = useState(false)

  // Initialize from localStorage
  useEffect(() => {
    const saved = localStorage.getItem(SIDEBAR_STORAGE_KEY)
    if (saved !== null) {
      setCollapsed(JSON.parse(saved))
    }
  }, [])

  // Detect mobile breakpoint
  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 768) // md breakpoint
    }
    
    checkMobile()
    window.addEventListener('resize', checkMobile)
    return () => window.removeEventListener('resize', checkMobile)
  }, [])

  // Auto-collapse on mobile
  useEffect(() => {
    if (isMobile && !collapsed) {
      setCollapsed(true)
    }
  }, [isMobile])

  const toggle = () => {
    const newCollapsed = !collapsed
    setCollapsed(newCollapsed)
    localStorage.setItem(SIDEBAR_STORAGE_KEY, JSON.stringify(newCollapsed))
    
    // On mobile, show overlay when expanding
    if (isMobile && !newCollapsed) {
      setShowMobileOverlay(true)
    } else {
      setShowMobileOverlay(false)
    }
  }

  const closeMobileOverlay = () => {
    setShowMobileOverlay(false)
    if (isMobile) {
      setCollapsed(true)
    }
  }

  return {
    collapsed,
    isMobile,
    showMobileOverlay,
    toggle,
    closeMobileOverlay
  }
}