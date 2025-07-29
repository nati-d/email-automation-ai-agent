import { apiRequest } from '../axiosConfig';

export interface Category {
  id: string;
  entity_name: string;
  name?: string;
  color?: string;
  count?: number;
  [key: string]: any;
}

export interface CreateCategoryData {
  name: string;
}

export async function fetchCategories(): Promise<Category[]> {
  const response = await apiRequest<{ categories: Category[] }>({
    url: '/categories',
    method: 'GET',
  });
  console.log(response.data);
  return response.data.categories;
}

export async function createCategory(categoryData: CreateCategoryData): Promise<Category> {
  const response = await apiRequest<Category>({
    url: '/categories',
    method: 'POST',
    data: categoryData,
  });
  return response.data;
} 