# Todo Application - Frontend-Only Architecture

## Executive Summary

This document defines the technical architecture for a browser-based todo application that operates entirely on the client side with no backend dependencies. The application uses Next.js 14+ as a static site generator, Material-UI for the component library, and browser LocalStorage for data persistence.

### Key Architectural Decisions

- **Frontend-Only Design**: Complete client-side application with no server dependencies
- **Static Site Generation**: Next.js configured for static export (`next export`)
- **Local Data Persistence**: Browser LocalStorage with IndexedDB fallback for large datasets
- **State Management**: Zustand for global state with React Context for theming
- **Component Architecture**: Atomic design pattern with Material-UI components
- **TypeScript**: Full type safety across the application

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         Browser Environment                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    Next.js Application                    │  │
│  │                                                           │  │
│  │  ┌─────────────────────────────────────────────────┐    │  │
│  │  │              Presentation Layer                   │    │  │
│  │  │  ┌──────────┐  ┌──────────┐  ┌──────────┐      │    │  │
│  │  │  │  Pages   │  │  Layouts │  │Components│      │    │  │
│  │  │  └──────────┘  └──────────┘  └──────────┘      │    │  │
│  │  └─────────────────────────────────────────────────┘    │  │
│  │                                                           │  │
│  │  ┌─────────────────────────────────────────────────┐    │  │
│  │  │              State Management Layer              │    │  │
│  │  │  ┌──────────┐  ┌──────────┐  ┌──────────┐      │    │  │
│  │  │  │ Zustand  │  │  React  │  │  Custom  │      │    │  │
│  │  │  │  Store   │  │ Context  │  │   Hooks  │      │    │  │
│  │  │  └──────────┘  └──────────┘  └──────────┘      │    │  │
│  │  └─────────────────────────────────────────────────┘    │  │
│  │                                                           │  │
│  │  ┌─────────────────────────────────────────────────┐    │  │
│  │  │              Service Layer (Classes)             │    │  │
│  │  │  ┌──────────┐  ┌──────────┐  ┌──────────┐      │    │  │
│  │  │  │   Todo   │  │  Search  │  │  Export  │      │    │  │
│  │  │  │ Service  │  │ Service  │  │ Service  │      │    │  │
│  │  │  └──────────┘  └──────────┘  └──────────┘      │    │  │
│  │  └─────────────────────────────────────────────────┘    │  │
│  │                                                           │  │
│  │  ┌─────────────────────────────────────────────────┐    │  │
│  │  │          Storage Abstraction Layer               │    │  │
│  │  │  ┌──────────┐  ┌──────────┐  ┌──────────┐      │    │  │
│  │  │  │  Local   │  │ IndexedDB│  │  Memory  │      │    │  │
│  │  │  │ Storage  │  │ Adapter  │  │  Cache   │      │    │  │
│  │  │  └──────────┘  └──────────┘  └──────────┘      │    │  │
│  │  └─────────────────────────────────────────────────┘    │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                  Browser Storage APIs                     │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │  │
│  │  │ LocalStorage │  │  IndexedDB   │  │SessionStorage│  │  │
│  │  │   (10MB)     │  │  (50MB+)     │  │   (5MB)      │  │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Component Architecture

### Directory Structure

