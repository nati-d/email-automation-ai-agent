import { create } from "zustand";

export interface Category {
  id: string;
  name: string;
  color: string;
}

interface CategoryStore {
  categories: Category[];
  addCategory: (category: Category) => void;
  updateCategory: (id: string, category: Partial<Category>) => void;
  deleteCategory: (id: string) => void;
}

export const useCategoryStore = create<CategoryStore>((set) => ({
  categories: [],
  addCategory: (category) =>
    set((state) => ({
      categories: [...state.categories, category],
    })),
  updateCategory: (id, updatedCategory) =>
    set((state) => ({
      categories: state.categories.map((category) =>
        category.id === id ? { ...category, ...updatedCategory } : category
      ),
    })),
  deleteCategory: (id) =>
    set((state) => ({
      categories: state.categories.filter((category) => category.id !== id),
    })),
})); 