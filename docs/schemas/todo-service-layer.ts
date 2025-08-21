/**
 * Todo Application - Service Layer Architecture
 * 
 * This file defines all service classes for the frontend-only todo application.
 * These services handle business logic, data operations, and local storage interactions.
 */

import {
  TodoItem,
  TodoStatus,
  Priority,
  Category,
  UserPreferences,
  FilterOptions,
  SortOption,
  SortOrder,
  CreateTodoDto,
  UpdateTodoDto,
  ExportOptions,
  ImportResult,
  ValidationResult,
  TodoStatistics,
  STORAGE_KEYS,
  DEFAULT_CATEGORIES,
  DEFAULT_PREFERENCES
} from './todo-data-schema';

// ============================================
// Storage Service - Core storage abstraction
// ============================================

/**
 * Storage adapter interface for different storage backends
 */
interface IStorageAdapter {
  get<T>(key: string): Promise<T | null>;
  set<T>(key: string, value: T): Promise<void>;
  remove(key: string): Promise<void>;
  clear(): Promise<void>;
  getSize(): Promise<number>;
  isAvailable(): boolean;
}

/**
 * LocalStorage Adapter
 */
class LocalStorageAdapter implements IStorageAdapter {
  private readonly maxSize = 10 * 1024 * 1024; // 10MB

  isAvailable(): boolean {
    try {
      const test = '__localStorage_test__';
      localStorage.setItem(test, test);
      localStorage.removeItem(test);
      return true;
    } catch {
      return false;
    }
  }

  async get<T>(key: string): Promise<T | null> {
    try {
      const item = localStorage.getItem(key);
      if (!item) return null;
      return JSON.parse(item) as T;
    } catch (error) {
      console.error(`Failed to get ${key} from localStorage:`, error);
      return null;
    }
  }

  async set<T>(key: string, value: T): Promise<void> {
    try {
      const serialized = JSON.stringify(value);
      
      // Check size before saving
      if (serialized.length > this.maxSize) {
        throw new Error('Data exceeds maximum storage size');
      }
      
      localStorage.setItem(key, serialized);
    } catch (error) {
      if (error.name === 'QuotaExceededError') {
        throw new Error('Storage quota exceeded');
      }
      throw error;
    }
  }

  async remove(key: string): Promise<void> {
    localStorage.removeItem(key);
  }

  async clear(): Promise<void> {
    // Only clear app-specific keys
    Object.values(STORAGE_KEYS).forEach(key => {
      localStorage.removeItem(key);
    });
  }

  async getSize(): Promise<number> {
    let totalSize = 0;
    Object.values(STORAGE_KEYS).forEach(key => {
      const item = localStorage.getItem(key);
      if (item) {
        totalSize += item.length * 2; // UTF-16 encoding
      }
    });
    return totalSize;
  }
}

/**
 * IndexedDB Adapter (Fallback for large datasets)
 */
class IndexedDBAdapter implements IStorageAdapter {
  private dbName = 'TodoAppDB';
  private dbVersion = 1;
  private db: IDBDatabase | null = null;

  async init(): Promise<void> {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open(this.dbName, this.dbVersion);
      
      request.onerror = () => reject(request.error);
      request.onsuccess = () => {
        this.db = request.result;
        resolve();
      };
      
      request.onupgradeneeded = (event) => {
        const db = (event.target as IDBOpenDBRequest).result;
        if (!db.objectStoreNames.contains('data')) {
          db.createObjectStore('data', { keyPath: 'key' });
        }
      };
    });
  }

  isAvailable(): boolean {
    return 'indexedDB' in window;
  }

  async get<T>(key: string): Promise<T | null> {
    if (!this.db) await this.init();
    
    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(['data'], 'readonly');
      const store = transaction.objectStore('data');
      const request = store.get(key);
      
      request.onerror = () => reject(request.error);
      request.onsuccess = () => {
        const result = request.result;
        resolve(result ? result.value : null);
      };
    });
  }

  async set<T>(key: string, value: T): Promise<void> {
    if (!this.db) await this.init();
    
    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(['data'], 'readwrite');
      const store = transaction.objectStore('data');
      const request = store.put({ key, value });
      
      request.onerror = () => reject(request.error);
      request.onsuccess = () => resolve();
    });
  }

  async remove(key: string): Promise<void> {
    if (!this.db) await this.init();
    
    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(['data'], 'readwrite');
      const store = transaction.objectStore('data');
      const request = store.delete(key);
      
      request.onerror = () => reject(request.error);
      request.onsuccess = () => resolve();
    });
  }

  async clear(): Promise<void> {
    if (!this.db) await this.init();
    
    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(['data'], 'readwrite');
      const store = transaction.objectStore('data');
      const request = store.clear();
      
      request.onerror = () => reject(request.error);
      request.onsuccess = () => resolve();
    });
  }

  async getSize(): Promise<number> {
    // Estimate size using navigator.storage.estimate()
    if ('storage' in navigator && 'estimate' in navigator.storage) {
      const estimate = await navigator.storage.estimate();
      return estimate.usage || 0;
    }
    return 0;
  }
}

/**
 * Main Storage Service with compression and caching
 */
export class StorageService {
  private adapter: IStorageAdapter;
  private cache: Map<string, any> = new Map();
  private compressionThreshold = 1024; // Compress data larger than 1KB

  constructor() {
    // Try localStorage first, fallback to IndexedDB
    const localStorage = new LocalStorageAdapter();
    if (localStorage.isAvailable()) {
      this.adapter = localStorage;
    } else {
      this.adapter = new IndexedDBAdapter();
    }
  }

