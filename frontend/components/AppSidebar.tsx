"use client"

import * as React from "react"
import Link from "next/link"
import {
  Inbox,
  Star,
  Tag,
  Plus,
  ChevronDown,
  LogOut,
  Settings,
  HelpCircle,
  UserIcon,
  Send,
  FileText,
  ChevronUp,
  Mail,
} from "lucide-react"

import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarSeparator,
  useSidebar,
} from "@/components/ui/sidebar"
import { Button } from "@/components/ui/button"
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { fetchCategories, createCategory, Category } from "@/lib/api/categories"
import { useApp } from "./AppContext"
import { AddCategoryModal } from "./email/AddCategoryModal"
import { useComposeModal } from "@/components/email/ComposeEmail";

// Define User type locally for now
interface User {
  name: string;
  email: string;
  userId: string;
  isNewUser?: string;
  sessionId: string;
  profilePicture?: string;
}

const SIDEBAR_ITEMS = [
  { label: "Inbox", icon: Inbox, count: 150, active: true, href: "#" },
  { label: "Starred", icon: Star, count: 0, href: "#" },
  { label: "Sent", icon: Send, count: 0, href: "#" },
  { label: "Drafts", icon: FileText, count: 0, href: "#" },
  { label: "Important", icon: Tag, count: 0, href: "#" },
]

