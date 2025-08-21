# Todo Application - Component Architecture

## Overview

This document defines the complete component architecture for the frontend-only todo application using Next.js 14+, Material-UI v5, and TypeScript. The architecture follows atomic design principles with a focus on reusability, accessibility, and performance.

## Component Hierarchy

```
Application Root
├── Providers Layer
│   ├── ThemeProvider (Material-UI)
│   ├── StoreProvider (Zustand)
│   └── NotificationProvider
│
├── Layout Components
│   ├── RootLayout
│   ├── Header
│   ├── Sidebar
│   ├── MainContent
│   └── Footer
│
├── Page Components
│   └── TodoPage (main page)
│
└── Feature Components
    ├── TodoManagement
    ├── FilterSystem
    ├── SearchSystem
    ├── StatisticsPanel
    └── ImportExport
```

## Page Components

### Main Todo Page (`app/page.tsx`)

```typescript
'use client';

import { useEffect } from 'react';
import { Box, Container } from '@mui/material';
import { MainLayout } from '@/components/templates/MainLayout';
import { TodoList } from '@/components/organisms/TodoList';
import { FilterPanel } from '@/components/organisms/FilterPanel';
import { StatisticsPanel } from '@/components/organisms/StatisticsPanel';
import { TodoFormModal } from '@/components/organisms/TodoFormModal';
import { FloatingActionButton } from '@/components/molecules/FloatingActionButton';
import { useTodoStore } from '@/store/todoStore';
import { useFilterStore } from '@/store/filterStore';
import { useKeyboardShortcuts } from '@/hooks/useKeyboardShortcuts';

export default function TodoPage() {
  const { todos, loadTodos } = useTodoStore();
  const { filters } = useFilterStore();
  const { registerShortcuts } = useKeyboardShortcuts();

  useEffect(() => {
    loadTodos();
    registerShortcuts();
  }, []);

  return (
    <MainLayout>
      <Container maxWidth="xl">
        <Box display="flex" gap={3}>
          <Box flex="0 0 280px">
            <FilterPanel />
            <StatisticsPanel collapsed />
          </Box>
          
          <Box flex="1">
            <TodoList 
              todos={todos}
              filters={filters}
            />
          </Box>
        </Box>
        
        <FloatingActionButton />
        <TodoFormModal />
      </Container>
    </MainLayout>
  );
}
```

## Template Components

### MainLayout (`components/templates/MainLayout.tsx`)

```typescript
import { ReactNode } from 'react';
import { Box, CssBaseline } from '@mui/material';
import { Header } from '@/components/organisms/Header';
import { MobileNavigation } from '@/components/organisms/MobileNavigation';
import { NotificationSnackbar } from '@/components/molecules/NotificationSnackbar';
import { ErrorBoundary } from '@/components/molecules/ErrorBoundary';
import { useMediaQuery } from '@/hooks/useMediaQuery';

interface MainLayoutProps {
  children: ReactNode;
}

export function MainLayout({ children }: MainLayoutProps) {
  const isMobile = useMediaQuery('(max-width: 768px)');

  return (
    <ErrorBoundary>
      <CssBaseline />
      <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
        <Header />
        
        <Box component="main" sx={{ flex: 1, py: 3 }}>
          {children}
        </Box>
        
        {isMobile && <MobileNavigation />}
        
        <NotificationSnackbar />
      </Box>
    </ErrorBoundary>
  );
}
```

## Organism Components

### TodoList Component