  /**
   * Get data from storage with caching
   */
  async get<T>(key: string): Promise<T | null> {
    // Check cache first
    if (this.cache.has(key)) {
      return this.cache.get(key) as T;
    }

    const data = await this.adapter.get<T>(key);
    
    if (data) {
      // Cache the data
      this.cache.set(key, data);
    }
    
    return data;
  }

  /**
   * Set data in storage with compression for large data
   */
  async set<T>(key: string, value: T): Promise<void> {
    // Update cache
    this.cache.set(key, value);
    
    // Compress if needed
    const serialized = JSON.stringify(value);
    const shouldCompress = serialized.length > this.compressionThreshold;
    
    if (shouldCompress) {
      // Use LZ-string or similar for compression
      // For now, we'll just store as-is
      await this.adapter.set(key, value);
    } else {
      await this.adapter.set(key, value);
    }
  }

  /**
   * Remove data from storage
   */
  async remove(key: string): Promise<void> {
    this.cache.delete(key);
    await this.adapter.remove(key);
  }

  /**
   * Clear all app data
   */
  async clear(): Promise<void> {
    this.cache.clear();
    await this.adapter.clear();
  }

  /**
   * Get storage size and quota information
   */
  async getStorageInfo(): Promise<{
    used: number;
    quota: number;
    percentage: number;
  }> {
    const used = await this.adapter.getSize();
    const quota = 10 * 1024 * 1024; // 10MB default
    const percentage = (used / quota) * 100;
    
    return { used, quota, percentage };
  }

  /**
   * Create a backup of all data
   */
  async createBackup(): Promise<string> {
    const backup: any = {};
    
    for (const [key, storageKey] of Object.entries(STORAGE_KEYS)) {
      backup[key] = await this.get(storageKey);
    }
    
    backup.timestamp = new Date().toISOString();
    backup.version = '1.0.0';
    
    return JSON.stringify(backup);
  }

  /**
   * Restore from backup
   */
  async restoreBackup(backupData: string): Promise<void> {
    try {
      const backup = JSON.parse(backupData);
      
      for (const [key, storageKey] of Object.entries(STORAGE_KEYS)) {
        if (backup[key]) {
          await this.set(storageKey, backup[key]);
        }
      }
    } catch (error) {
      throw new Error('Invalid backup data');
    }
  }
}

// ============================================
// Todo Service - Main business logic
// ============================================

export class TodoService {
  private storage: StorageService;
  private validationService: ValidationService;

  constructor() {
    this.storage = new StorageService();
    this.validationService = new ValidationService();
  }

  /**
   * Create a new todo
   */
  async create(dto: CreateTodoDto): Promise<TodoItem> {
    // Validate input
    const validation = this.validationService.validateCreateTodo(dto);
    if (!validation.valid) {
      throw new Error(`Validation failed: ${validation.errors[0].message}`);
    }

    // Create todo object
    const now = new Date().toISOString();
    const todo: TodoItem = {
      id: this.generateId(),
      title: dto.title,
      description: dto.description,
      status: TodoStatus.ACTIVE,
      priority: dto.priority || Priority.MEDIUM,
      category: dto.category || 'cat-general',
      tags: dto.tags || [],
      dueDate: dto.dueDate,
      dueTime: dto.dueTime,
      createdAt: now,
      updatedAt: now,
      order: Date.now(), // Use timestamp for initial order
      isDeleted: false
    };

    // Get existing todos
    const todos = await this.getAll();
    todos.push(todo);

    // Save to storage
    await this.storage.set(STORAGE_KEYS.TODOS, todos);

    return todo;
  }

  /**
   * Update an existing todo
   */
  async update(id: string, updates: UpdateTodoDto): Promise<TodoItem> {
    const todos = await this.getAll();
    const index = todos.findIndex(t => t.id === id);
    
    if (index === -1) {
      throw new Error('Todo not found');
    }

    // Validate updates
    const validation = this.validationService.validateUpdateTodo(updates);
    if (!validation.valid) {
      throw new Error(`Validation failed: ${validation.errors[0].message}`);
    }

    // Apply updates
    const updatedTodo = {
      ...todos[index],
      ...updates,
      updatedAt: new Date().toISOString()
    };

    // Handle completion
    if (updates.status === TodoStatus.COMPLETED && todos[index].status !== TodoStatus.COMPLETED) {
      updatedTodo.completedAt = new Date().toISOString();
    } else if (updates.status === TodoStatus.ACTIVE && todos[index].status === TodoStatus.COMPLETED) {
      delete updatedTodo.completedAt;
    }

    todos[index] = updatedTodo;
    await this.storage.set(STORAGE_KEYS.TODOS, todos);

    return updatedTodo;
  }

  /**
   * Delete a todo (soft delete with undo capability)
   */
  async delete(id: string, permanent: boolean = false): Promise<void> {
    const todos = await this.getAll();
    const index = todos.findIndex(t => t.id === id);
    
    if (index === -1) {
      throw new Error('Todo not found');
    }

    if (permanent) {
      // Permanent deletion
      todos.splice(index, 1);
    } else {
      // Soft delete
      todos[index].isDeleted = true;
      todos[index].deletedAt = new Date().toISOString();
    }

    await this.storage.set(STORAGE_KEYS.TODOS, todos);
  }

  /**
   * Restore a soft-deleted todo
   */
  async restore(id: string): Promise<TodoItem> {
    const todos = await this.getAll();
    const todo = todos.find(t => t.id === id);
    
    if (!todo) {
      throw new Error('Todo not found');
    }

    todo.isDeleted = false;
    delete todo.deletedAt;
    todo.updatedAt = new Date().toISOString();

    await this.storage.set(STORAGE_KEYS.TODOS, todos);
    return todo;
  }