export function AppSidebar() {
  const { toggleSidebar } = useSidebar()
  const { currentCategory, setCurrentCategory } = useApp()
  const [user, setUser] = React.useState<User | null>(null)
  const [categories, setCategories] = React.useState<Category[]>([])
  const [loading, setLoading] = React.useState(true)
  const [modalOpen, setModalOpen] = React.useState(false)
  const [modalLoading, setModalLoading] = React.useState(false)
  const [addAccountLoading, setAddAccountLoading] = React.useState(false)
  const { openCompose } = useComposeModal();

  React.useEffect(() => {
    const stored = localStorage.getItem("user")
    if (stored) {
      setUser(JSON.parse(stored))
    }
  }, [])

  React.useEffect(() => {
    const loadCategories = async () => {
      try {
        setLoading(true)
        const categoriesData = await fetchCategories()
        setCategories(categoriesData)
      } catch (error) {
        console.error("Failed to fetch categories:", error)
        setCategories([])
      } finally {
        setLoading(false)
      }
    }

    loadCategories()
  }, [])

  const handleCategoryClick = (categoryName: string) => {
    setCurrentCategory(categoryName)
  }

  const handleInboxClick = () => {
    setCurrentCategory(null) // Clear category filter to show all emails
  }

  const handleAddCategory = async (categoryData: { name: string }) => {
    try {
      setModalLoading(true)
      const newCategory = await createCategory(categoryData)
      setCategories(prev => [...prev, newCategory])
      setModalOpen(false)
    } catch (error) {
      console.error("Failed to create category:", error)
      // You might want to show a toast notification here
    } finally {
      setModalLoading(false)
    }
  }

  function handleLogout() {
    localStorage.removeItem("user")
    window.location.reload()
  }

  // Add Account integration
  const handleAddAccount = async () => {
    if (typeof window === 'undefined') return;
    const userStr = localStorage.getItem('user');
    if (!userStr) return;
    const user = JSON.parse(userStr);
    const sessionId = user.sessionId || user.session_id;
    if (!sessionId) return;
    setAddAccountLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/oauth/add-another-account/initiate', {
        headers: {
          'Authorization': `Bearer ${sessionId}`,
        },
      });
      const data = await response.json();
      if (response.ok && data.authorization_url) {
        window.location.href = data.authorization_url;
      } else {
        alert(data.detail?.message || data.message || 'Failed to get OAuth URL for adding another account');
      }
    } catch (error: any) {
      alert('Failed to initiate add account: ' + (error.message || error));
    } finally {
      setAddAccountLoading(false);
    }
  };

  return (
    <>
      <Sidebar
        className="border-r w-60 min-w-0 max-w-full overflow-x-hidden "
        style={{
          background: 'var(--sidebar)',
          color: 'var(--sidebar-foreground)',
          borderColor: 'var(--sidebar-border)',
        }}
        collapsible="none"
      >
        <SidebarHeader className="p-4 flex flex-col gap-4 w-full min-w-0 max-w-full overflow-x-hidden">
          <div className="flex items-center gap-2">
            {/* Email Agent logo */}
            <Mail className="w-6 h-6" style={{ color: 'var(--primary)' }} />
            <span className="text-xl font-semibold" style={{ color: 'var(--sidebar-foreground)' }}>Email Agent</span>
          </div>
          <Button
            className="w-full font-semibold rounded-full px-6 py-3 shadow transition text-base"
            style={{ background: 'var(--primary)', color: 'var(--primary-foreground)' }}
            onClick={openCompose}
          >
            <Plus className="w-5 h-5 mr-2" /> COMPOSE
          </Button>
        </SidebarHeader>
        <SidebarContent className="flex-1 overflow-y-auto px-4 w-full min-w-0 max-w-full overflow-x-hidden hide-scrollbar">
          <SidebarGroup>
            <SidebarMenu>
              {SIDEBAR_ITEMS.map(({ label, icon: Icon, count, active, href }) => (
                <SidebarMenuItem key={label}>
                  <SidebarMenuButton
                    asChild
                    isActive={active && !currentCategory}
                    className={active && !currentCategory ? 'relative bg-[color:var(--sidebar-accent)]/30 border-l-4 border-[color:var(--primary)] text-[color:var(--primary)] font-semibold' : 'hover:bg-[color:var(--sidebar-accent)]/20'}
                    style={active && !currentCategory ? { background: 'rgba(25, 118, 210, 0.08)', borderLeft: '4px solid var(--primary)', color: 'var(--primary)', fontWeight: 600 } : {}}
                  >
                    <Link href={href} className="flex items-center w-full max-w-full justify-between gap-2 truncate" onClick={label === "Inbox" ? handleInboxClick : undefined}>
                      <span className="flex items-center gap-2 truncate">
                        <Icon className="w-5 h-5 shrink-0" />
                        <span className="truncate">{label}</span>
                      </span>
                      {count > 0 && (
                        <span className="bg-zinc-200 text-zinc-700 rounded-full px-2 py-0.5 text-xs font-semibold truncate max-w-[48px] text-ellipsis overflow-hidden">
                          {count}
                        </span>
                      )}
                    </Link>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroup>

          <SidebarSeparator className="my-4" />

          <Collapsible defaultOpen className="group/collapsible">
            <SidebarGroup>
              <SidebarGroupLabel asChild>
                <div className="flex items-center justify-between w-full">
                  <CollapsibleTrigger className="flex items-center justify-between text-xs font-semibold uppercase tracking-wide text-zinc-500 hover:text-zinc-700 py-2 rounded-md">
                    Categories
                    <ChevronDown className="ml-auto h-4 w-4 transition-transform group-data-[state=open]/collapsible:rotate-180" />
                  </CollapsibleTrigger>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => setModalOpen(true)}
                    className="h-6 w-6 text-zinc-500 hover:text-zinc-700"
                  >
                    <Plus className="h-3 w-3" />
                  </Button>
                </div>
              </SidebarGroupLabel>
              <CollapsibleContent>
                <SidebarGroupContent className="mt-2">
                  <SidebarMenu>
                    {loading ? (
                      <div className="px-2 py-2 text-xs text-zinc-500">Loading categories...</div>
                    ) : (
                      <>
                        {/* All category - always show */}
                        <SidebarMenuItem>
                          <SidebarMenuButton
                            asChild
                            isActive={!currentCategory}
                            className={!currentCategory ? 'bg-[color:var(--sidebar-accent)]/20 text-[color:var(--primary)] font-medium' : 'hover:bg-[color:var(--sidebar-accent)]/10'}
                            style={!currentCategory ? { background: 'rgba(25, 118, 210, 0.15)', color: 'var(--primary)' } : {}}
                          >
                            <Link 
                              href="#" 
                              className="flex items-center w-full max-w-full justify-between gap-2 truncate"
                              onClick={() => handleCategoryClick('')}
                            >
                              <span className="flex items-center gap-2 truncate">
                                <span 
                                  className="w-2 h-2 rounded-full" 
                                  style={{ background: '#6b7280' }}
                                />
                                <span className="truncate">All</span>
                              </span>
                              <span className="ml-auto bg-gray-100 text-gray-700 rounded-full px-2 py-0.5 text-xs font-semibold truncate max-w-[48px] text-ellipsis overflow-hidden">
                                All
                              </span>
                            </Link>
                          </SidebarMenuButton>
                        </SidebarMenuItem>
                        
                        {categories.length > 0 ? (
                          categories.map((category) => {
                            const isActive = currentCategory === category.name
                            return (
                              <SidebarMenuItem key={category.id}>
                                <SidebarMenuButton
                                  asChild
                                  isActive={isActive}
                                  className={isActive ? 'bg-[color:var(--sidebar-accent)]/20 text-[color:var(--primary)] font-medium' : 'hover:bg-[color:var(--sidebar-accent)]/10'}
                                  style={isActive ? { background: 'rgba(25, 118, 210, 0.15)', color: 'var(--primary)' } : {}}
                                >
                                  <Link 
                                    href="#" 
                                    className="flex items-center w-full max-w-full justify-between gap-2 truncate"
                                    onClick={() => handleCategoryClick(category.name || '')}
                                  >
                                    <span className="flex items-center gap-2 truncate">
                                      <span 
                                        className="w-2 h-2 rounded-full" 
                                        style={{ background: category.color || '#3b82f6' }}
                                      />
                                      <span className="truncate">{category.name}</span>
                                    </span>
                                    {category.count && (
                                      <span className="ml-auto bg-blue-100 text-blue-700 rounded-full px-2 py-0.5 text-xs font-semibold truncate max-w-[48px] text-ellipsis overflow-hidden">
                                        {category.count.toLocaleString()}
                                      </span>
                                    )}
                                  </Link>
                                </SidebarMenuButton>
                              </SidebarMenuItem>
                            )
                          })
                        ) : (
                          <div className="px-2 py-2 text-xs text-zinc-500">No categories found</div>
                        )}
                      </>
                    )}
                  </SidebarMenu>
                </SidebarGroupContent>
              </CollapsibleContent>
            </SidebarGroup>
          </Collapsible>
        </SidebarContent>
        <SidebarFooter className="p-2 border-t w-full min-w-0 max-w-full overflow-x-hidden" style={{ borderColor: 'var(--sidebar-border)' }}>
          <SidebarMenu>
            <SidebarMenuItem>
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <SidebarMenuButton>
                    <Avatar className="h-6 w-6">
                      <AvatarImage src={user?.profilePicture || "/placeholder.svg"} alt={user?.name || "User"} />
                      <AvatarFallback className="bg-zinc-200 text-zinc-700 text-xs font-medium">
                        {user?.name ? user.name.charAt(0).toUpperCase() : "U"}
                      </AvatarFallback>
                    </Avatar>
                    <span className="truncate">{user?.name || "Guest User"}</span>
                    <ChevronUp className="ml-auto h-4 w-4" />
                  </SidebarMenuButton>
                </DropdownMenuTrigger>
                <DropdownMenuContent side="top" align="start" className="w-[--radix-popper-anchor-width]">
                  <DropdownMenuItem onClick={handleAddAccount} disabled={addAccountLoading}>
                    <Plus className="mr-2 h-4 w-4" />
                    <span>{addAccountLoading ? 'Redirecting...' : 'Add Account'}</span>
                  </DropdownMenuItem>
                  <DropdownMenuItem>
                    <HelpCircle className="mr-2 h-4 w-4" />
                    <span>Help</span>
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={handleLogout}>
                    <LogOut className="mr-2 h-4 w-4" />
                    <span>Log out</span>
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </SidebarMenuItem>
          </SidebarMenu>
        </SidebarFooter>
      </Sidebar>

      <AddCategoryModal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        onSubmit={handleAddCategory}
        loading={modalLoading}
      />
    </>
  )
} 