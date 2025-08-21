/**
 * Todo Application - Data Schema and TypeScript Interfaces
 * 
 * This file defines all data structures, TypeScript interfaces,
 * and validation schemas for the frontend-only todo application.
 */

// ============================================
// Core Data Models
// ============================================

/**
 * Priority levels for todo items
 */
export enum Priority {
  HIGH = 'high',
  MEDIUM = 'medium',
  LOW = 'low'
}

/**
 * Todo item status
 */
export enum TodoStatus {
  ACTIVE = 'active',
  COMPLETED = 'completed'
}

/**
 * Main Todo Item Interface
 */
export interface TodoItem {
  // Identification
  id: string;                      // UUID v4
  
  // Core fields
  title: string;                    // Required, 1-200 characters
  description?: string;             // Optional, 0-1000 characters
  
  // Status and priority
  status: TodoStatus;               // Default: 'active'
  priority: Priority;               // Default: 'medium'
  
  // Organization
  category: string;                 // Default: 'General'
  tags: string[];                   // Maximum 3 tags
  
  // Temporal fields
  dueDate?: string;                 // ISO 8601 string format
  dueTime?: string;                 // HH:MM format (24-hour)
  completedAt?: string;             // ISO 8601 string when completed
  
  // Metadata
  createdAt: string;                // ISO 8601 string
  updatedAt: string;                // ISO 8601 string
  
  // UI state
  order: number;                    // For custom sorting/drag-drop
  isDeleted?: boolean;              // Soft delete flag
  deletedAt?: string;               // ISO 8601 string when deleted
}

/**
 * Category Definition
 */
export interface Category {
  id: string;                       // UUID v4
  name: string;                     // 1-30 characters
  color: string;                    // Hex color code (#RRGGBB)
  icon?: string;                    // Material icon name
  isDefault: boolean;               // System category flag
  createdAt: string;                // ISO 8601 string
  order: number;                    // Display order
}

/**
 * User Preferences
 */
export interface UserPreferences {
  // Theme settings
  theme: 'light' | 'dark' | 'system';
  
  // Display preferences
  completedAtBottom: boolean;       // Move completed todos to bottom
  showCompletedTodos: boolean;      // Show/hide completed todos
  showStatistics: boolean;          // Show statistics panel
  compactView: boolean;             // Compact todo item display
  
  // Default values
  defaultPriority: Priority;
  defaultCategory: string;          // Category ID
  
  // Behavior settings
  confirmDelete: boolean;           // Show delete confirmation
  autoSave: boolean;               // Auto-save changes
  keyboardShortcutsEnabled: boolean;
  
  // Sorting preferences
  defaultSortBy: SortOption;
  defaultSortOrder: SortOrder;
  
  // Notification settings
  showNotifications: boolean;       // Show success/error toasts
  soundEnabled: boolean;           // Play sounds on actions
}

/**
 * Filter Options
 */
export interface FilterOptions {
  searchQuery?: string;             // Text search query
  status?: TodoStatus | 'all';      // Status filter
  priorities?: Priority[];          // Priority filter (multiple)
  categories?: string[];            // Category IDs (multiple)
  tags?: string[];                  // Tag filter (multiple)
  dateRange?: DateRange;            // Due date range
  hasNoDueDate?: boolean;          // Include items without due date
}

/**
 * Date Range for filtering
 */
export interface DateRange {
  start: string;                    // ISO 8601 string
  end: string;                      // ISO 8601 string
  preset?: DateRangePreset;         // Optional preset identifier
}

/**
 * Date Range Presets
 */
export enum DateRangePreset {
  TODAY = 'today',
  TOMORROW = 'tomorrow',
  THIS_WEEK = 'this_week',
  NEXT_WEEK = 'next_week',
  THIS_MONTH = 'this_month',
  OVERDUE = 'overdue',
  NO_DATE = 'no_date',
  CUSTOM = 'custom'
}

/**
 * Sort Options
 */
export enum SortOption {
  CREATED_AT = 'createdAt',
  UPDATED_AT = 'updatedAt',
  DUE_DATE = 'dueDate',
  PRIORITY = 'priority',
  TITLE = 'title',
  CATEGORY = 'category',
  STATUS = 'status',
  CUSTOM = 'custom'               // Manual drag-drop order
}

/**
 * Sort Order
 */
export enum SortOrder {
  ASC = 'asc',
  DESC = 'desc'
}

// ============================================
// Statistics and Analytics
// ============================================

/**
 * Todo Statistics
 */
