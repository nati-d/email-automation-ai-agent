'use client'

import { useState } from 'react'
import { useCategories, useCreateCategory, useUpdateCategory, useDeleteCategory, useRecategorizeEmails } from '@/lib/queries'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { useToast } from '@/components/providers/toast-provider'
import { Loader2, Plus, Edit, Trash2, RefreshCw, Check } from 'lucide-react'

interface Category {
  id: string
  name: string
  description?: string
  color?: string
  is_active: boolean
  user_id: string
  created_at: string
  updated_at: string
}

export function CategoryManager() {
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false)
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false)
  const [newCategory, setNewCategory] = useState({ name: '', description: '', color: '#6366f1' })
  const [editingCategory, setEditingCategory] = useState<Category | null>(null)
  
  const { data: categoriesData, isLoading } = useCategories()
  const createCategory = useCreateCategory()
  const updateCategory = useUpdateCategory()
  const deleteCategory = useDeleteCategory()
  const recategorizeEmails = useRecategorizeEmails()
  const { toast } = useToast()
  
  const handleCreateCategory = async () => {
    if (!newCategory.name.trim()) {
      toast.error('Validation Error', 'Category name is required')
      return
    }
    
    try {
      await createCategory.mutateAsync({
        name: newCategory.name,
        description: newCategory.description || undefined,
        color: newCategory.color
      })
      
      setNewCategory({ name: '', description: '', color: '#6366f1' })
      setIsCreateDialogOpen(false)
      toast.success('Category Created', `Category "${newCategory.name}" has been created`)
    } catch (error) {
      toast.error('Error', `Failed to create category: ${error instanceof Error ? error.message : 'Unknown error'}`)
    }
  }
  
  const handleEditCategory = (category: Category) => {
    setEditingCategory(category)
    setIsEditDialogOpen(true)
  }
  
  const handleUpdateCategory = async () => {
    if (!editingCategory) return
    
    if (!editingCategory.name.trim()) {
      toast.error('Validation Error', 'Category name is required')
      return
    }
    
    try {
      await updateCategory.mutateAsync({
        categoryId: editingCategory.id,
        data: {
          name: editingCategory.name,
          description: editingCategory.description,
          color: editingCategory.color
        }
      })
      
      setIsEditDialogOpen(false)
      toast.success('Category Updated', `Category "${editingCategory.name}" has been updated`)
    } catch (error) {
      toast.error('Error', `Failed to update category: ${error instanceof Error ? error.message : 'Unknown error'}`)
    }
  }
  
  const handleDeleteCategory = async (categoryId: string, categoryName: string) => {
    if (confirm(`Are you sure you want to delete the category "${categoryName}"? This will re-categorize all emails using this category.`)) {
      try {
        await deleteCategory.mutateAsync(categoryId)
        toast.success('Category Deleted', `Category "${categoryName}" has been deleted`)
      } catch (error) {
        toast.error('Error', `Failed to delete category: ${error instanceof Error ? error.message : 'Unknown error'}`)
      }
    }
  }
  
  const handleRecategorizeEmails = async () => {
    try {
      const result = await recategorizeEmails.mutateAsync()
      toast.success('Emails Re-categorized', `Successfully re-categorized ${result.recategorized_count} emails`)
    } catch (error) {
      toast.error('Error', `Failed to re-categorize emails: ${error instanceof Error ? error.message : 'Unknown error'}`)
    }
  }
  
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold">Email Categories</h2>
        <div className="flex items-center gap-2">
          <Button 
            variant="outline" 
            onClick={handleRecategorizeEmails}
            disabled={recategorizeEmails.isPending}
            className="gap-2"
          >
            {recategorizeEmails.isPending ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <RefreshCw className="h-4 w-4" />
            )}
            Re-categorize Emails
          </Button>
          
          <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
            <DialogTrigger asChild>
              <Button className="gap-2 bg-purple-500 hover:bg-purple-600 text-white">
                <Plus className="h-4 w-4" />
                New Category
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Create New Category</DialogTitle>
                <DialogDescription>
                  Create a new category to organize your emails
                </DialogDescription>
              </DialogHeader>
              
              <div className="grid gap-4 py-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium">Name</label>
                  <Input
                    value={newCategory.name}
                    onChange={(e) => setNewCategory({ ...newCategory, name: e.target.value })}
                    placeholder="Category name"
                  />
                </div>
                
                <div className="space-y-2">
                  <label className="text-sm font-medium">Description (optional)</label>
                  <Textarea
                    value={newCategory.description}
                    onChange={(e) => setNewCategory({ ...newCategory, description: e.target.value })}
                    placeholder="Brief description"
                  />
                </div>
                
                <div className="space-y-2">
                  <label className="text-sm font-medium">Color</label>
                  <div className="flex items-center gap-2">
                    <input
                      type="color"
                      value={newCategory.color}
                      onChange={(e) => setNewCategory({ ...newCategory, color: e.target.value })}
                      className="h-10 w-10 rounded border"
                    />
                    <span className="text-sm text-muted-foreground">
                      Choose a color for this category
                    </span>
                  </div>
                </div>
              </div>
              
              <DialogFooter>
                <Button variant="outline" onClick={() => setIsCreateDialogOpen(false)}>
                  Cancel
                </Button>
                <Button 
                  onClick={handleCreateCategory} 
                  disabled={createCategory.isPending}
                  className="bg-purple-500 hover:bg-purple-600 text-white"
                >
                  {createCategory.isPending ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Creating...
                    </>
                  ) : (
                    'Create Category'
                  )}
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </div>
      </div>
      
      {isLoading ? (
        <div className="flex justify-center p-8">
          <Loader2 className="h-8 w-8 animate-spin text-purple-500" />
        </div>
      ) : !categoriesData || categoriesData.categories.length === 0 ? (
        <div className="text-center p-8 border rounded-lg bg-muted/30">
          <h3 className="text-lg font-medium mb-2">No Categories Yet</h3>
          <p className="text-muted-foreground mb-4">
            Create categories to help organize your emails automatically
          </p>
          <Button 
            onClick={() => setIsCreateDialogOpen(true)}
            className="bg-purple-500 hover:bg-purple-600 text-white"
          >
            <Plus className="mr-2 h-4 w-4" />
            Create Your First Category
          </Button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {categoriesData.categories.map((category) => (
            <Card key={category.id}>
              <CardHeader className="pb-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div 
                      className="w-4 h-4 rounded-full" 
                      style={{ backgroundColor: category.color || '#6366f1' }} 
                    />
                    <CardTitle className="text-base">{category.name}</CardTitle>
                  </div>
                  <div className="flex items-center gap-1">
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-8 w-8"
                      onClick={() => handleEditCategory(category)}
                    >
                      <Edit className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-8 w-8"
                      onClick={() => handleDeleteCategory(category.id, category.name)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
                {category.description && (
                  <CardDescription>{category.description}</CardDescription>
                )}
              </CardHeader>
              <CardFooter className="pt-2 text-xs text-muted-foreground">
                Created {new Date(category.created_at).toLocaleDateString()}
              </CardFooter>
            </Card>
          ))}
        </div>
      )}
      
      {/* Edit Category Dialog */}
      <Dialog open={isEditDialogOpen} onOpenChange={setIsEditDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Edit Category</DialogTitle>
            <DialogDescription>
              Update your category details
            </DialogDescription>
          </DialogHeader>
          
          {editingCategory && (
            <div className="grid gap-4 py-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Name</label>
                <Input
                  value={editingCategory.name}
                  onChange={(e) => setEditingCategory({ ...editingCategory, name: e.target.value })}
                  placeholder="Category name"
                />
              </div>
              
              <div className="space-y-2">
                <label className="text-sm font-medium">Description (optional)</label>
                <Textarea
                  value={editingCategory.description || ''}
                  onChange={(e) => setEditingCategory({ ...editingCategory, description: e.target.value })}
                  placeholder="Brief description"
                />
              </div>
              
              <div className="space-y-2">
                <label className="text-sm font-medium">Color</label>
                <div className="flex items-center gap-2">
                  <input
                    type="color"
                    value={editingCategory.color || '#6366f1'}
                    onChange={(e) => setEditingCategory({ ...editingCategory, color: e.target.value })}
                    className="h-10 w-10 rounded border"
                  />
                  <span className="text-sm text-muted-foreground">
                    Choose a color for this category
                  </span>
                </div>
              </div>
            </div>
          )}
          
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsEditDialogOpen(false)}>
              Cancel
            </Button>
            <Button 
              onClick={handleUpdateCategory} 
              disabled={updateCategory.isPending}
              className="bg-purple-500 hover:bg-purple-600 text-white"
            >
              {updateCategory.isPending ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Updating...
                </>
              ) : (
                'Update Category'
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}