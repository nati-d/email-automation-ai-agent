'use client'

import { useState } from 'react'
import { EmailSidebar } from './email-sidebar'
import { EmailList } from './email-list'
import { EmailView } from './email-view'
import { ComposeEmail } from './compose-email'
import { Button } from '@/components/ui/button'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { ThemeToggle } from '@/components/ui/theme-toggle'
import { useAuthStore } from '@/lib/store'
import { useLogout } from '@/lib/queries'
import { Menu, LogOut, Settings, User } from 'lucide-react'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { cn } from '@/lib/utils'

export function EmailLayout() {
  const [selectedEmailId, setSelectedEmailId] = useState<string | null>(null)
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const { user } = useAuthStore()
  const logout = useLogout()

  const handleEmailSelect = (emailId: string) => {
    setSelectedEmailId(emailId)
  }

  const handleBackToList = () => {
    setSelectedEmailId(null)
  }

  const handleLogout = () => {
    logout.mutate()
  }

  return (
    <div className="h-screen flex flex-col">
      {/* Header */}
      <header className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="flex items-center justify-between px-4 py-3">
          <div className="flex items-center gap-3">
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="md:hidden"
            >
              <Menu className="h-4 w-4" />
            </Button>
            <h1 className="text-xl font-semibold">Email Agent</h1>
          </div>

          <div className="flex items-center gap-2">
            <ThemeToggle />
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" className="relative h-8 w-8 rounded-full">
                  <Avatar className="h-8 w-8">
                    <AvatarImage src={user?.picture} alt={user?.name} />
                    <AvatarFallback>
                      {user?.name?.slice(0, 2).toUpperCase() || 'U'}
                    </AvatarFallback>
                  </Avatar>
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent className="w-56" align="end" forceMount>
                <div className="flex items-center justify-start gap-2 p-2">
                  <div className="flex flex-col space-y-1 leading-none">
                    {user?.name && (
                      <p className="font-medium">{user.name}</p>
                    )}
                    {user?.email && (
                      <p className="w-[200px] truncate text-sm text-muted-foreground">
                        {user.email}
                      </p>
                    )}
                  </div>
                </div>
                <DropdownMenuSeparator />
                <DropdownMenuItem>
                  <User className="mr-2 h-4 w-4" />
                  Profile
                </DropdownMenuItem>
                <DropdownMenuItem>
                  <Settings className="mr-2 h-4 w-4" />
                  Settings
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={handleLogout}>
                  <LogOut className="mr-2 h-4 w-4" />
                  Log out
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>
      </header>

      {/* Main content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Sidebar */}
        <aside className={cn(
          'w-64 border-r bg-muted/10 transition-all duration-300',
          !sidebarOpen && 'w-0 overflow-hidden md:w-64'
        )}>
          <EmailSidebar />
        </aside>

        {/* Email list */}
        <div className={cn(
          'flex-1 flex transition-all duration-300',
          selectedEmailId ? 'md:flex' : 'flex'
        )}>
          <div className={cn(
            'w-full border-r transition-all duration-300',
            selectedEmailId ? 'hidden md:block md:w-1/2 lg:w-2/5' : 'block'
          )}>
            <EmailList
              onEmailSelect={handleEmailSelect}
              selectedEmailId={selectedEmailId || undefined}
            />
          </div>

          {/* Email view */}
          {selectedEmailId && (
            <div className={cn(
              'w-full transition-all duration-300',
              'md:w-1/2 lg:w-3/5'
            )}>
              <EmailView
                emailId={selectedEmailId}
                onBack={handleBackToList}
              />
            </div>
          )}
        </div>
      </div>

      {/* Compose modal */}
      <ComposeEmail />
    </div>
  )
}