```typescript
// components/organisms/TodoList.tsx
import { useState, useMemo, useCallback } from 'react';
import {
  Box,
  Paper,
  Typography,
  Divider,
  Collapse,
  IconButton
} from '@mui/material';
import { DragDropContext, Droppable, Draggable } from '@hello-pangea/dnd';
import { TodoItem } from '@/components/molecules/TodoItem';
import { BulkActionBar } from '@/components/molecules/BulkActionBar';
import { SortControls } from '@/components/molecules/SortControls';
import { EmptyState } from '@/components/molecules/EmptyState';
import { VirtualList } from '@/components/molecules/VirtualList';
import { useTodoOperations } from '@/hooks/useTodoOperations';
import { useFilteredTodos } from '@/hooks/useFilteredTodos';
import { TodoItem as TodoType } from '@/types';

interface TodoListProps {
  todos: TodoType[];
  filters: FilterOptions;
}

export function TodoList({ todos, filters }: TodoListProps) {
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const [expandedIds, setExpandedIds] = useState<Set<string>>(new Set());
  
  const { updateTodo, deleteTodo, reorderTodos } = useTodoOperations();
  const filteredTodos = useFilteredTodos(todos, filters);
  
  const handleDragEnd = useCallback((result: any) => {
    if (!result.destination) return;
    
    const items = Array.from(filteredTodos);
    const [reorderedItem] = items.splice(result.source.index, 1);
    items.splice(result.destination.index, 0, reorderedItem);
    
    reorderTodos(items);
  }, [filteredTodos, reorderTodos]);

  const handleSelectAll = useCallback(() => {
    if (selectedIds.size === filteredTodos.length) {
      setSelectedIds(new Set());
    } else {
      setSelectedIds(new Set(filteredTodos.map(t => t.id)));
    }
  }, [selectedIds, filteredTodos]);

  if (filteredTodos.length === 0) {
    return <EmptyState type={filters.searchQuery ? 'no-results' : 'no-todos'} />;
  }

  const showVirtualList = filteredTodos.length > 100;

  return (
    <Paper elevation={0} sx={{ p: 2 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h6">
          {filteredTodos.length} {filteredTodos.length === 1 ? 'todo' : 'todos'}
        </Typography>
        
        <SortControls />
      </Box>
      
      <Divider sx={{ mb: 2 }} />
      
      {selectedIds.size > 0 && (
        <BulkActionBar
          selectedCount={selectedIds.size}
          onSelectAll={handleSelectAll}
          selectedIds={Array.from(selectedIds)}
        />
      )}
      
      {showVirtualList ? (
        <VirtualList
          items={filteredTodos}
          itemHeight={80}
          renderItem={(todo) => (
            <TodoItem
              key={todo.id}
              todo={todo}
              selected={selectedIds.has(todo.id)}
              expanded={expandedIds.has(todo.id)}
              onSelect={(id) => {
                const newSelected = new Set(selectedIds);
                if (newSelected.has(id)) {
                  newSelected.delete(id);
                } else {
                  newSelected.add(id);
                }
                setSelectedIds(newSelected);
              }}
              onToggleExpand={(id) => {
                const newExpanded = new Set(expandedIds);
                if (newExpanded.has(id)) {
                  newExpanded.delete(id);
                } else {
                  newExpanded.add(id);
                }
                setExpandedIds(newExpanded);
              }}
            />
          )}
        />
      ) : (
        <DragDropContext onDragEnd={handleDragEnd}>
          <Droppable droppableId="todo-list">
            {(provided) => (
              <Box ref={provided.innerRef} {...provided.droppableProps}>
                {filteredTodos.map((todo, index) => (
                  <Draggable key={todo.id} draggableId={todo.id} index={index}>
                    {(provided, snapshot) => (
                      <Box
                        ref={provided.innerRef}
                        {...provided.draggableProps}
                        {...provided.dragHandleProps}
                        sx={{
                          opacity: snapshot.isDragging ? 0.8 : 1,
                          mb: 1
                        }}
                      >
                        <TodoItem
                          todo={todo}
                          selected={selectedIds.has(todo.id)}
                          expanded={expandedIds.has(todo.id)}
                          onSelect={(id) => {
                            const newSelected = new Set(selectedIds);
                            if (newSelected.has(id)) {
                              newSelected.delete(id);
                            } else {
                              newSelected.add(id);
                            }
                            setSelectedIds(newSelected);
                          }}
                          onToggleExpand={(id) => {
                            const newExpanded = new Set(expandedIds);
                            if (newExpanded.has(id)) {
                              newExpanded.delete(id);
                            } else {
                              newExpanded.add(id);
                            }
                            setExpandedIds(newExpanded);
                          }}
                        />
                      </Box>
                    )}
                  </Draggable>
                ))}
                {provided.placeholder}
              </Box>
            )}
          </Droppable>
        </DragDropContext>
      )}
    </Paper>
  );
}
```

