import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatEmailDate(dateStr: string | undefined | null): string {
  if (!dateStr) return '-';
  // Try to parse ISO or RFC date
  const date = new Date(dateStr);
  if (isNaN(date.getTime())) return '-';
  // Format as 'MMM dd, yyyy'
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  });
}