  /**
   * Toggle todo completion status
   */
  async toggleComplete(id: string): Promise<TodoItem> {
    const todo = await this.getById(id);
    if (!todo) {
      throw new Error('Todo not found');
    }

    const newStatus = todo.status === TodoStatus.ACTIVE 
      ? TodoStatus.COMPLETED 
      : TodoStatus.ACTIVE;

    return this.update(id, { status: newStatus });
  }

  /**
   * Bulk update multiple todos
   */
  async bulkUpdate(ids: string[], updates: UpdateTodoDto): Promise<TodoItem[]> {
    const todos = await this.getAll();
    const updatedTodos: TodoItem[] = [];
    const now = new Date().toISOString();

    todos.forEach(todo => {
      if (ids.includes(todo.id)) {
        Object.assign(todo, updates, { updatedAt: now });
        
        // Handle completion status change
        if (updates.status === TodoStatus.COMPLETED && todo.status !== TodoStatus.COMPLETED) {
          todo.completedAt = now;
        } else if (updates.status === TodoStatus.ACTIVE && todo.status === TodoStatus.COMPLETED) {
          delete todo.completedAt;
        }
        
        updatedTodos.push(todo);
      }
    });

    await this.storage.set(STORAGE_KEYS.TODOS, todos);
    return updatedTodos;
  }

  /**
   * Bulk delete multiple todos
   */
  async bulkDelete(ids: string[], permanent: boolean = false): Promise<void> {
    const todos = await this.getAll();
    
    if (permanent) {
      const filtered = todos.filter(t => !ids.includes(t.id));
      await this.storage.set(STORAGE_KEYS.TODOS, filtered);
    } else {
      const now = new Date().toISOString();
      todos.forEach(todo => {
        if (ids.includes(todo.id)) {
          todo.isDeleted = true;
          todo.deletedAt = now;
        }
      });
      await this.storage.set(STORAGE_KEYS.TODOS, todos);
    }
  }

  /**
   * Get all todos (excluding soft-deleted by default)
   */
  async getAll(includeDeleted: boolean = false): Promise<TodoItem[]> {
    const todos = await this.storage.get<TodoItem[]>(STORAGE_KEYS.TODOS) || [];
    
    if (includeDeleted) {
      return todos;
    }
    
    return todos.filter(t => !t.isDeleted);
  }

  /**
   * Get todo by ID
   */
  async getById(id: string): Promise<TodoItem | null> {
    const todos = await this.getAll(true);
    return todos.find(t => t.id === id) || null;
  }

  /**
   * Reorder todos (for drag and drop)
   */
  async reorder(orderedIds: string[]): Promise<void> {
    const todos = await this.getAll();
    
    // Create a map for quick lookup
    const todoMap = new Map(todos.map(t => [t.id, t]));
    
    // Update order based on new positions
    orderedIds.forEach((id, index) => {
      const todo = todoMap.get(id);
      if (todo) {
        todo.order = index;
        todo.updatedAt = new Date().toISOString();
      }
    });

    await this.storage.set(STORAGE_KEYS.TODOS, Array.from(todoMap.values()));
  }

  /**
   * Clean up old completed todos
   */
  async cleanup(daysOld: number = 30): Promise<number> {
    const todos = await this.getAll(true);
    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - daysOld);
    
    const filtered = todos.filter(todo => {
      if (todo.status === TodoStatus.COMPLETED && todo.completedAt) {
        const completedDate = new Date(todo.completedAt);
        return completedDate > cutoffDate;
      }
      return true;
    });

    const deletedCount = todos.length - filtered.length;
    await this.storage.set(STORAGE_KEYS.TODOS, filtered);
    