```
/todo-app
├── /app                          # Next.js App Router
│   ├── layout.tsx               # Root layout with providers
│   ├── page.tsx                 # Main todo list page
│   ├── globals.css             # Global styles
│   └── /api                    # Empty (no API routes)
│
├── /components
│   ├── /atoms                  # Basic building blocks
│   │   ├── Button.tsx
│   │   ├── Checkbox.tsx
│   │   ├── TextField.tsx
│   │   └── IconButton.tsx
│   │
│   ├── /molecules             # Composite components
│   │   ├── TodoItem.tsx
│   │   ├── FilterChip.tsx
│   │   ├── PriorityBadge.tsx
│   │   ├── SearchBar.tsx
│   │   └── DatePicker.tsx
│   │
│   ├── /organisms            # Complex components
│   │   ├── TodoList.tsx
│   │   ├── TodoForm.tsx
│   │   ├── FilterPanel.tsx
│   │   ├── StatisticsPanel.tsx
│   │   └── BulkActionBar.tsx
│   │
│   └── /templates           # Page templates
│       ├── MainLayout.tsx
│       ├── EmptyState.tsx
│       └── ErrorBoundary.tsx
│
├── /hooks                    # Custom React hooks
│   ├── useTodos.ts
│   ├── useLocalStorage.ts
│   ├── useDebounce.ts
│   ├── useKeyboardShortcuts.ts
│   └── useMediaQuery.ts
│
├── /services               # Business logic services
│   ├── TodoService.ts
│   ├── StorageService.ts
│   ├── SearchService.ts
│   ├── FilterService.ts
│   ├── ExportService.ts
│   └── ValidationService.ts
│
├── /store                  # Zustand state management
│   ├── todoStore.ts
│   ├── filterStore.ts
│   ├── uiStore.ts
│   └── preferenceStore.ts
│
├── /lib                    # Utility functions
│   ├── constants.ts
│   ├── validators.ts
│   ├── formatters.ts
│   ├── sortUtils.ts
│   └── dateUtils.ts
│
├── /types                  # TypeScript definitions
│   ├── todo.types.ts
│   ├── filter.types.ts
│   ├── preference.types.ts
│   └── index.ts
│
├── /styles                 # Styling
│   ├── theme.ts           # Material-UI theme
│   └── /modules           # CSS modules
│
└── /public                # Static assets
    ├── manifest.json      # PWA manifest
    └── /icons            # App icons
```

### Component Hierarchy

```
App
├── ThemeProvider (Material-UI)
│   └── StoreProvider (Zustand)
│       └── MainLayout
│           ├── Header
│           │   ├── AppBar
│           │   ├── SearchBar
│           │   ├── ThemeToggle
│           │   └── MenuButton
│           │
│           ├── Sidebar (Desktop) / Drawer (Mobile)
│           │   ├── FilterPanel
│           │   │   ├── StatusFilter
│           │   │   ├── PriorityFilter
│           │   │   ├── CategoryFilter
│           │   │   └── DateRangeFilter
│           │   └── StatisticsWidget
│           │
│           ├── Main Content
│           │   ├── TodoList
│           │   │   ├── SortControls
│           │   │   ├── BulkActionBar
│           │   │   └── TodoItems[]
│           │   │       ├── Checkbox
│           │   │       ├── TodoContent
│           │   │       ├── PriorityBadge
│           │   │       ├── CategoryChip
│           │   │       ├── DueDate
│           │   │       └── ActionButtons
│           │   │
│           │   └── EmptyState
│           │
│           ├── FloatingActionButton
│           │   └── TodoFormModal
│           │
│           └── NotificationSnackbar
```

## State Management Architecture

### Zustand Store Structure

```typescript
// Global State Tree
interface AppState {
  // Todo Store
  todos: {
    items: TodoItem[];
    loading: boolean;
    error: string | null;
    lastSync: Date;
  };
  
  // Filter Store
  filters: {
    searchQuery: string;
    status: FilterStatus;
    priorities: Priority[];
    categories: string[];
    dateRange: DateRange | null;
    sortBy: SortOption;
    sortOrder: 'asc' | 'desc';
  };
  
  // UI Store
  ui: {
    sidebarOpen: boolean;
    selectedTodos: string[];
    editingTodo: string | null;
    formModalOpen: boolean;
    statsModalOpen: boolean;
    bulkActionMode: boolean;
  };
  
  // Preferences Store
  preferences: {
    theme: 'light' | 'dark' | 'system';
    completedAtBottom: boolean;
    showStatistics: boolean;
    defaultPriority: Priority;
    defaultCategory: string;
    keyboardShortcutsEnabled: boolean;
  };
}
```

