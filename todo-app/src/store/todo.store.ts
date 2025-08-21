import { create } from 'zustand';
import { Todo, TodoFilters, TodoSort, Priority, TodoStatistics } from '@/types/todo';
import { TodoService } from '@/services/todo.service';

interface TodoStore {
  todos: Todo[];
  filters: TodoFilters;
  sort: TodoSort;
  selectedTodos: string[];
  isLoading: boolean;
  
  // Actions
  loadTodos: () => void;
  createTodo: (title: string, description?: string, priority?: Priority, category?: string, tags?: string[], dueDate?: string) => void;
  updateTodo: (id: string, updates: Partial<Todo>) => void;
  deleteTodo: (id: string) => void;
  deleteMultipleTodos: (ids: string[]) => void;
  toggleTodoStatus: (id: string) => void;
  toggleMultipleTodosStatus: (ids: string[], status: 'active' | 'completed') => void;
  reorderTodo: (id: string, newOrder: number) => void;
  clearCompleted: () => void;
  
  // Filter and Sort
  setFilters: (filters: TodoFilters) => void;
  setSort: (sort: TodoSort) => void;
  
  // Selection
  toggleSelection: (id: string) => void;
  selectAll: () => void;
  clearSelection: () => void;
  
  // Data
  getFilteredTodos: () => Todo[];
  getStatistics: () => TodoStatistics;
  exportTodos: () => string;
  importTodos: (jsonData: string) => { success: boolean; imported: number; error?: string };
}

const todoService = TodoService.getInstance();

export const useTodoStore = create<TodoStore>((set, get) => ({
  todos: [],
  filters: { status: 'all' },
  sort: { by: 'order', order: 'asc' },
  selectedTodos: [],
  isLoading: false,

  loadTodos: () => {
    set({ isLoading: true });
    const todos = todoService.getAll();
    set({ todos, isLoading: false });
  },

  createTodo: (title, description, priority = 'medium', category, tags = [], dueDate) => {
    const newTodo = todoService.create(title, description, priority, category, tags, dueDate);
    set(state => ({ todos: [...state.todos, newTodo] }));
  },

  updateTodo: (id, updates) => {
    const updatedTodo = todoService.update(id, updates);
    if (updatedTodo) {
      set(state => ({
        todos: state.todos.map(t => t.id === id ? updatedTodo : t)
      }));
    }
  },

  deleteTodo: (id) => {
    if (todoService.delete(id)) {
      set(state => ({
        todos: state.todos.filter(t => t.id !== id),
        selectedTodos: state.selectedTodos.filter(sid => sid !== id)
      }));
    }
  },

  deleteMultipleTodos: (ids) => {
    const deleted = todoService.deleteMultiple(ids);
    if (deleted > 0) {
      set(state => ({
        todos: state.todos.filter(t => !ids.includes(t.id)),
        selectedTodos: state.selectedTodos.filter(sid => !ids.includes(sid))
      }));
    }
  },

  toggleTodoStatus: (id) => {
    const updatedTodo = todoService.toggleStatus(id);
    if (updatedTodo) {
      set(state => ({
        todos: state.todos.map(t => t.id === id ? updatedTodo : t)
      }));
    }
  },

  toggleMultipleTodosStatus: (ids, status) => {
    todoService.toggleMultipleStatus(ids, status);
    const todos = todoService.getAll();
    set({ todos });
  },

  reorderTodo: (id, newOrder) => {
    todoService.reorder(id, newOrder);
    const todos = todoService.getAll();
    set({ todos });
  },

  clearCompleted: () => {
    const cleared = todoService.clearCompleted();
    if (cleared > 0) {
      set(state => ({
        todos: state.todos.filter(t => t.status !== 'completed'),
        selectedTodos: state.selectedTodos.filter(id => {
          const todo = state.todos.find(t => t.id === id);
          return todo && todo.status !== 'completed';
        })
      }));
    }
  },

  setFilters: (filters) => {
    set({ filters });
  },

  setSort: (sort) => {
    set({ sort });
  },

  toggleSelection: (id) => {
    set(state => ({
      selectedTodos: state.selectedTodos.includes(id)
        ? state.selectedTodos.filter(sid => sid !== id)
        : [...state.selectedTodos, id]
    }));
  },

  selectAll: () => {
    const { todos } = get();
    set({ selectedTodos: todos.map(t => t.id) });
  },

  clearSelection: () => {
    set({ selectedTodos: [] });
  },

  getFilteredTodos: () => {
    const { filters, sort } = get();
    return todoService.getAll(filters, sort);
  },

  getStatistics: () => {
    const { todos } = get();
    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());

    const stats: TodoStatistics = {
      total: todos.length,
      active: todos.filter(t => t.status === 'active').length,
      completed: todos.filter(t => t.status === 'completed').length,
      overdue: todos.filter(t => 
        t.status === 'active' && 
        t.dueDate && 
        new Date(t.dueDate) < now
      ).length,
      completedToday: todos.filter(t => 
        t.completedAt && 
        new Date(t.completedAt) >= today
      ).length,
      byPriority: {
        high: todos.filter(t => t.priority === 'high').length,
        medium: todos.filter(t => t.priority === 'medium').length,
        low: todos.filter(t => t.priority === 'low').length,
      },
      byCategory: {},
    };

    todos.forEach(t => {
      if (t.category) {
        stats.byCategory[t.category] = (stats.byCategory[t.category] || 0) + 1;
      }
    });

    return stats;
  },

  exportTodos: () => {
    return todoService.exportData();
  },

  importTodos: (jsonData) => {
    const result = todoService.importData(jsonData);
    if (result.success) {
      const todos = todoService.getAll();
      set({ todos });
    }
    return result;
  },
}));