    return deletedCount;
  }

  /**
   * Generate unique ID
   */
  private generateId(): string {
    return `todo-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }
}

// ============================================
// Search Service - In-memory search operations
// ============================================

export class SearchService {
  private searchIndex: Map<string, Set<string>> = new Map();

  /**
   * Build search index for todos
   */
  buildIndex(todos: TodoItem[]): void {
    this.searchIndex.clear();
    
    todos.forEach(todo => {
      // Index title words
      this.indexText(todo.title, todo.id);
      
      // Index description words
      if (todo.description) {
        this.indexText(todo.description, todo.id);
      }
      
      // Index tags
      todo.tags.forEach(tag => {
        this.indexText(tag, todo.id);
      });
    });
  }

  /**
   * Index text for a todo
   */
  private indexText(text: string, todoId: string): void {
    const words = text.toLowerCase().split(/\s+/);
    
    words.forEach(word => {
      if (!this.searchIndex.has(word)) {
        this.searchIndex.set(word, new Set());
      }
      this.searchIndex.get(word)!.add(todoId);
    });
  }

  /**
   * Search todos by query
   */
  search(todos: TodoItem[], query: string): TodoItem[] {
    if (!query || query.trim().length < 2) {
      return todos;
    }

    const searchTerms = query.toLowerCase().split(/\s+/);
    const matchingIds = new Set<string>();

    // Find todos that match all search terms
    searchTerms.forEach(term => {
      todos.forEach(todo => {
        if (this.todoMatchesTerm(todo, term)) {
          matchingIds.add(todo.id);
        }
      });
    });

    return todos.filter(todo => matchingIds.has(todo.id));
  }

  /**
   * Check if a todo matches a search term
   */
  private todoMatchesTerm(todo: TodoItem, term: string): boolean {
    const searchableText = [
      todo.title,
      todo.description || '',
      todo.category,
      ...todo.tags
    ].join(' ').toLowerCase();

    return searchableText.includes(term);
  }

  /**
   * Fuzzy search implementation
   */
  fuzzySearch(todos: TodoItem[], query: string, threshold: number = 0.6): TodoItem[] {
    if (!query || query.trim().length < 2) {
      return todos;
    }

    const results: Array<{ todo: TodoItem; score: number }> = [];

    todos.forEach(todo => {
      const score = this.calculateFuzzyScore(todo, query.toLowerCase());
      if (score >= threshold) {
        results.push({ todo, score });
      }
    });

    // Sort by score descending
    results.sort((a, b) => b.score - a.score);

    return results.map(r => r.todo);
  }

  /**
   * Calculate fuzzy match score
   */
  private calculateFuzzyScore(todo: TodoItem, query: string): number {
    const searchableText = [
      todo.title,
      todo.description || ''
    ].join(' ').toLowerCase();

    // Simple Levenshtein distance-based scoring
    // In production, use a proper fuzzy search library
    let score = 0;
    let lastIndex = -1;

    for (const char of query) {
      const index = searchableText.indexOf(char, lastIndex + 1);
      if (index > -1) {
        score += 1 / (index - lastIndex);
        lastIndex = index;
      }
    }

    return score / query.length;
  }

  /**
   * Highlight search matches in text
   */
  highlightMatches(text: string, query: string): string {
    if (!query) return text;

    const terms = query.split(/\s+/).filter(t => t.length > 0);
    let highlighted = text;

    terms.forEach(term => {
      const regex = new RegExp(`(${term})`, 'gi');
      highlighted = highlighted.replace(regex, '<mark>$1</mark>');
    });

    return highlighted;
  }

  /**
   * Get search suggestions based on partial input
   */
  getSuggestions(todos: TodoItem[], partial: string, limit: number = 5): string[] {
    const suggestions = new Set<string>();
    const lowerPartial = partial.toLowerCase();

    todos.forEach(todo => {
      // Check title words
      const words = todo.title.split(/\s+/);
      words.forEach(word => {
        if (word.toLowerCase().startsWith(lowerPartial)) {
          suggestions.add(word);
        }
      });

      // Check tags
      todo.tags.forEach(tag => {
        if (tag.toLowerCase().startsWith(lowerPartial)) {
          suggestions.add(tag);
        }
      });
    });

    return Array.from(suggestions).slice(0, limit);
  }
}

// ============================================
// Filter Service - Client-side filtering
// ============================================

export class FilterService {
  /**
   * Apply multiple filters to todos
   */
  applyFilters(todos: TodoItem[], filters: FilterOptions): TodoItem[] {
    let filtered = [...todos];

    // Status filter
    if (filters.status && filters.status !== 'all') {
      filtered = filtered.filter(todo => todo.status === filters.status);
    }

    // Priority filter
    if (filters.priorities && filters.priorities.length > 0) {
      filtered = filtered.filter(todo => 
        filters.priorities!.includes(todo.priority)
      );
    }

    // Category filter
    if (filters.categories && filters.categories.length > 0) {
      filtered = filtered.filter(todo => 
        filters.categories!.includes(todo.category)
      );
    }

    // Tags filter
    if (filters.tags && filters.tags.length > 0) {
      filtered = filtered.filter(todo => 
        filters.tags!.some(tag => todo.tags.includes(tag))
      );
    }

    // Date range filter
    if (filters.dateRange) {
      const startDate = new Date(filters.dateRange.start);
      const endDate = new Date(filters.dateRange.end);
      
      filtered = filtered.filter(todo => {
        if (!todo.dueDate) {
          return filters.hasNoDueDate === true;
        }
        
        const dueDate = new Date(todo.dueDate);
        return dueDate >= startDate && dueDate <= endDate;
      });
    }

    // Overdue filter
    const now = new Date();
    filtered = filtered.filter(todo => {
      if (!todo.dueDate) return true;
      
      const dueDate = new Date(todo.dueDate);
      const isOverdue = dueDate < now && todo.status === TodoStatus.ACTIVE;
      
      // Add visual indicator for overdue items
      if (isOverdue) {
        (todo as any).isOverdue = true;
      }
      
      return true;
    });

    return filtered;
  }

  /**
   * Sort todos by specified criteria
   */
  sortTodos(todos: TodoItem[], sortBy: SortOption, order: SortOrder = SortOrder.ASC): TodoItem[] {
    const sorted = [...todos];

    sorted.sort((a, b) => {
      let comparison = 0;

      switch (sortBy) {
        case SortOption.CREATED_AT:
          comparison = new Date(a.createdAt).getTime() - new Date(b.createdAt).getTime();
          break;

        case SortOption.UPDATED_AT:
          comparison = new Date(a.updatedAt).getTime() - new Date(b.updatedAt).getTime();
          break;

        case SortOption.DUE_DATE:
          // Todos without due dates go to the end
          if (!a.dueDate && !b.dueDate) return 0;
          if (!a.dueDate) return 1;
          if (!b.dueDate) return -1;
          comparison = new Date(a.dueDate).getTime() - new Date(b.dueDate).getTime();
          break;

        case SortOption.PRIORITY:
          const priorityOrder = { high: 0, medium: 1, low: 2 };
          comparison = priorityOrder[a.priority] - priorityOrder[b.priority];
          break;

        case SortOption.TITLE:
          comparison = a.title.localeCompare(b.title);
          break;

        case SortOption.CATEGORY:
          comparison = a.category.localeCompare(b.category);
          break;

        case SortOption.STATUS:
          comparison = a.status.localeCompare(b.status);
          break;

        case SortOption.CUSTOM:
          comparison = a.order - b.order;
          break;
      }

      return order === SortOrder.DESC ? -comparison : comparison;
    });

    return sorted;
  }

  /**
   * Group todos by category
   */
  groupByCategory(todos: TodoItem[]): Map<string, TodoItem[]> {
    const groups = new Map<string, TodoItem[]>();

    todos.forEach(todo => {
      if (!groups.has(todo.category)) {
        groups.set(todo.category, []);
      }
      groups.get(todo.category)!.push(todo);
    });

    return groups;
  }

  /**
   * Group todos by priority
   */
  groupByPriority(todos: TodoItem[]): Map<Priority, TodoItem[]> {
    const groups = new Map<Priority, TodoItem[]>();

    // Initialize all priority levels
    Object.values(Priority).forEach(priority => {
      groups.set(priority, []);
    });

    todos.forEach(todo => {
      groups.get(todo.priority)!.push(todo);
    });

    return groups;
  }

  /**
   * Group todos by date
   */
  groupByDate(todos: TodoItem[]): Map<string, TodoItem[]> {
    const groups = new Map<string, TodoItem[]>();
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);
    
    const thisWeek = new Date(today);
    thisWeek.setDate(thisWeek.getDate() + 7);

    todos.forEach(todo => {
      let group = 'No Date';
      
      if (todo.dueDate) {
        const dueDate = new Date(todo.dueDate);
        dueDate.setHours(0, 0, 0, 0);
        
        if (dueDate < today) {
          group = 'Overdue';
        } else if (dueDate.getTime() === today.getTime()) {
          group = 'Today';
        } else if (dueDate.getTime() === tomorrow.getTime()) {
          group = 'Tomorrow';
        } else if (dueDate < thisWeek) {
          group = 'This Week';
        } else {
          group = 'Later';
        }
      }

      if (!groups.has(group)) {
        groups.set(group, []);
      }
      groups.get(group)!.push(todo);
    });

    return groups;
  }
}

// ============================================
// Export Service - Data export/import
// ============================================

export class ExportService {
  /**
   * Export todos as JSON
   */
  exportAsJSON(todos: TodoItem[], options?: ExportOptions): string {
    let exportData = todos;

    if (options) {
      // Filter by completion status
      if (!options.includeCompleted) {
        exportData = exportData.filter(t => t.status !== TodoStatus.COMPLETED);
      }

      // Filter by deleted status
      if (!options.includeDeleted) {
        exportData = exportData.filter(t => !t.isDeleted);
      }

      // Filter by date range
      if (options.dateRange) {
        const start = new Date(options.dateRange.start);
        const end = new Date(options.dateRange.end);
        
        exportData = exportData.filter(todo => {
          const created = new Date(todo.createdAt);
          return created >= start && created <= end;
        });
      }

      // Filter by categories
      if (options.categories && options.categories.length > 0) {
        exportData = exportData.filter(todo => 
          options.categories!.includes(todo.category)
        );
      }
    }

    return JSON.stringify({
      version: '1.0.0',
      exportDate: new Date().toISOString(),
      todos: exportData
    }, null, 2);
  }

  /**
   * Export todos as CSV
   */
  exportAsCSV(todos: TodoItem[]): string {
    const headers = [
      'Title',
      'Description',
      'Status',
      'Priority',
      'Category',
      'Tags',
      'Due Date',
      'Created At',
      'Completed At'
    ];

    const rows = todos.map(todo => [
      this.escapeCSV(todo.title),
      this.escapeCSV(todo.description || ''),
      todo.status,
      todo.priority,
      todo.category,
      todo.tags.join(';'),
      todo.dueDate || '',
      todo.createdAt,
      todo.completedAt || ''
    ]);

    const csv = [
      headers.join(','),
      ...rows.map(row => row.join(','))
    ].join('\n');

    return csv;
  }

  /**
   * Export todos as Markdown
   */
  exportAsMarkdown(todos: TodoItem[]): string {
    const grouped = this.groupTodosByStatus(todos);
    let markdown = '# Todo List Export\n\n';
    markdown += `*Exported on ${new Date().toLocaleDateString()}*\n\n`;

    // Active todos
    if (grouped.active.length > 0) {
      markdown += '## Active Tasks\n\n';
      grouped.active.forEach(todo => {
        markdown += this.todoToMarkdown(todo);
      });
    }

    // Completed todos
    if (grouped.completed.length > 0) {
      markdown += '\n## Completed Tasks\n\n';
      grouped.completed.forEach(todo => {
        markdown += this.todoToMarkdown(todo, true);
      });
    }

    return markdown;
  }

  /**
   * Convert todo to markdown format
   */
  private todoToMarkdown(todo: TodoItem, completed: boolean = false): string {
    const checkbox = completed ? '[x]' : '[ ]';
    const priority = {
      high: '🔴',
      medium: '🟠',
      low: '🟢'
    }[todo.priority];

    let md = `- ${checkbox} **${todo.title}** ${priority}\n`;
    
    if (todo.description) {
      md += `  - ${todo.description}\n`;
    }
    
    if (todo.dueDate) {
      md += `  - Due: ${new Date(todo.dueDate).toLocaleDateString()}\n`;
    }
    
    if (todo.tags.length > 0) {
      md += `  - Tags: ${todo.tags.map(t => `\`${t}\``).join(', ')}\n`;
    }
    
    md += '\n';
    return md;
  }

  /**
   * Import todos from JSON
   */
  async importFromJSON(jsonString: string): Promise<ImportResult> {
    const result: ImportResult = {
      success: false,
      imported: 0,
      failed: 0,
      errors: []
    };

    try {
      const data = JSON.parse(jsonString);
      
      if (!data.todos || !Array.isArray(data.todos)) {
        throw new Error('Invalid JSON format: missing todos array');
      }

      const validationService = new ValidationService();
      const importedTodos: TodoItem[] = [];

      data.todos.forEach((item: any, index: number) => {
        try {
          // Validate each todo
          const validation = validationService.validateImportedTodo(item);
          
          if (validation.valid) {
            // Generate new ID to avoid conflicts
            item.id = `todo-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
            importedTodos.push(item as TodoItem);
            result.imported++;
          } else {
            result.failed++;
            result.errors.push({
              row: index + 1,
              field: validation.errors[0].field,
              message: validation.errors[0].message
            });
          }
        } catch (error) {
          result.failed++;
          result.errors.push({
            row: index + 1,
            field: 'general',
            message: error.message
          });
        }
      });

      if (importedTodos.length > 0) {
        // Save imported todos
        const storage = new StorageService();
        const existingTodos = await storage.get<TodoItem[]>(STORAGE_KEYS.TODOS) || [];
        const mergedTodos = [...existingTodos, ...importedTodos];
        await storage.set(STORAGE_KEYS.TODOS, mergedTodos);
        
        result.success = true;
      }
    } catch (error) {
      result.errors.push({
        row: 0,
        field: 'general',
        message: `Failed to parse JSON: ${error.message}`
      });
    }

    return result;
  }

  /**
   * Import todos from CSV
   */
  async importFromCSV(csvString: string): Promise<ImportResult> {
    const result: ImportResult = {
      success: false,
      imported: 0,
      failed: 0,
      errors: []
    };

    try {
      const lines = csvString.split('\n');
      const headers = lines[0].split(',').map(h => h.trim());
      
      const todos: TodoItem[] = [];
      
      for (let i = 1; i < lines.length; i++) {
        if (!lines[i].trim()) continue;
        
        try {
          const values = this.parseCSVLine(lines[i]);
          const todo = this.csvRowToTodo(headers, values);
          todos.push(todo);
          result.imported++;
        } catch (error) {
          result.failed++;
          result.errors.push({
            row: i + 1,
            field: 'general',
            message: error.message
          });
        }
      }

      if (todos.length > 0) {
        const storage = new StorageService();
        const existingTodos = await storage.get<TodoItem[]>(STORAGE_KEYS.TODOS) || [];
        const mergedTodos = [...existingTodos, ...todos];
        await storage.set(STORAGE_KEYS.TODOS, mergedTodos);
        
        result.success = true;
      }
    } catch (error) {
      result.errors.push({
        row: 0,
        field: 'general',
        message: `Failed to parse CSV: ${error.message}`
      });
    }

    return result;
  }

  /**
   * Parse CSV line handling quoted values
   */
  private parseCSVLine(line: string): string[] {
    const values: string[] = [];
    let current = '';
    let inQuotes = false;
    
    for (let i = 0; i < line.length; i++) {
      const char = line[i];
      
      if (char === '"') {
        inQuotes = !inQuotes;
      } else if (char === ',' && !inQuotes) {
        values.push(current.trim());
        current = '';
      } else {
        current += char;
      }
    }
    
    values.push(current.trim());
    return values;
  }

  /**
   * Convert CSV row to todo
   */
  private csvRowToTodo(headers: string[], values: string[]): TodoItem {
    const now = new Date().toISOString();
    const todo: any = {
      id: `todo-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      createdAt: now,
      updatedAt: now,
      status: TodoStatus.ACTIVE,
      priority: Priority.MEDIUM,
      category: 'cat-general',
      tags: [],
      order: Date.now()
    };

    headers.forEach((header, index) => {
      const value = values[index];
      if (!value) return;

      switch (header.toLowerCase()) {
        case 'title':
          todo.title = value;
          break;
        case 'description':
          todo.description = value;
          break;
        case 'status':
          todo.status = value.toLowerCase() as TodoStatus;
          break;
        case 'priority':
          todo.priority = value.toLowerCase() as Priority;
          break;
        case 'category':
          todo.category = value;
          break;
        case 'tags':
          todo.tags = value.split(';').map(t => t.trim()).filter(t => t);
          break;
        case 'due date':
        case 'duedate':
          todo.dueDate = value;
          break;
      }
    });

    if (!todo.title) {
      throw new Error('Title is required');
    }

    return todo as TodoItem;
  }

  /**
   * Escape CSV special characters
   */
  private escapeCSV(value: string): string {
    if (value.includes(',') || value.includes('"') || value.includes('\n')) {
      return `"${value.replace(/"/g, '""')}"`;
    }
    return value;
  }

  /**
   * Group todos by status
   */
  private groupTodosByStatus(todos: TodoItem[]): {
    active: TodoItem[];
    completed: TodoItem[];
  } {
    return {
      active: todos.filter(t => t.status === TodoStatus.ACTIVE),
      completed: todos.filter(t => t.status === TodoStatus.COMPLETED)
    };
  }

  /**
   * Generate PDF export (requires additional library)
   */
  async exportAsPDF(todos: TodoItem[]): Promise<Blob> {
    // This would require a library like jsPDF or pdfmake
    // For now, return a placeholder
    throw new Error('PDF export requires additional library implementation');
  }
}