export interface TodoStatistics {
  // Counts
  totalTodos: number;
  activeTodos: number;
  completedTodos: number;
  overdueTodos: number;
  
  // Completion metrics
  completedToday: number;
  completedThisWeek: number;
  completedThisMonth: number;
  completionRate: number;           // Percentage
  
  // Time metrics
  averageCompletionTime: number;    // In hours
  
  // Distribution
  byPriority: PriorityDistribution;
  byCategory: CategoryDistribution;
  
  // Productivity
  currentStreak: number;            // Days
  longestStreak: number;            // Days
  lastActivityDate: string;         // ISO 8601
  
  // Trends
  dailyCompletions: DailyCompletion[];
}

export interface PriorityDistribution {
  high: number;
  medium: number;
  low: number;
}

export interface CategoryDistribution {
  [categoryId: string]: number;
}

export interface DailyCompletion {
  date: string;                     // YYYY-MM-DD
  completed: number;
  created: number;
}

// ============================================
// Data Transfer Objects (DTOs)
// ============================================

/**
 * Create Todo DTO
 */
export interface CreateTodoDto {
  title: string;
  description?: string;
  priority?: Priority;
  category?: string;
  tags?: string[];
  dueDate?: string;
  dueTime?: string;
}

/**
 * Update Todo DTO
 */
export interface UpdateTodoDto {
  title?: string;
  description?: string;
  status?: TodoStatus;
  priority?: Priority;
  category?: string;
  tags?: string[];
  dueDate?: string | null;         // null to clear
  dueTime?: string | null;         // null to clear
}

/**
 * Bulk Update DTO
 */
export interface BulkUpdateDto {
  ids: string[];
  updates: UpdateTodoDto;
}

/**
 * Import/Export DTOs
 */
export interface ExportOptions {
  format: 'json' | 'csv' | 'markdown' | 'pdf';
  includeCompleted: boolean;
  includeDeleted: boolean;
  dateRange?: DateRange;
  categories?: string[];
}

export interface ImportResult {
  success: boolean;
  imported: number;
  failed: number;
  errors: ImportError[];
}

export interface ImportError {
  row: number;
  field: string;
  message: string;
}

// ============================================
// LocalStorage Schema
// ============================================

/**
 * LocalStorage Key Structure
 */
export const STORAGE_KEYS = {
  // Primary data
  TODOS: 'todo_app_todos_v1',
  CATEGORIES: 'todo_app_categories_v1',
  PREFERENCES: 'todo_app_preferences_v1',
  
  // Metadata
  LAST_SYNC: 'todo_app_last_sync_v1',
  STATISTICS: 'todo_app_statistics_v1',
  
  // Backup and recovery
  BACKUP: 'todo_app_backup_v1',
  BACKUP_DATE: 'todo_app_backup_date_v1',
  
  // UI State (temporary)
  FILTER_STATE: 'todo_app_filter_state_v1',
  UI_STATE: 'todo_app_ui_state_v1',
  
  // Search
  SEARCH_HISTORY: 'todo_app_search_history_v1',
  
  // Version control
  SCHEMA_VERSION: 'todo_app_schema_version_v1'
} as const;

/**
 * Storage Data Structure
 */
export interface StorageData {
  version: string;                  // Schema version
  todos: TodoItem[];
  categories: Category[];
  preferences: UserPreferences;
  statistics: TodoStatistics;
  lastModified: string;             // ISO 8601
}

/**
 * Storage Metadata
 */
export interface StorageMetadata {
  version: string;
  totalSize: number;                // Bytes
  todoCount: number;
  categoryCount: number;
  lastBackup?: string;              // ISO 8601
  schemaVersion: string;
}

// ============================================
// Validation Schemas
// ============================================

/**
 * Validation Rules
 */
export const VALIDATION_RULES = {
  todo: {
    title: {
      minLength: 1,
      maxLength: 200,
      required: true,
      pattern: /^[^<>]*$/            // No HTML tags
    },
    description: {
      maxLength: 1000,
      required: false,
      pattern: /^[^<>]*$/            // No HTML tags
    },
    tags: {
      maxCount: 3,
      maxLength: 20,
      pattern: /^[a-zA-Z0-9-_]+$/    // Alphanumeric with dash/underscore
    }
  },
  category: {
    name: {
      minLength: 1,
      maxLength: 30,
      required: true,
      pattern: /^[a-zA-Z0-9\s]+$/    // Alphanumeric with spaces
    },
    color: {
      pattern: /^#[0-9A-Fa-f]{6}$/   // Hex color
    }
  },
  storage: {
    maxSize: 10 * 1024 * 1024,       // 10MB
    warningThreshold: 0.8,           // 80% full warning
    maxTodos: 10000,
    maxCategories: 20
  }
} as const;

