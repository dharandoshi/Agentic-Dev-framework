import { v4 as uuidv4 } from 'uuid';
import { Todo, TodoFilters, TodoSort, Priority, TodoStatus } from '@/types/todo';
import { StorageService } from './storage.service';

const TODOS_STORAGE_KEY = 'todos';

export class TodoService {
  private static instance: TodoService;
  private storageService: StorageService;
  private todos: Todo[] = [];

  private constructor() {
    this.storageService = StorageService.getInstance();
    this.loadTodos();
  }

  static getInstance(): TodoService {
    if (!TodoService.instance) {
      TodoService.instance = new TodoService();
    }
    return TodoService.instance;
  }

  private loadTodos(): void {
    const storedTodos = this.storageService.get<Todo[]>(TODOS_STORAGE_KEY);
    this.todos = storedTodos || [];
  }

  private saveTodos(): void {
    this.storageService.set(TODOS_STORAGE_KEY, this.todos);
  }

  private getNextOrder(): number {
    if (this.todos.length === 0) return 0;
    return Math.max(...this.todos.map(t => t.order)) + 1;
  }

  create(title: string, description?: string, priority: Priority = 'medium', category?: string, tags: string[] = [], dueDate?: string): Todo {
    const now = new Date().toISOString();
    const newTodo: Todo = {
      id: uuidv4(),
      title,
      description,
      status: 'active',
      priority,
      category,
      tags,
      dueDate,
      createdAt: now,
      updatedAt: now,
      order: this.getNextOrder(),
    };

    this.todos.push(newTodo);
    this.saveTodos();
    return newTodo;
  }

  update(id: string, updates: Partial<Todo>): Todo | null {
    const index = this.todos.findIndex(t => t.id === id);
    if (index === -1) return null;

    const updatedTodo: Todo = {
      ...this.todos[index],
      ...updates,
      id: this.todos[index].id,
      createdAt: this.todos[index].createdAt,
      updatedAt: new Date().toISOString(),
    };

    if (updates.status === 'completed' && this.todos[index].status !== 'completed') {
      updatedTodo.completedAt = new Date().toISOString();
    } else if (updates.status === 'active') {
      updatedTodo.completedAt = undefined;
    }

    this.todos[index] = updatedTodo;
    this.saveTodos();
    return updatedTodo;
  }

  delete(id: string): boolean {
    const index = this.todos.findIndex(t => t.id === id);
    if (index === -1) return false;

    this.todos.splice(index, 1);
    this.saveTodos();
    return true;
  }

  deleteMultiple(ids: string[]): number {
    const initialLength = this.todos.length;
    this.todos = this.todos.filter(t => !ids.includes(t.id));
    this.saveTodos();
    return initialLength - this.todos.length;
  }

  toggleStatus(id: string): Todo | null {
    const todo = this.todos.find(t => t.id === id);
    if (!todo) return null;

    const newStatus: TodoStatus = todo.status === 'active' ? 'completed' : 'active';
    return this.update(id, { status: newStatus });
  }

  toggleMultipleStatus(ids: string[], status: TodoStatus): number {
    let updated = 0;
    ids.forEach(id => {
      if (this.update(id, { status })) {
        updated++;
      }
    });
    return updated;
  }

  reorder(id: string, newOrder: number): void {
    const todoIndex = this.todos.findIndex(t => t.id === id);
    if (todoIndex === -1) return;

    const todo = this.todos[todoIndex];
    const oldOrder = todo.order;

    this.todos.forEach(t => {
      if (t.id === id) {
        t.order = newOrder;
      } else if (oldOrder < newOrder && t.order > oldOrder && t.order <= newOrder) {
        t.order--;
      } else if (oldOrder > newOrder && t.order < oldOrder && t.order >= newOrder) {
        t.order++;
      }
    });

    this.saveTodos();
  }

  clearCompleted(): number {
    const initialLength = this.todos.length;
    this.todos = this.todos.filter(t => t.status !== 'completed');
    this.saveTodos();
    return initialLength - this.todos.length;
  }

  getAll(filters?: TodoFilters, sort?: TodoSort): Todo[] {
    let filteredTodos = [...this.todos];

    if (filters) {
      if (filters.status && filters.status !== 'all') {
        filteredTodos = filteredTodos.filter(t => t.status === filters.status);
      }

      if (filters.priority && filters.priority !== 'all') {
        filteredTodos = filteredTodos.filter(t => t.priority === filters.priority);
      }

      if (filters.category) {
        filteredTodos = filteredTodos.filter(t => t.category === filters.category);
      }

      if (filters.tags && filters.tags.length > 0) {
        filteredTodos = filteredTodos.filter(t => 
          filters.tags!.some(tag => t.tags.includes(tag))
        );
      }

      if (filters.search) {
        const searchLower = filters.search.toLowerCase();
        filteredTodos = filteredTodos.filter(t => 
          t.title.toLowerCase().includes(searchLower) ||
          (t.description && t.description.toLowerCase().includes(searchLower))
        );
      }

      if (filters.dueDateFrom) {
        filteredTodos = filteredTodos.filter(t => 
          t.dueDate && t.dueDate >= filters.dueDateFrom!
        );
      }

      if (filters.dueDateTo) {
        filteredTodos = filteredTodos.filter(t => 
          t.dueDate && t.dueDate <= filters.dueDateTo!
        );
      }
    }

    if (sort) {
      filteredTodos.sort((a, b) => {
        let comparison = 0;

        switch (sort.by) {
          case 'title':
            comparison = a.title.localeCompare(b.title);
            break;
          case 'priority':
            const priorityOrder = { high: 0, medium: 1, low: 2 };
            comparison = priorityOrder[a.priority] - priorityOrder[b.priority];
            break;
          case 'dueDate':
            if (!a.dueDate && !b.dueDate) comparison = 0;
            else if (!a.dueDate) comparison = 1;
            else if (!b.dueDate) comparison = -1;
            else comparison = a.dueDate.localeCompare(b.dueDate);
            break;
          case 'createdAt':
            comparison = a.createdAt.localeCompare(b.createdAt);
            break;
          case 'order':
          default:
            comparison = a.order - b.order;
            break;
        }

        return sort.order === 'asc' ? comparison : -comparison;
      });
    }

    return filteredTodos;
  }

  getById(id: string): Todo | null {
    return this.todos.find(t => t.id === id) || null;
  }

  getCategories(): string[] {
    const categories = new Set<string>();
    this.todos.forEach(t => {
      if (t.category) categories.add(t.category);
    });
    return Array.from(categories).sort();
  }

  getTags(): string[] {
    const tags = new Set<string>();
    this.todos.forEach(t => {
      t.tags.forEach(tag => tags.add(tag));
    });
    return Array.from(tags).sort();
  }

  exportData(): string {
    return JSON.stringify(this.todos, null, 2);
  }

  importData(jsonData: string): { success: boolean; imported: number; error?: string } {
    try {
      const importedTodos = JSON.parse(jsonData) as Todo[];
      
      if (!Array.isArray(importedTodos)) {
        throw new Error('Invalid data format: expected an array of todos');
      }

      const validTodos = importedTodos.filter(t => 
        t.id && t.title && t.status && t.priority && t.createdAt
      );

      this.todos = [...this.todos, ...validTodos];
      this.saveTodos();

      return { success: true, imported: validTodos.length };
    } catch (error) {
      return { 
        success: false, 
        imported: 0, 
        error: error instanceof Error ? error.message : 'Import failed' 
      };
    }
  }
}