// ============================================
// Statistics Service - Analytics and metrics
// ============================================

export class StatisticsService {
  /**
   * Calculate todo statistics
   */
  calculateStatistics(todos: TodoItem[]): TodoStatistics {
    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const weekAgo = new Date(today);
    weekAgo.setDate(weekAgo.getDate() - 7);
    const monthAgo = new Date(today);
    monthAgo.setMonth(monthAgo.getMonth() - 1);

    // Filter out deleted todos
    const activeTodos = todos.filter(t => !t.isDeleted);

    // Basic counts
    const totalTodos = activeTodos.length;
    const completedTodos = activeTodos.filter(t => t.status === TodoStatus.COMPLETED).length;
    const activeTodosCount = totalTodos - completedTodos;
    
    // Overdue todos
    const overdueTodos = activeTodos.filter(todo => {
      if (!todo.dueDate || todo.status === TodoStatus.COMPLETED) return false;
      return new Date(todo.dueDate) < now;
    }).length;

    // Completed today
    const completedToday = activeTodos.filter(todo => {
      if (!todo.completedAt) return false;
      const completedDate = new Date(todo.completedAt);
      return completedDate >= today;
    }).length;

    // Completed this week
    const completedThisWeek = activeTodos.filter(todo => {
      if (!todo.completedAt) return false;
      const completedDate = new Date(todo.completedAt);
      return completedDate >= weekAgo;
    }).length;

    // Completed this month
    const completedThisMonth = activeTodos.filter(todo => {
      if (!todo.completedAt) return false;
      const completedDate = new Date(todo.completedAt);
      return completedDate >= monthAgo;
    }).length;

    // Completion rate
    const completionRate = totalTodos > 0 
      ? Math.round((completedTodos / totalTodos) * 100) 
      : 0;

    // Priority distribution
    const byPriority = {
      high: activeTodos.filter(t => t.priority === Priority.HIGH).length,
      medium: activeTodos.filter(t => t.priority === Priority.MEDIUM).length,
      low: activeTodos.filter(t => t.priority === Priority.LOW).length
    };

    // Category distribution
    const byCategory: CategoryDistribution = {};
    activeTodos.forEach(todo => {
      byCategory[todo.category] = (byCategory[todo.category] || 0) + 1;
    });

    // Calculate average completion time
    const completionTimes: number[] = [];
    activeTodos.forEach(todo => {
      if (todo.completedAt && todo.createdAt) {
        const created = new Date(todo.createdAt).getTime();
        const completed = new Date(todo.completedAt).getTime();
        const hours = (completed - created) / (1000 * 60 * 60);
        completionTimes.push(hours);
      }
    });

    const averageCompletionTime = completionTimes.length > 0
      ? Math.round(completionTimes.reduce((a, b) => a + b, 0) / completionTimes.length)
      : 0;

    // Calculate daily completions for the last 7 days
    const dailyCompletions: DailyCompletion[] = [];
    for (let i = 6; i >= 0; i--) {
      const date = new Date(today);
      date.setDate(date.getDate() - i);
      const dateStr = date.toISOString().split('T')[0];
      
      const completed = activeTodos.filter(todo => {
        if (!todo.completedAt) return false;
        return todo.completedAt.startsWith(dateStr);
      }).length;

      const created = activeTodos.filter(todo => {
        return todo.createdAt.startsWith(dateStr);
      }).length;

      dailyCompletions.push({ date: dateStr, completed, created });
    }

    // Calculate streaks
    const { currentStreak, longestStreak } = this.calculateStreaks(activeTodos);

    // Last activity date
    const lastActivityDate = this.getLastActivityDate(activeTodos);

    return {
      totalTodos,
      activeTodos: activeTodosCount,
      completedTodos,
      overdueTodos,
      completedToday,
      completedThisWeek,
      completedThisMonth,
      completionRate,
      byPriority,
      byCategory,
      averageCompletionTime,
      dailyCompletions,
      currentStreak,
      longestStreak,
      lastActivityDate
    };
  }