### State Flow Diagram

```
User Action → Component → Custom Hook → Zustand Action → Service Layer → Storage
     ↑                                           ↓
     └────────── Re-render ←──── State Update ←─┘
```

## Service Layer Architecture

### Core Services

```typescript
// TodoService - Main business logic
class TodoService {
  private storage: StorageService;
  private validator: ValidationService;
  
  async create(todo: CreateTodoDto): Promise<TodoItem>
  async update(id: string, updates: UpdateTodoDto): Promise<TodoItem>
  async delete(id: string): Promise<void>
  async complete(id: string): Promise<TodoItem>
  async bulkUpdate(ids: string[], updates: UpdateTodoDto): Promise<TodoItem[]>
  async getAll(): Promise<TodoItem[]>
  async getById(id: string): Promise<TodoItem | null>
  async reorder(todos: TodoItem[]): Promise<void>
}

// StorageService - Abstraction over browser storage
class StorageService {
  private adapter: StorageAdapter;
  private cache: Map<string, any>;
  
  async get<T>(key: string): Promise<T | null>
  async set<T>(key: string, value: T): Promise<void>
  async remove(key: string): Promise<void>
  async clear(): Promise<void>
  async getSize(): Promise<number>
  async compress(data: any): Promise<string>
  async decompress(data: string): Promise<any>
}

// SearchService - In-memory search operations
class SearchService {
  search(todos: TodoItem[], query: string): TodoItem[]
  highlightMatches(text: string, query: string): string
  buildSearchIndex(todos: TodoItem[]): SearchIndex
  fuzzySearch(todos: TodoItem[], query: string): TodoItem[]
}

// FilterService - Client-side filtering
class FilterService {
  applyFilters(todos: TodoItem[], filters: FilterOptions): TodoItem[]
  sortTodos(todos: TodoItem[], sortBy: SortOption, order: SortOrder): TodoItem[]
  groupByCategory(todos: TodoItem[]): Map<string, TodoItem[]>
  groupByPriority(todos: TodoItem[]): Map<Priority, TodoItem[]>
}

// ExportService - Data export functionality
class ExportService {
  exportAsJSON(todos: TodoItem[]): string
  exportAsCSV(todos: TodoItem[]): string
  exportAsMarkdown(todos: TodoItem[]): string
  exportAsPDF(todos: TodoItem[]): Blob
  importFromJSON(json: string): TodoItem[]
  importFromCSV(csv: string): TodoItem[]
}
```

## Data Flow Architecture

### Create Todo Flow

```
1. User fills form
2. TodoForm component validates input
3. Calls useTodos hook → createTodo action
4. TodoService.create() validates business rules
5. Generates UUID, timestamps
6. StorageService.set() saves to LocalStorage
7. Updates Zustand store
8. Components re-render with new todo
```

### Search and Filter Flow

```
1. User types in search / changes filter
2. Debounced input (300ms)
3. Updates filter store
4. useFilteredTodos hook recalculates
5. SearchService.search() for text matching
6. FilterService.applyFilters() for criteria
7. FilterService.sortTodos() for ordering
8. Returns filtered, sorted list
9. TodoList re-renders with results
```

## Storage Architecture

### Storage Strategy

```typescript
// Storage Keys Structure
const STORAGE_KEYS = {
  TODOS: 'todo_app_todos_v1',
  PREFERENCES: 'todo_app_preferences_v1',
  CATEGORIES: 'todo_app_categories_v1',
  LAST_SYNC: 'todo_app_last_sync_v1',
  BACKUP: 'todo_app_backup_v1'
};

// Storage Limits Management
interface StorageQuota {
  used: number;
  total: number;
  percentage: number;
}

// Compression for large datasets
class CompressionService {
  compress(data: any): string {
    // LZ-string compression
    return LZString.compressToUTF16(JSON.stringify(data));
  }
  
  decompress(compressed: string): any {
    return JSON.parse(LZString.decompressFromUTF16(compressed));
  }
}
```

