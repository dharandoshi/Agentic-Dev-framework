'use client';

import { List, Typography, Box, Paper } from '@mui/material';
import TodoItem from './TodoItem';
import { Todo } from '@/types/todo';

interface TodoListProps {
  todos: Todo[];
  onToggle: (id: string) => void;
  onUpdate: (id: string, updates: Partial<Todo>) => void;
  onDelete: (id: string) => void;
  onSelect?: (id: string) => void;
  selectedTodos?: string[];
}

export default function TodoList({
  todos,
  onToggle,
  onUpdate,
  onDelete,
  onSelect,
  selectedTodos = [],
}: TodoListProps) {
  if (todos.length === 0) {
    return (
      <Paper
        sx={{
          p: 4,
          textAlign: 'center',
          bgcolor: 'background.paper',
        }}
      >
        <Typography variant="h6" color="text.secondary">
          No todos found
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
          Add a new todo to get started
        </Typography>
      </Paper>
    );
  }

  return (
    <List sx={{ width: '100%' }}>
      {todos.map((todo) => (
        <TodoItem
          key={todo.id}
          todo={todo}
          onToggle={onToggle}
          onUpdate={onUpdate}
          onDelete={onDelete}
          onSelect={onSelect}
          selected={selectedTodos.includes(todo.id)}
        />
      ))}
    </List>
  );
}