  /**
   * Calculate completion streaks
   */
  private calculateStreaks(todos: TodoItem[]): {
    currentStreak: number;
    longestStreak: number;
  } {
    const completionDates = new Set<string>();
    
    todos.forEach(todo => {
      if (todo.completedAt) {
        const dateStr = todo.completedAt.split('T')[0];
        completionDates.add(dateStr);
      }
    });

    const sortedDates = Array.from(completionDates).sort();
    
    let currentStreak = 0;
    let longestStreak = 0;
    let tempStreak = 0;
    let lastDate: Date | null = null;

    sortedDates.forEach(dateStr => {
      const date = new Date(dateStr);
      
      if (lastDate) {
        const dayDiff = Math.floor((date.getTime() - lastDate.getTime()) / (1000 * 60 * 60 * 24));
        
        if (dayDiff === 1) {
          tempStreak++;
        } else {
          longestStreak = Math.max(longestStreak, tempStreak);
          tempStreak = 1;
        }
      } else {
        tempStreak = 1;
      }
      
      lastDate = date;
    });

    // Check if current streak is ongoing
    const today = new Date().toISOString().split('T')[0];
    const yesterday = new Date();
    yesterday.setDate(yesterday.getDate() - 1);
    const yesterdayStr = yesterday.toISOString().split('T')[0];

    if (completionDates.has(today) || completionDates.has(yesterdayStr)) {
      currentStreak = tempStreak;
    }

    longestStreak = Math.max(longestStreak, tempStreak);

    return { currentStreak, longestStreak };
  }

