"use client"

import { useEffect, useState } from "react"
import type React from "react"
import { CheckCircle, AlertCircle, Info, X } from "lucide-react"

interface ToastProps {
  message: string
  type: string
  visible: boolean
}

export const Toast: React.FC<ToastProps> = ({ message, type, visible }) => {
  const [isVisible, setIsVisible] = useState(false)

  useEffect(() => {
    setIsVisible(visible)
  }, [visible, message])

  const getIcon = () => {
    switch (type) {
      case "success":
        return <CheckCircle size={18} />
      case "error":
        return <AlertCircle size={18} />
      default:
        return <Info size={18} />
    }
  }

  if (!isVisible) return null

  return (
    <div className={`toast ${type} ${isVisible ? "visible" : ""}`}>
      <div className="toast-icon">{getIcon()}</div>
      <div className="toast-message">{message}</div>
      <button className="toast-close" onClick={() => setIsVisible(false)}>
        <X size={16} />
      </button>
    </div>
  )
}
