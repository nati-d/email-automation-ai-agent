"use client"

import * as React from "react"
import { cn } from "@/lib/utils"

interface TooltipProps {
  children: React.ReactNode
  content: string
  side?: "top" | "right" | "bottom" | "left"
  align?: "start" | "center" | "end"
  className?: string
}

export function Tooltip({
  children,
  content,
  side = "top",
  align = "center",
  className,
}: TooltipProps) {
  const [isVisible, setIsVisible] = React.useState(false)
  const [position, setPosition] = React.useState({ top: 0, left: 0 })
  const childRef = React.useRef<HTMLDivElement>(null)
  const tooltipRef = React.useRef<HTMLDivElement>(null)

  const calculatePosition = React.useCallback(() => {
    if (!childRef.current || !tooltipRef.current) return

    const childRect = childRef.current.getBoundingClientRect()
    const tooltipRect = tooltipRef.current.getBoundingClientRect()
    
    let top = 0
    let left = 0

    switch (side) {
      case "top":
        top = childRect.top - tooltipRect.height - 8
        break
      case "right":
        left = childRect.right + 8
        break
      case "bottom":
        top = childRect.bottom + 8
        break
      case "left":
        left = childRect.left - tooltipRect.width - 8
        break
    }

    switch (side) {
      case "top":
      case "bottom":
        switch (align) {
          case "start":
            left = childRect.left
            break
          case "center":
            left = childRect.left + (childRect.width / 2) - (tooltipRect.width / 2)
            break
          case "end":
            left = childRect.right - tooltipRect.width
            break
        }
        break
      case "left":
      case "right":
        switch (align) {
          case "start":
            top = childRect.top
            break
          case "center":
            top = childRect.top + (childRect.height / 2) - (tooltipRect.height / 2)
            break
          case "end":
            top = childRect.bottom - tooltipRect.height
            break
        }
        break
    }

    setPosition({ top, left })
  }, [side, align])

  React.useEffect(() => {
    if (isVisible) {
      calculatePosition()
    }
  }, [isVisible, calculatePosition])

  const handleMouseEnter = () => {
    setIsVisible(true)
  }

  const handleMouseLeave = () => {
    setIsVisible(false)
  }

  return (
    <div 
      className="relative inline-block"
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      onFocus={handleMouseEnter}
      onBlur={handleMouseLeave}
      ref={childRef}
    >
      {children}
      {isVisible && (
        <div
          ref={tooltipRef}
          className={cn(
            "fixed z-50 px-2 py-1 text-xs font-medium text-white bg-gray-900 dark:bg-gray-700 rounded shadow-sm whitespace-nowrap",
            className
          )}
          style={{
            top: `${position.top}px`,
            left: `${position.left}px`,
          }}
        >
          {content}
        </div>
      )}
    </div>
  )
}