/**
 * Validation Result
 */
export interface ValidationResult {
  valid: boolean;
  errors: ValidationError[];
}

export interface ValidationError {
  field: string;
  message: string;
  code: string;
}

// ============================================
// Default Values
// ============================================

/**
 * Default Categories
 */
export const DEFAULT_CATEGORIES: Category[] = [
  {
    id: 'cat-general',
    name: 'General',
    color: '#9E9E9E',
    icon: 'category',
    isDefault: true,
    createdAt: new Date().toISOString(),
    order: 0
  },
  {
    id: 'cat-work',
    name: 'Work',
    color: '#2196F3',
    icon: 'work',
    isDefault: true,
    createdAt: new Date().toISOString(),
    order: 1
  },
  {
    id: 'cat-personal',
    name: 'Personal',
    color: '#4CAF50',
    icon: 'person',
    isDefault: true,
    createdAt: new Date().toISOString(),
    order: 2
  },
  {
    id: 'cat-shopping',
    name: 'Shopping',
    color: '#FF9800',
    icon: 'shopping_cart',
    isDefault: true,
    createdAt: new Date().toISOString(),
    order: 3
  },
  {
    id: 'cat-health',
    name: 'Health',
    color: '#F44336',
    icon: 'favorite',
    isDefault: true,
    createdAt: new Date().toISOString(),
    order: 4
  },
  {
    id: 'cat-finance',
    name: 'Finance',
    color: '#9C27B0',
    icon: 'attach_money',
    isDefault: true,
    createdAt: new Date().toISOString(),
    order: 5
  }
];

/**
 * Default Preferences
 */
export const DEFAULT_PREFERENCES: UserPreferences = {
  theme: 'system',
  completedAtBottom: true,
  showCompletedTodos: true,
  showStatistics: false,
  compactView: false,
  defaultPriority: Priority.MEDIUM,
  defaultCategory: 'cat-general',
  confirmDelete: true,
  autoSave: true,
  keyboardShortcutsEnabled: true,
  defaultSortBy: SortOption.PRIORITY,
  defaultSortOrder: SortOrder.DESC,
  showNotifications: true,
  soundEnabled: false
};

// ============================================
// Type Guards
// ============================================

/**
 * Type guard for TodoItem
 */
export function isTodoItem(obj: any): obj is TodoItem {
  return (
    typeof obj === 'object' &&
    typeof obj.id === 'string' &&
    typeof obj.title === 'string' &&
    typeof obj.status === 'string' &&
    typeof obj.priority === 'string' &&
    typeof obj.createdAt === 'string'
  );
}

/**
 * Type guard for Category
 */
export function isCategory(obj: any): obj is Category {
  return (
    typeof obj === 'object' &&
    typeof obj.id === 'string' &&
    typeof obj.name === 'string' &&
    typeof obj.color === 'string' &&
    typeof obj.isDefault === 'boolean'
  );
}

// ============================================
// Serialization Helpers
// ============================================

/**
 * Serialize todo for storage
 */
export function serializeTodo(todo: TodoItem): string {
  return JSON.stringify(todo);
}

/**
 * Deserialize todo from storage
 */
export function deserializeTodo(data: string): TodoItem | null {
  try {
    const parsed = JSON.parse(data);
    if (isTodoItem(parsed)) {
      return parsed;
    }
    return null;
  } catch {
    return null;
  }
}

/**
 * Compress data for storage efficiency
 */
export function compressData(data: any): string {
  // Use a compression library like lz-string
  // This is a placeholder - implement with actual compression
  return JSON.stringify(data);
}

/**
 * Decompress data from storage
 */
export function decompressData(compressed: string): any {
  // Use a compression library like lz-string
  // This is a placeholder - implement with actual decompression
  return JSON.parse(compressed);
}

// ============================================
// Migration Schemas
// ============================================

/**
 * Schema version history for migrations
 */
export const SCHEMA_VERSIONS = {
  V1: '1.0.0',
  V2: '2.0.0', // Future version
} as const;

/**
 * Migration function type
 */
export type MigrationFunction = (data: any) => any;

/**
 * Schema migrations map
 */
export const MIGRATIONS: Record<string, MigrationFunction> = {
  '1.0.0_to_2.0.0': (data) => {
    // Future migration logic
    return data;
  }
};

// Export all types
export type {
  StorageData,
  StorageMetadata
};