### TodoForm Component

```typescript
// components/organisms/TodoFormModal.tsx
import { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Box,
  IconButton
} from '@mui/material';
import { DatePicker, TimePicker } from '@mui/x-date-pickers';
import { Close as CloseIcon } from '@mui/icons-material';
import { useUIStore } from '@/store/uiStore';
import { useTodoStore } from '@/store/todoStore';
import { useCategoryStore } from '@/store/categoryStore';
import { Priority, CreateTodoDto } from '@/types';

export function TodoFormModal() {
  const { formModalOpen, closeFormModal, editingTodo } = useUIStore();
  const { createTodo, updateTodo } = useTodoStore();
  const { categories } = useCategoryStore();
  
  const [formData, setFormData] = useState<CreateTodoDto>({
    title: '',
    description: '',
    priority: Priority.MEDIUM,
    category: 'cat-general',
    tags: [],
    dueDate: undefined,
    dueTime: undefined
  });
  
  const [tagInput, setTagInput] = useState('');
  const [errors, setErrors] = useState<Record<string, string>>({});

  const handleSubmit = async () => {
    // Validation
    const newErrors: Record<string, string> = {};
    
    if (!formData.title.trim()) {
      newErrors.title = 'Title is required';
    }
    
    if (formData.title.length > 200) {
      newErrors.title = 'Title must be less than 200 characters';
    }
    
    if (formData.description && formData.description.length > 1000) {
      newErrors.description = 'Description must be less than 1000 characters';
    }
    
    if (formData.tags.length > 3) {
      newErrors.tags = 'Maximum 3 tags allowed';
    }
    
    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }
    
    try {
      if (editingTodo) {
        await updateTodo(editingTodo.id, formData);
      } else {
        await createTodo(formData);
      }
      
      closeFormModal();
      resetForm();
    } catch (error) {
      console.error('Failed to save todo:', error);
    }
  };

  const resetForm = () => {
    setFormData({
      title: '',
      description: '',
      priority: Priority.MEDIUM,
      category: 'cat-general',
      tags: [],
      dueDate: undefined,
      dueTime: undefined
    });
    setErrors({});
    setTagInput('');
  };

  const handleAddTag = () => {
    if (tagInput && formData.tags.length < 3) {
      setFormData({
        ...formData,
        tags: [...formData.tags, tagInput.trim()]
      });
      setTagInput('');
    }
  };

  const handleRemoveTag = (index: number) => {
    setFormData({
      ...formData,
      tags: formData.tags.filter((_, i) => i !== index)
    });
  };

  return (
    <Dialog
      open={formModalOpen}
      onClose={closeFormModal}
      maxWidth="sm"
      fullWidth
      PaperProps={{
        sx: { borderRadius: 2 }
      }}
    >
      <DialogTitle>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          {editingTodo ? 'Edit Todo' : 'Create New Todo'}
          <IconButton onClick={closeFormModal} size="small">
            <CloseIcon />
          </IconButton>
        </Box>
      </DialogTitle>
      
      <DialogContent>
        <Grid container spacing={2} sx={{ mt: 1 }}>
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Title"
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              error={!!errors.title}
              helperText={errors.title}
              required
              autoFocus
            />
          </Grid>
          
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Description"
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              error={!!errors.description}
              helperText={errors.description}
              multiline
              rows={3}
            />
          </Grid>
          
          <Grid item xs={6}>
            <FormControl fullWidth>
              <InputLabel>Priority</InputLabel>
              <Select
                value={formData.priority}
                onChange={(e) => setFormData({ ...formData, priority: e.target.value as Priority })}
                label="Priority"
              >
                <MenuItem value={Priority.HIGH}>High</MenuItem>
                <MenuItem value={Priority.MEDIUM}>Medium</MenuItem>
                <MenuItem value={Priority.LOW}>Low</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          
          <Grid item xs={6}>
            <FormControl fullWidth>
              <InputLabel>Category</InputLabel>
              <Select
                value={formData.category}
                onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                label="Category"
              >
                {categories.map((cat) => (
                  <MenuItem key={cat.id} value={cat.id}>
                    <Box display="flex" alignItems="center" gap={1}>
                      <Box
                        sx={{
                          width: 12,
                          height: 12,
                          borderRadius: '50%',
                          backgroundColor: cat.color
                        }}
                      />
                      {cat.name}
                    </Box>
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          
          <Grid item xs={6}>
            <DatePicker
              label="Due Date"
              value={formData.dueDate ? new Date(formData.dueDate) : null}
              onChange={(date) => setFormData({ 
                ...formData, 
                dueDate: date ? date.toISOString() : undefined 
              })}
              slotProps={{ textField: { fullWidth: true } }}
            />
          </Grid>
          
          <Grid item xs={6}>
            <TimePicker
              label="Due Time"
              value={formData.dueTime ? new Date(`2000-01-01T${formData.dueTime}`) : null}
              onChange={(time) => setFormData({ 
                ...formData, 
                dueTime: time ? time.toTimeString().slice(0, 5) : undefined 
              })}
              slotProps={{ textField: { fullWidth: true } }}
              disabled={!formData.dueDate}
            />
          </Grid>
          
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Add Tag"
              value={tagInput}
              onChange={(e) => setTagInput(e.target.value)}
              onKeyPress={(e) => {
                if (e.key === 'Enter') {
                  e.preventDefault();
                  handleAddTag();
                }
              }}
              error={!!errors.tags}
              helperText={errors.tags || `${formData.tags.length}/3 tags`}
              disabled={formData.tags.length >= 3}
            />
            
            <Box display="flex" gap={1} mt={1} flexWrap="wrap">
              {formData.tags.map((tag, index) => (
                <Chip
                  key={index}
                  label={tag}
                  onDelete={() => handleRemoveTag(index)}
                  size="small"
                />
              ))}
            </Box>
          </Grid>
        </Grid>
      </DialogContent>
      
      <DialogActions sx={{ p: 2 }}>
        <Button onClick={closeFormModal}>Cancel</Button>
        <Button onClick={handleSubmit} variant="contained">
          {editingTodo ? 'Update' : 'Create'} Todo
        </Button>
      </DialogActions>
    </Dialog>
  );
}
```