### Storage Fallback Strategy

```
Primary: LocalStorage (10MB limit)
    ↓ (If quota exceeded)
Secondary: IndexedDB (50MB+ limit)
    ↓ (If not supported)
Tertiary: SessionStorage (5MB limit, temporary)
    ↓ (If all fail)
Memory: In-memory storage (no persistence)
```

## Performance Optimization

### Rendering Optimizations

```typescript
// Virtual Scrolling for large lists
const VirtualTodoList = () => {
  return (
    <VirtualList
      height={600}
      itemCount={todos.length}
      itemSize={80}
      overscan={5}
    >
      {({ index, style }) => (
        <TodoItem
          key={todos[index].id}
          todo={todos[index]}
          style={style}
        />
      )}
    </VirtualList>
  );
};

// Memoization
const TodoItem = React.memo(({ todo }) => {
  // Component implementation
}, (prevProps, nextProps) => {
  return prevProps.todo.updatedAt === nextProps.todo.updatedAt;
});

// Lazy Loading
const StatisticsPanel = lazy(() => import('./StatisticsPanel'));
const ExportDialog = lazy(() => import('./ExportDialog'));
```

### Data Optimizations

```typescript
// Debounced operations
const debouncedSave = useMemo(
  () => debounce((todos) => saveTodos(todos), 500),
  []
);

// Batch updates
const batchUpdate = (updates: TodoUpdate[]) => {
  set((state) => ({
    todos: state.todos.map(todo => {
      const update = updates.find(u => u.id === todo.id);
      return update ? { ...todo, ...update.changes } : todo;
    })
  }));
};

// Incremental search indexing
const searchIndex = useMemo(
  () => buildSearchIndex(todos),
  [todos.length] // Only rebuild on count change
);
```

## Security Considerations

### Client-Side Security

```typescript
// Input Sanitization
class ValidationService {
  sanitizeInput(input: string): string {
    return DOMPurify.sanitize(input, {
      ALLOWED_TAGS: [],
      ALLOWED_ATTR: []
    });
  }
  
  validateTodo(todo: CreateTodoDto): ValidationResult {
    // XSS prevention
    // Length validation
    // Character validation
  }
}

// Content Security Policy
const CSP_HEADER = {
  'Content-Security-Policy': 
    "default-src 'self'; " +
    "script-src 'self' 'unsafe-inline'; " +
    "style-src 'self' 'unsafe-inline'; " +
    "img-src 'self' data: blob:; " +
    "connect-src 'self';"
};
```

## Build Configuration

### Next.js Configuration

```javascript
// next.config.js
module.exports = {
  output: 'export', // Static HTML export
  distDir: 'out',
  images: {
    unoptimized: true // For static export
  },
  webpack: (config) => {
    // Optimizations
    config.optimization.splitChunks = {
      chunks: 'all',
      cacheGroups: {
        default: false,
        vendors: false,
        vendor: {
          name: 'vendor',
          chunks: 'all',
          test: /node_modules/
        }
      }
    };
    return config;
  }
};
```

### Build Output Structure

```
/out (Static Build)
├── index.html
├── 404.html
├── _next/
│   ├── static/
│   │   ├── chunks/
│   │   ├── css/
│   │   └── media/
│   └── data/
├── manifest.json
└── icons/
```

## Deployment Architecture

### Static Hosting Options

1. **Vercel** (Recommended)
   - Automatic deployments
   - Edge network CDN
   - Zero configuration

2. **Netlify**
   - Git-based deployments
   - Form handling (unused)
   - Functions (unused)

3. **GitHub Pages**
   - Free hosting
   - Custom domain support
   - GitHub Actions CI/CD

4. **AWS S3 + CloudFront**
   - Scalable static hosting
   - Global CDN
   - Custom domain with Route53

### Deployment Configuration

