'use client';

import { useEffect, useState } from 'react';
import {
  Container,
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  Box,
  Tabs,
  Tab,
  Paper,
  Button,
  Menu,
  MenuItem,
  Divider,
  Badge,
  TextField,
  InputAdornment,
} from '@mui/material';
import {
  Brightness4 as DarkModeIcon,
  Brightness7 as LightModeIcon,
  FilterList as FilterIcon,
  Sort as SortIcon,
  Delete as DeleteIcon,
  CheckCircle as CheckIcon,
  Search as SearchIcon,
  Download as ExportIcon,
  Upload as ImportIcon,
  Dashboard as StatsIcon,
  Clear as ClearIcon,
} from '@mui/icons-material';
import { useTodoStore } from '@/store/todo.store';
import { useThemeMode } from './providers';
import TodoList from '@/components/TodoList';
import AddTodo from '@/components/AddTodo';
import { TodoFilters, TodoSort, Priority, TodoStatus } from '@/types/todo';

export default function Home() {
  const { toggleTheme, isDarkMode } = useThemeMode();
  const {
    todos,
    filters,
    sort,
    selectedTodos,
    loadTodos,
    createTodo,
    updateTodo,
    deleteTodo,
    deleteMultipleTodos,
    toggleTodoStatus,
    toggleMultipleTodosStatus,
    clearCompleted,
    setFilters,
    setSort,
    toggleSelection,
    selectAll,
    clearSelection,
    getFilteredTodos,
    getStatistics,
    exportTodos,
    importTodos,
  } = useTodoStore();

  const [searchQuery, setSearchQuery] = useState('');
  const [sortAnchor, setSortAnchor] = useState<null | HTMLElement>(null);
  const [filterAnchor, setFilterAnchor] = useState<null | HTMLElement>(null);
  const [statusFilter, setStatusFilter] = useState<TodoStatus | 'all'>('all');
  const [priorityFilter, setPriorityFilter] = useState<Priority | 'all'>('all');
  const [categoryFilter, setCategoryFilter] = useState<string>('');

  useEffect(() => {
    loadTodos();
  }, [loadTodos]);

  useEffect(() => {
    setFilters({
      status: statusFilter,
      priority: priorityFilter,
      category: categoryFilter || undefined,
      search: searchQuery || undefined,
    });
  }, [statusFilter, priorityFilter, categoryFilter, searchQuery, setFilters]);

  const filteredTodos = getFilteredTodos();
  const stats = getStatistics();
  const categories = [...new Set(todos.map(t => t.category).filter(Boolean))] as string[];

  const handleExport = () => {
    const data = exportTodos();
    const blob = new Blob([data], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `todos-${new Date().toISOString().split('T')[0]}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleImport = () => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.json';
    input.onchange = async (e) => {
      const file = (e.target as HTMLInputElement).files?.[0];
      if (file) {
        const text = await file.text();
        const result = importTodos(text);
        if (result.success) {
          alert(`Successfully imported ${result.imported} todos`);
        } else {
          alert(`Import failed: ${result.error}`);
        }
      }
    };
    input.click();
  };

  const handleBulkDelete = () => {
    if (selectedTodos.length > 0 && confirm(`Delete ${selectedTodos.length} selected todos?`)) {
      deleteMultipleTodos(selectedTodos);
      clearSelection();
    }
  };

  const handleBulkComplete = () => {
    if (selectedTodos.length > 0) {
      toggleMultipleTodosStatus(selectedTodos, 'completed');
      clearSelection();
    }
  };

  const handleTabChange = (_: React.SyntheticEvent, newValue: TodoStatus | 'all') => {
    setStatusFilter(newValue);
  };

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: 'background.default' }}>
      <AppBar position="static" elevation={0}>
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Todo App
          </Typography>
          
          <IconButton onClick={() => setSortAnchor(document.getElementById('stats-btn'))}>
            <Badge badgeContent={stats.total} color="secondary">
              <StatsIcon />
            </Badge>
          </IconButton>

          <IconButton onClick={handleExport}>
            <ExportIcon />
          </IconButton>

          <IconButton onClick={handleImport}>
            <ImportIcon />
          </IconButton>

          <IconButton onClick={toggleTheme} color="inherit">
            {isDarkMode ? <LightModeIcon /> : <DarkModeIcon />}
          </IconButton>
        </Toolbar>
      </AppBar>

      <Container maxWidth="md" sx={{ mt: 3 }}>
        <AddTodo onAdd={createTodo} categories={categories} />

        <Paper sx={{ mb: 2, p: 2 }}>
          <Box sx={{ display: 'flex', gap: 2, mb: 2, alignItems: 'center' }}>
            <TextField
              size="small"
              placeholder="Search todos..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon />
                  </InputAdornment>
                ),
              }}
              sx={{ flex: 1 }}
            />

            <IconButton onClick={(e) => setFilterAnchor(e.currentTarget)}>
              <Badge badgeContent={priorityFilter !== 'all' || categoryFilter ? '!' : 0} color="secondary">
                <FilterIcon />
              </Badge>
            </IconButton>

            <IconButton onClick={(e) => setSortAnchor(e.currentTarget)}>
              <SortIcon />
            </IconButton>

            {selectedTodos.length > 0 && (
              <>
                <Divider orientation="vertical" flexItem />
                <Button
                  size="small"
                  startIcon={<CheckIcon />}
                  onClick={handleBulkComplete}
                >
                  Complete ({selectedTodos.length})
                </Button>
                <Button
                  size="small"
                  color="error"
                  startIcon={<DeleteIcon />}
                  onClick={handleBulkDelete}
                >
                  Delete ({selectedTodos.length})
                </Button>
                <Button size="small" onClick={clearSelection}>
                  Clear
                </Button>
              </>
            )}

            {stats.completed > 0 && (
              <Button
                size="small"
                startIcon={<ClearIcon />}
                onClick={() => clearCompleted()}
              >
                Clear Completed
              </Button>
            )}
          </Box>

          <Tabs value={statusFilter} onChange={handleTabChange} aria-label="status filter tabs">
            <Tab label={`All (${stats.total})`} value="all" />
            <Tab label={`Active (${stats.active})`} value="active" />
            <Tab label={`Completed (${stats.completed})`} value="completed" />
            {stats.overdue > 0 && (
              <Tab label={`Overdue (${stats.overdue})`} value="overdue" disabled />
            )}
          </Tabs>
        </Paper>

        <TodoList
          todos={filteredTodos}
          onToggle={toggleTodoStatus}
          onUpdate={updateTodo}
          onDelete={deleteTodo}
          onSelect={toggleSelection}
          selectedTodos={selectedTodos}
        />

        {/* Sort Menu */}
        <Menu
          anchorEl={sortAnchor}
          open={Boolean(sortAnchor)}
          onClose={() => setSortAnchor(null)}
        >
          <MenuItem onClick={() => { setSort({ by: 'order', order: 'asc' }); setSortAnchor(null); }}>
            Default Order
          </MenuItem>
          <MenuItem onClick={() => { setSort({ by: 'title', order: 'asc' }); setSortAnchor(null); }}>
            Title (A-Z)
          </MenuItem>
          <MenuItem onClick={() => { setSort({ by: 'title', order: 'desc' }); setSortAnchor(null); }}>
            Title (Z-A)
          </MenuItem>
          <MenuItem onClick={() => { setSort({ by: 'priority', order: 'asc' }); setSortAnchor(null); }}>
            Priority (High First)
          </MenuItem>
          <MenuItem onClick={() => { setSort({ by: 'dueDate', order: 'asc' }); setSortAnchor(null); }}>
            Due Date (Earliest)
          </MenuItem>
          <MenuItem onClick={() => { setSort({ by: 'createdAt', order: 'desc' }); setSortAnchor(null); }}>
            Newest First
          </MenuItem>
        </Menu>

        {/* Filter Menu */}
        <Menu
          anchorEl={filterAnchor}
          open={Boolean(filterAnchor)}
          onClose={() => setFilterAnchor(null)}
        >
          <MenuItem disabled>
            <Typography variant="subtitle2">Priority Filter</Typography>
          </MenuItem>
          <MenuItem onClick={() => { setPriorityFilter('all'); setFilterAnchor(null); }}>
            All Priorities
          </MenuItem>
          <MenuItem onClick={() => { setPriorityFilter('high'); setFilterAnchor(null); }}>
            High Priority
          </MenuItem>
          <MenuItem onClick={() => { setPriorityFilter('medium'); setFilterAnchor(null); }}>
            Medium Priority
          </MenuItem>
          <MenuItem onClick={() => { setPriorityFilter('low'); setFilterAnchor(null); }}>
            Low Priority
          </MenuItem>
          <Divider />
          <MenuItem disabled>
            <Typography variant="subtitle2">Category Filter</Typography>
          </MenuItem>
          <MenuItem onClick={() => { setCategoryFilter(''); setFilterAnchor(null); }}>
            All Categories
          </MenuItem>
          {categories.map(cat => (
            <MenuItem key={cat} onClick={() => { setCategoryFilter(cat); setFilterAnchor(null); }}>
              {cat}
            </MenuItem>
          ))}
        </Menu>
      </Container>
    </Box>
  );
}