## Molecule Components

### TodoItem Component

```typescript
// components/molecules/TodoItem.tsx
import { useState, memo } from 'react';
import {
  Card,
  CardContent,
  Box,
  Typography,
  Checkbox,
  IconButton,
  Chip,
  Collapse,
  Menu,
  MenuItem,
  Tooltip
} from '@mui/material';
import {
  MoreVert as MoreIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  DragIndicator as DragIcon,
  Schedule as ScheduleIcon,
  Flag as FlagIcon
} from '@mui/icons-material';
import { PriorityBadge } from '@/components/atoms/PriorityBadge';
import { CategoryChip } from '@/components/atoms/CategoryChip';
import { DueDateDisplay } from '@/components/atoms/DueDateDisplay';
import { useTodoStore } from '@/store/todoStore';
import { TodoItem as TodoType, TodoStatus } from '@/types';

interface TodoItemProps {
  todo: TodoType;
  selected: boolean;
  expanded: boolean;
  onSelect: (id: string) => void;
  onToggleExpand: (id: string) => void;
}

export const TodoItem = memo(function TodoItem({
  todo,
  selected,
  expanded,
  onSelect,
  onToggleExpand
}: TodoItemProps) {
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const { toggleComplete, deleteTodo, openEditModal } = useTodoStore();

  const isCompleted = todo.status === TodoStatus.COMPLETED;
  const isOverdue = todo.dueDate && new Date(todo.dueDate) < new Date() && !isCompleted;

  const handleComplete = () => {
    toggleComplete(todo.id);
  };

  const handleEdit = () => {
    openEditModal(todo);
    setAnchorEl(null);
  };

  const handleDelete = () => {
    deleteTodo(todo.id);
    setAnchorEl(null);
  };

  return (
    <Card
      elevation={selected ? 2 : 0}
      sx={{
        backgroundColor: theme => {
          if (isOverdue) return theme.palette.error.light + '20';
          if (selected) return theme.palette.action.selected;
          return 'background.paper';
        },
        opacity: isCompleted ? 0.7 : 1,
        transition: 'all 0.2s ease'
      }}
    >
      <CardContent sx={{ py: 1.5 }}>
        <Box display="flex" alignItems="flex-start" gap={1}>
          <DragIcon 
            sx={{ 
              cursor: 'grab',
              color: 'text.secondary',
              mt: 0.5
            }} 
          />
          
          <Checkbox
            checked={isCompleted}
            onChange={handleComplete}
            size="small"
          />
          
          <Box flex={1}>
            <Box 
              display="flex" 
              alignItems="center" 
              gap={1}
              onClick={() => onToggleExpand(todo.id)}
              sx={{ cursor: 'pointer' }}
            >
              <Typography
                variant="body1"
                sx={{
                  textDecoration: isCompleted ? 'line-through' : 'none',
                  color: isCompleted ? 'text.secondary' : 'text.primary'
                }}
              >
                {todo.title}
              </Typography>
              
              <PriorityBadge priority={todo.priority} />
              <CategoryChip categoryId={todo.category} />
              {todo.dueDate && <DueDateDisplay date={todo.dueDate} />}
            </Box>
            
            <Collapse in={expanded}>
              <Box mt={1}>
                {todo.description && (
                  <Typography variant="body2" color="text.secondary" paragraph>
                    {todo.description}
                  </Typography>
                )}
                
                {todo.tags.length > 0 && (
                  <Box display="flex" gap={0.5} mb={1}>
                    {todo.tags.map((tag) => (
                      <Chip key={tag} label={tag} size="small" variant="outlined" />
                    ))}
                  </Box>
                )}
                
                <Typography variant="caption" color="text.secondary">
                  Created: {new Date(todo.createdAt).toLocaleDateString()}
                  {todo.completedAt && (
                    <> • Completed: {new Date(todo.completedAt).toLocaleDateString()}</>
                  )}
                </Typography>
              </Box>
            </Collapse>
          </Box>
          
          <Box display="flex" gap={0.5}>
            <Checkbox
              checked={selected}
              onChange={() => onSelect(todo.id)}
              size="small"
              sx={{ display: selected ? 'block' : 'none' }}
            />
            
            <IconButton size="small" onClick={(e) => setAnchorEl(e.currentTarget)}>
              <MoreIcon />
            </IconButton>
          </Box>
        </Box>
      </CardContent>
      
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={() => setAnchorEl(null)}
      >
        <MenuItem onClick={handleEdit}>
          <EditIcon fontSize="small" sx={{ mr: 1 }} />
          Edit
        </MenuItem>
        <MenuItem onClick={handleDelete}>
          <DeleteIcon fontSize="small" sx={{ mr: 1 }} />
          Delete
        </MenuItem>
      </Menu>
    </Card>
  );
});
```

