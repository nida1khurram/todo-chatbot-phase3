// frontend/src/lib/utils/optimistic-updates.ts

// Types for optimistic updates
export interface OptimisticUpdate<T> {
  id: string;
  type: 'create' | 'update' | 'delete';
  data?: T;
  originalData?: T;
}

// Optimistic update helpers
export const optimisticUpdates = {
  // Create a new item optimistically
  createItem: <T extends { id: number }>(items: T[], newItem: T): T[] => {
    return [newItem, ...items];
  },

  // Update an item optimistically
  updateItem: <T extends { id: number }>(items: T[], updatedItem: T): T[] => {
    return items.map(item =>
      item.id === updatedItem.id ? { ...item, ...updatedItem } : item
    );
  },

  // Delete an item optimistically
  deleteItem: <T extends { id: number }>(items: T[], id: number): T[] => {
    return items.filter(item => item.id !== id);
  },

  // Toggle completion status optimistically
  toggleCompletion: <T extends { id: number; completed: boolean }>(items: T[], id: number): T[] => {
    return items.map(item =>
      item.id === id ? { ...item, completed: !item.completed } : item
    );
  }
};