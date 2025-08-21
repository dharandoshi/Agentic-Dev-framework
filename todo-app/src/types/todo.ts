export type Priority = 'low' | 'medium' | 'high';
export type TodoStatus = 'active' | 'completed';

export interface Todo {
  id: string;
  title: string;
  description?: string;
  status: TodoStatus;
  priority: Priority;
  category?: string;
  tags: string[];
  dueDate?: string;
  completedAt?: string;
  createdAt: string;
  updatedAt: string;
  order: number;
}

export interface TodoFilters {
  status?: TodoStatus | 'all';
  priority?: Priority | 'all';
  category?: string;
  tags?: string[];
  search?: string;
  dueDateFrom?: string;
  dueDateTo?: string;
}

export type SortBy = 'createdAt' | 'dueDate' | 'priority' | 'title' | 'order';
export type SortOrder = 'asc' | 'desc';

export interface TodoSort {
  by: SortBy;
  order: SortOrder;
}

export interface TodoStatistics {
  total: number;
  active: number;
  completed: number;
  overdue: number;
  completedToday: number;
  byPriority: Record<Priority, number>;
  byCategory: Record<string, number>;
}