## Atom Components

### Priority Badge

```typescript
// components/atoms/PriorityBadge.tsx
import { Chip } from '@mui/material';
import { Flag as FlagIcon } from '@mui/icons-material';
import { Priority } from '@/types';

interface PriorityBadgeProps {
  priority: Priority;
  size?: 'small' | 'medium';
}

export function PriorityBadge({ priority, size = 'small' }: PriorityBadgeProps) {
  const colors = {
    [Priority.HIGH]: '#F44336',
    [Priority.MEDIUM]: '#FF9800',
    [Priority.LOW]: '#4CAF50'
  };

  const labels = {
    [Priority.HIGH]: 'High',
    [Priority.MEDIUM]: 'Medium',
    [Priority.LOW]: 'Low'
  };

  return (
    <Chip
      icon={<FlagIcon />}
      label={labels[priority]}
      size={size}
      sx={{
        backgroundColor: colors[priority] + '20',
        color: colors[priority],
        '& .MuiChip-icon': {
          color: colors[priority]
        }
      }}
    />
  );
}
```

## Custom Hooks

### useTodos Hook

```typescript
// hooks/useTodos.ts
import { useCallback, useEffect } from 'react';
import { useTodoStore } from '@/store/todoStore';
import { TodoService } from '@/services/TodoService';
import { CreateTodoDto, UpdateTodoDto } from '@/types';

export function useTodos() {
  const {
    todos,
    loading,
    error,
    setTodos,
    setLoading,
    setError
  } = useTodoStore();

  const todoService = new TodoService();

  const loadTodos = useCallback(async () => {
    setLoading(true);
    try {
      const data = await todoService.getAll();
      setTodos(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  const createTodo = useCallback(async (dto: CreateTodoDto) => {
    try {
      const newTodo = await todoService.create(dto);
      setTodos([...todos, newTodo]);
      return newTodo;
    } catch (err) {
      setError(err.message);
      throw err;
    }
  }, [todos]);

  const updateTodo = useCallback(async (id: string, updates: UpdateTodoDto) => {
    try {
      const updatedTodo = await todoService.update(id, updates);
      setTodos(todos.map(t => t.id === id ? updatedTodo : t));
      return updatedTodo;
    } catch (err) {
      setError(err.message);
      throw err;
    }
  }, [todos]);

  const deleteTodo = useCallback(async (id: string) => {
    try {
      await todoService.delete(id);
      setTodos(todos.filter(t => t.id !== id));
    } catch (err) {
      setError(err.message);
      throw err;
    }
  }, [todos]);

  const toggleComplete = useCallback(async (id: string) => {
    try {
      const updatedTodo = await todoService.toggleComplete(id);
      setTodos(todos.map(t => t.id === id ? updatedTodo : t));
      return updatedTodo;
    } catch (err) {
      setError(err.message);
      throw err;
    }
  }, [todos]);

  useEffect(() => {
    loadTodos();
  }, []);

  return {
    todos,
    loading,
    error,
    createTodo,
    updateTodo,
    deleteTodo,
    toggleComplete,
    refresh: loadTodos
  };
}
```