  /**
   * Get last activity date
   */
  private getLastActivityDate(todos: TodoItem[]): string {
    let lastDate = new Date(0);

    todos.forEach(todo => {
      const updated = new Date(todo.updatedAt);
      if (updated > lastDate) {
        lastDate = updated;
      }
    });

    return lastDate.toISOString();
  }
}

// ============================================
// Validation Service - Input validation
// ============================================

export class ValidationService {
  /**
   * Validate create todo DTO
   */
  validateCreateTodo(dto: CreateTodoDto): ValidationResult {
    const errors: ValidationError[] = [];

    // Title validation
    if (!dto.title || dto.title.trim().length === 0) {
      errors.push({
        field: 'title',
        message: 'Title is required',
        code: 'REQUIRED'
      });
    } else if (dto.title.length > 200) {
      errors.push({
        field: 'title',
        message: 'Title must be less than 200 characters',
        code: 'MAX_LENGTH'
      });
    }

    // Description validation
    if (dto.description && dto.description.length > 1000) {
      errors.push({
        field: 'description',
        message: 'Description must be less than 1000 characters',
        code: 'MAX_LENGTH'
      });
    }

    // Tags validation
    if (dto.tags) {
      if (dto.tags.length > 3) {
        errors.push({
          field: 'tags',
          message: 'Maximum 3 tags allowed',
          code: 'MAX_COUNT'
        });
      }

      dto.tags.forEach(tag => {
        if (tag.length > 20) {
          errors.push({
            field: 'tags',
            message: 'Tag must be less than 20 characters',
            code: 'MAX_LENGTH'
          });
        }
      });
    }

    // Due date validation
    if (dto.dueDate) {
      try {
        const date = new Date(dto.dueDate);
        if (isNaN(date.getTime())) {
          errors.push({
            field: 'dueDate',
            message: 'Invalid date format',
            code: 'INVALID_FORMAT'
          });
        }
      } catch {
        errors.push({
          field: 'dueDate',
          message: 'Invalid date format',
          code: 'INVALID_FORMAT'
        });
      }
    }

    return {
      valid: errors.length === 0,
      errors
    };
  }

