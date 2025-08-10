"use client";

import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { X, Plus } from "lucide-react";

interface AddCategoryModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (categoryData: { name: string; description?: string; color?: string }) => void;
  loading?: boolean;
}

export const AddCategoryModal: React.FC<AddCategoryModalProps> = ({
  isOpen,
  onClose,
  onSubmit,
  loading = false,
}) => {
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [color, setColor] = useState("#3b82f6");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (name.trim()) {
      onSubmit({ 
        name: name.trim(),
        description: description.trim() || undefined,
        color: color
      });
      // Reset form
      setName("");
      setDescription("");
      setColor("#3b82f6");
    }
  };

  const handleClose = () => {
    if (!loading) {
      onClose();
      // Reset form on close
      setName("");
      setDescription("");
      setColor("#3b82f6");
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-md mx-4">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b">
          <h2 className="text-lg font-semibold text-gray-900">Add New Category</h2>
          <Button
            variant="ghost"
            size="icon"
            onClick={handleClose}
            disabled={loading}
            className="h-8 w-8"
          >
            <X className="h-4 w-4" />
          </Button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {/* Name Field */}
          <div className="space-y-2">
            <Label htmlFor="category-name" className="text-sm font-medium text-gray-700">
              Category Name *
            </Label>
            <Input
              id="category-name"
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Enter category name"
              required
              disabled={loading}
              className="w-full"
            />
          </div>

          {/* Description Field */}
          <div className="space-y-2">
            <Label htmlFor="category-description" className="text-sm font-medium text-gray-700">
              Description
            </Label>
            <Textarea
              id="category-description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Describe what emails belong to this category (helps with AI classification)"
              disabled={loading}
              className="w-full min-h-[80px] resize-none"
              maxLength={200}
            />
            <p className="text-xs text-gray-500">
              {description.length}/200 characters. This helps AI classify emails automatically.
            </p>
          </div>

          {/* Color Field */}
          <div className="space-y-2">
            <Label htmlFor="category-color" className="text-sm font-medium text-gray-700">
              Color
            </Label>
            <div className="flex items-center gap-3">
              <input
                id="category-color"
                type="color"
                value={color}
                onChange={(e) => setColor(e.target.value)}
                disabled={loading}
                className="w-12 h-10 rounded border border-gray-300 cursor-pointer disabled:cursor-not-allowed"
              />
              <Input
                type="text"
                value={color}
                onChange={(e) => setColor(e.target.value)}
                placeholder="#3b82f6"
                disabled={loading}
                className="flex-1"
                pattern="^#[0-9A-Fa-f]{6}$"
              />
            </div>
          </div>

          {/* Actions */}
          <div className="flex gap-3 pt-4">
            <Button
              type="button"
              variant="outline"
              onClick={handleClose}
              disabled={loading}
              className="flex-1"
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={loading || !name.trim()}
              className="flex-1"
            >
              {loading ? (
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  Adding...
                </div>
              ) : (
                <div className="flex items-center gap-2">
                  <Plus className="w-4 h-4" />
                  Add Category
                </div>
              )}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}; 