### useLocalStorage Hook

```typescript
// hooks/useLocalStorage.ts
import { useState, useEffect, useCallback } from 'react';

export function useLocalStorage<T>(
  key: string,
  initialValue: T,
  options?: {
    serialize?: (value: T) => string;
    deserialize?: (value: string) => T;
  }
) {
  const serialize = options?.serialize || JSON.stringify;
  const deserialize = options?.deserialize || JSON.parse;

  const [storedValue, setStoredValue] = useState<T>(() => {
    if (typeof window === 'undefined') {
      return initialValue;
    }

    try {
      const item = window.localStorage.getItem(key);
      return item ? deserialize(item) : initialValue;
    } catch (error) {
      console.error(`Error loading ${key} from localStorage:`, error);
      return initialValue;
    }
  });

  const setValue = useCallback((value: T | ((val: T) => T)) => {
    try {
      const valueToStore = value instanceof Function ? value(storedValue) : value;
      setStoredValue(valueToStore);
      
      if (typeof window !== 'undefined') {
        window.localStorage.setItem(key, serialize(valueToStore));
      }
    } catch (error) {
      console.error(`Error saving ${key} to localStorage:`, error);
    }
  }, [key, serialize, storedValue]);

  const removeValue = useCallback(() => {
    try {
      setStoredValue(initialValue);
      if (typeof window !== 'undefined') {
        window.localStorage.removeItem(key);
      }
    } catch (error) {
      console.error(`Error removing ${key} from localStorage:`, error);
    }
  }, [key, initialValue]);

  useEffect(() => {
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === key && e.newValue !== null) {
        setStoredValue(deserialize(e.newValue));
      }
    };

    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, [key, deserialize]);

  return [storedValue, setValue, removeValue] as const;
}
```