  /**
   * Validate update todo DTO
   */
  validateUpdateTodo(dto: UpdateTodoDto): ValidationResult {
    const errors: ValidationError[] = [];

    // Title validation
    if (dto.title !== undefined) {
      if (!dto.title || dto.title.trim().length === 0) {
        errors.push({
          field: 'title',
          message: 'Title cannot be empty',
          code: 'REQUIRED'
        });
      } else if (dto.title.length > 200) {
        errors.push({
          field: 'title',
          message: 'Title must be less than 200 characters',
          code: 'MAX_LENGTH'
        });
      }
    }

    // Description validation
    if (dto.description !== undefined && dto.description.length > 1000) {
      errors.push({
        field: 'description',
        message: 'Description must be less than 1000 characters',
        code: 'MAX_LENGTH'
      });
    }

    // Tags validation
    if (dto.tags) {
      if (dto.tags.length > 3) {
        errors.push({
          field: 'tags',
          message: 'Maximum 3 tags allowed',
          code: 'MAX_COUNT'
        });
      }
    }

    return {
      valid: errors.length === 0,
      errors
    };
  }

  /**
   * Validate imported todo
   */
  validateImportedTodo(todo: any): ValidationResult {
    const errors: ValidationError[] = [];

    if (!todo.title) {
      errors.push({
        field: 'title',
        message: 'Title is required',
        code: 'REQUIRED'
      });
    }

    if (!todo.status) {
      todo.status = TodoStatus.ACTIVE;
    }

    if (!todo.priority) {
      todo.priority = Priority.MEDIUM;
    }

    if (!todo.category) {
      todo.category = 'cat-general';
    }

    if (!todo.tags) {
      todo.tags = [];
    }

    if (!todo.createdAt) {
      todo.createdAt = new Date().toISOString();
    }

    if (!todo.updatedAt) {
      todo.updatedAt = new Date().toISOString();
    }

    return {
      valid: errors.length === 0,
      errors
    };
  }

  /**
   * Sanitize user input to prevent XSS
   */
  sanitizeInput(input: string): string {
    // Remove any HTML tags
    return input.replace(/<[^>]*>/g, '');
  }
}

// ============================================
// Category Service - Category management
// ============================================

export class CategoryService {
  private storage: StorageService;

  constructor() {
    this.storage = new StorageService();
  }

  /**
   * Get all categories
   */
  async getAll(): Promise<Category[]> {
    const categories = await this.storage.get<Category[]>(STORAGE_KEYS.CATEGORIES);
    return categories || DEFAULT_CATEGORIES;
  }

  /**
   * Create a new category
   */
  async create(name: string, color: string): Promise<Category> {
    const categories = await this.getAll();
    
    // Check if category already exists
    if (categories.some(c => c.name.toLowerCase() === name.toLowerCase())) {
      throw new Error('Category already exists');
    }

    // Check max categories limit
    if (categories.filter(c => !c.isDefault).length >= 14) {
      throw new Error('Maximum custom categories limit reached');
    }

    const newCategory: Category = {
      id: `cat-${Date.now()}`,
      name,
      color,
      isDefault: false,
      createdAt: new Date().toISOString(),
      order: categories.length
    };

    categories.push(newCategory);
    await this.storage.set(STORAGE_KEYS.CATEGORIES, categories);

    return newCategory;
  }

  /**
   * Update a category
   */
  async update(id: string, updates: Partial<Category>): Promise<Category> {
    const categories = await this.getAll();
    const index = categories.findIndex(c => c.id === id);
    
    if (index === -1) {
      throw new Error('Category not found');
    }

    // Don't allow updating default categories
    if (categories[index].isDefault) {
      throw new Error('Cannot update default categories');
    }

    categories[index] = { ...categories[index], ...updates };
    await this.storage.set(STORAGE_KEYS.CATEGORIES, categories);

    return categories[index];
  }

  /**
   * Delete a category
   */
  async delete(id: string): Promise<void> {
    const categories = await this.getAll();
    const category = categories.find(c => c.id === id);
    
    if (!category) {
      throw new Error('Category not found');
    }

    if (category.isDefault) {
      throw new Error('Cannot delete default categories');
    }

    // Check if category is in use
    const todoService = new TodoService();
    const todos = await todoService.getAll();
    const inUse = todos.some(t => t.category === id);
    
    if (inUse) {
      throw new Error('Category is in use by todos');
    }

    const filtered = categories.filter(c => c.id !== id);
    await this.storage.set(STORAGE_KEYS.CATEGORIES, filtered);
  }
}

// Export all services
export default {
  StorageService,
  TodoService,
  SearchService,
  FilterService,
  ExportService,
  StatisticsService,
  ValidationService,
  CategoryService
};