```yaml
# GitHub Actions Deployment
name: Deploy to GitHub Pages
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-node@v2
      - run: npm ci
      - run: npm run build
      - run: npm run export
      - uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./out
```

## Progressive Web App (PWA) Configuration

### Service Worker

```javascript
// service-worker.js
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open('todo-app-v1').then((cache) => {
      return cache.addAll([
        '/',
        '/index.html',
        '/_next/static/css/main.css',
        '/_next/static/js/main.js'
      ]);
    })
  );
});

self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request).then((response) => {
      return response || fetch(event.request);
    })
  );
});
```

### Manifest Configuration

```json
{
  "name": "Todo App",
  "short_name": "Todo",
  "description": "Personal task management application",
  "start_url": "/",
  "display": "standalone",
  "theme_color": "#1976D2",
  "background_color": "#ffffff",
  "icons": [
    {
      "src": "/icon-192.png",
      "sizes": "192x192",
      "type": "image/png"
    },
    {
      "src": "/icon-512.png",
      "sizes": "512x512",
      "type": "image/png"
    }
  ]
}
```

## Error Handling Architecture

### Error Boundary Implementation

```typescript
class ErrorBoundary extends Component {
  state = { hasError: false, error: null };
  
  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }
  
  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
    // Could send to error tracking service if needed
  }
  
  render() {
    if (this.state.hasError) {
      return <ErrorFallback error={this.state.error} />;
    }
    return this.props.children;
  }
}
```

### Storage Error Handling

```typescript
class StorageService {
  async set<T>(key: string, value: T): Promise<void> {
    try {
      const serialized = JSON.stringify(value);
      localStorage.setItem(key, serialized);
    } catch (error) {
      if (error.name === 'QuotaExceededError') {
        // Handle storage quota
        await this.cleanup();
        // Retry or fallback to IndexedDB
      } else {
        // Handle other errors
        console.error('Storage error:', error);
        throw new StorageError('Failed to save data');
      }
    }
  }
}
```

## Testing Strategy

### Unit Testing

```typescript
// TodoService.test.ts
describe('TodoService', () => {
  it('should create a new todo', async () => {
    const todo = await todoService.create({
      title: 'Test Todo',
      priority: 'high'
    });
    expect(todo.id).toBeDefined();
    expect(todo.title).toBe('Test Todo');
  });
});
```

### Component Testing

```typescript
// TodoItem.test.tsx
describe('TodoItem', () => {
  it('should render todo content', () => {
    render(<TodoItem todo={mockTodo} />);
    expect(screen.getByText(mockTodo.title)).toBeInTheDocument();
  });
});
```

### E2E Testing

```typescript
// todo-flow.e2e.ts
describe('Todo Creation Flow', () => {
  it('should create and complete a todo', async () => {
    await page.goto('/');
    await page.click('[data-testid="add-todo"]');
    await page.fill('[name="title"]', 'Test Todo');
    await page.click('[type="submit"]');
    await expect(page.locator('text=Test Todo')).toBeVisible();
  });
});
```

## Migration Path

### Future Backend Integration

If backend integration becomes necessary:

1. **API Service Layer**: Add API service alongside existing storage service
2. **Sync Service**: Implement sync between local and remote storage
3. **Authentication**: Add auth context and protected routes
4. **Conflict Resolution**: Implement last-write-wins or operational transformation
5. **Offline Queue**: Queue mutations when offline, sync when online

```typescript
// Future API integration point
class ApiService implements StorageAdapter {
  async get<T>(key: string): Promise<T> {
    // Fetch from API instead of localStorage
    const response = await fetch(`/api/todos`);
    return response.json();
  }
  
  async set<T>(key: string, value: T): Promise<void> {
    // Send to API instead of localStorage
    await fetch(`/api/todos`, {
      method: 'POST',
      body: JSON.stringify(value)
    });
  }
}
```

---

*Document Version: 1.0.0*  
*Last Updated: 2025-01-21*  
*Status: Complete - Implementation Ready*