### useKeyboardShortcuts Hook

```typescript
// hooks/useKeyboardShortcuts.ts
import { useEffect, useCallback } from 'react';
import { useUIStore } from '@/store/uiStore';
import { useFilterStore } from '@/store/filterStore';

interface ShortcutConfig {
  key: string;
  ctrl?: boolean;
  shift?: boolean;
  alt?: boolean;
  action: () => void;
  description: string;
}

export function useKeyboardShortcuts() {
  const { openFormModal, toggleTheme, toggleSidebar } = useUIStore();
  const { setSearchQuery } = useFilterStore();

  const shortcuts: ShortcutConfig[] = [
    {
      key: 'n',
      action: openFormModal,
      description: 'Create new todo'
    },
    {
      key: 'f',
      ctrl: true,
      action: () => {
        const searchInput = document.querySelector('[data-search-input]');
        if (searchInput) (searchInput as HTMLInputElement).focus();
      },
      description: 'Focus search'
    },
    {
      key: 'd',
      ctrl: true,
      action: toggleTheme,
      description: 'Toggle dark mode'
    },
    {
      key: 'b',
      ctrl: true,
      action: toggleSidebar,
      description: 'Toggle sidebar'
    },
    {
      key: 'Escape',
      action: () => {
        setSearchQuery('');
        // Close any open modals
      },
      description: 'Clear search / Close modal'
    }
  ];

  const handleKeyDown = useCallback((event: KeyboardEvent) => {
    // Ignore if typing in an input
    if (
      event.target instanceof HTMLInputElement ||
      event.target instanceof HTMLTextAreaElement
    ) {
      return;
    }

    shortcuts.forEach(shortcut => {
      const matchesKey = event.key.toLowerCase() === shortcut.key.toLowerCase();
      const matchesCtrl = shortcut.ctrl ? event.ctrlKey || event.metaKey : true;
      const matchesShift = shortcut.shift ? event.shiftKey : true;
      const matchesAlt = shortcut.alt ? event.altKey : true;

      if (matchesKey && matchesCtrl && matchesShift && matchesAlt) {
        event.preventDefault();
        shortcut.action();
      }
    });
  }, [shortcuts]);

  const registerShortcuts = useCallback(() => {
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [handleKeyDown]);

  return {
    shortcuts,
    registerShortcuts
  };
}
```

## Theme Configuration

### Material-UI Theme

```typescript
// styles/theme.ts
import { createTheme, ThemeOptions } from '@mui/material/styles';

const lightTheme: ThemeOptions = {
  palette: {
    mode: 'light',
    primary: {
      main: '#1976D2',
      light: '#42A5F5',
      dark: '#1565C0'
    },
    secondary: {
      main: '#388E3C',
      light: '#66BB6A',
      dark: '#2E7D32'
    },
    error: {
      main: '#D32F2F',
      light: '#EF5350',
      dark: '#C62828'
    },
    warning: {
      main: '#F57C00',
      light: '#FFB74D',
      dark: '#E65100'
    },
    info: {
      main: '#0288D1',
      light: '#4FC3F7',
      dark: '#01579B'
    },
    success: {
      main: '#388E3C',
      light: '#66BB6A',
      dark: '#2E7D32'
    },
    background: {
      default: '#FAFAFA',
      paper: '#FFFFFF'
    }
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontSize: '2.5rem',
      fontWeight: 500
    },
    h2: {
      fontSize: '2rem',
      fontWeight: 500
    },
    h3: {
      fontSize: '1.75rem',
      fontWeight: 500
    },
    h4: {
      fontSize: '1.5rem',
      fontWeight: 500
    },
    h5: {
      fontSize: '1.25rem',
      fontWeight: 500
    },
    h6: {
      fontSize: '1rem',
      fontWeight: 500
    }
  },
  shape: {
    borderRadius: 8
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          borderRadius: 8
        }
      }
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          boxShadow: '0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24)'
        }
      }
    },
    MuiTextField: {
      defaultProps: {
        variant: 'outlined'
      }
    }
  }
};

const darkTheme: ThemeOptions = {
  ...lightTheme,
  palette: {
    ...lightTheme.palette,
    mode: 'dark',
    background: {
      default: '#121212',
      paper: '#1E1E1E'
    },
    text: {
      primary: '#FFFFFF',
      secondary: '#B0B0B0'
    }
  }
};

export const getTheme = (mode: 'light' | 'dark') => {
  return createTheme(mode === 'light' ? lightTheme : darkTheme);
};
```

## Mobile Responsive Components

### Mobile Navigation

```typescript
// components/organisms/MobileNavigation.tsx
import { BottomNavigation, BottomNavigationAction, Paper } from '@mui/material';
import {
  Home as HomeIcon,
  BarChart as StatsIcon,
  Search as SearchIcon,
  Settings as SettingsIcon
} from '@mui/icons-material';
import { useRouter } from 'next/navigation';
import { useUIStore } from '@/store/uiStore';

export function MobileNavigation() {
  const router = useRouter();
  const { activeTab, setActiveTab } = useUIStore();

  return (
    <Paper
      sx={{
        position: 'fixed',
        bottom: 0,
        left: 0,
        right: 0,
        zIndex: 1000
      }}
      elevation={3}
    >
      <BottomNavigation
        value={activeTab}
        onChange={(_, newValue) => setActiveTab(newValue)}
        showLabels
      >
        <BottomNavigationAction
          label="Home"
          icon={<HomeIcon />}
          value="home"
        />
        <BottomNavigationAction
          label="Stats"
          icon={<StatsIcon />}
          value="stats"
        />
        <BottomNavigationAction
          label="Search"
          icon={<SearchIcon />}
          value="search"
        />
        <BottomNavigationAction
          label="Settings"
          icon={<SettingsIcon />}
          value="settings"
        />
      </BottomNavigation>
    </Paper>
  );
}
```

## Performance Optimizations

### Virtual List Component

```typescript
// components/molecules/VirtualList.tsx
import { useRef, useEffect, useState } from 'react';
import { FixedSizeList as List } from 'react-window';
import AutoSizer from 'react-virtualized-auto-sizer';
import { Box } from '@mui/material';

interface VirtualListProps<T> {
  items: T[];
  itemHeight: number;
  renderItem: (item: T, index: number) => React.ReactNode;
  overscan?: number;
}

export function VirtualList<T>({
  items,
  itemHeight,
  renderItem,
  overscan = 5
}: VirtualListProps<T>) {
  const listRef = useRef<List>(null);

  const Row = ({ index, style }: { index: number; style: React.CSSProperties }) => (
    <div style={style}>
      {renderItem(items[index], index)}
    </div>
  );

  return (
    <Box sx={{ height: '100%', minHeight: 400 }}>
      <AutoSizer>
        {({ height, width }) => (
          <List
            ref={listRef}
            height={height}
            itemCount={items.length}
            itemSize={itemHeight}
            width={width}
            overscanCount={overscan}
          >
            {Row}
          </List>
        )}
      </AutoSizer>
    </Box>
  );
}
```

## Accessibility Features

### Accessible Todo Item

```typescript
// Accessibility enhancements for TodoItem
<Card
  role="article"
  aria-label={`Todo: ${todo.title}`}
  aria-describedby={`todo-desc-${todo.id}`}
  tabIndex={0}
  onKeyDown={(e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      onToggleExpand(todo.id);
    }
  }}
>
  <Checkbox
    inputProps={{
      'aria-label': `Mark ${todo.title} as ${isCompleted ? 'incomplete' : 'complete'}`
    }}
  />
  
  <Typography id={`todo-desc-${todo.id}`} className="sr-only">
    {todo.description || 'No description'}
    Priority: {todo.priority}
    Category: {todo.category}
    {todo.dueDate && `Due: ${new Date(todo.dueDate).toLocaleDateString()}`}
  </Typography>
</Card>
```

---

*Document Version: 1.0.0*  
*Last Updated: 2025-01-21*  
*Status: Complete - Implementation Ready*