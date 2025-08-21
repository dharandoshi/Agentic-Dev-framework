'use client';

import { useState } from 'react';
import {
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Checkbox,
  IconButton,
  Chip,
  Box,
  TextField,
  Typography,
} from '@mui/material';
import {
  Delete as DeleteIcon,
  Edit as EditIcon,
  Save as SaveIcon,
  Cancel as CancelIcon,
  DragIndicator as DragIcon,
} from '@mui/icons-material';
import { format, isPast } from 'date-fns';
import { Todo, Priority } from '@/types/todo';

interface TodoItemProps {
  todo: Todo;
  onToggle: (id: string) => void;
  onUpdate: (id: string, updates: Partial<Todo>) => void;
  onDelete: (id: string) => void;
  onSelect?: (id: string) => void;
  selected?: boolean;
}

const priorityColors: Record<Priority, 'error' | 'warning' | 'success'> = {
  high: 'error',
  medium: 'warning',
  low: 'success',
};

export default function TodoItem({
  todo,
  onToggle,
  onUpdate,
  onDelete,
  onSelect,
  selected = false,
}: TodoItemProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [editTitle, setEditTitle] = useState(todo.title);
  const [editDescription, setEditDescription] = useState(todo.description || '');

  const handleSave = () => {
    if (editTitle.trim()) {
      onUpdate(todo.id, {
        title: editTitle.trim(),
        description: editDescription.trim() || undefined,
      });
      setIsEditing(false);
    }
  };

  const handleCancel = () => {
    setEditTitle(todo.title);
    setEditDescription(todo.description || '');
    setIsEditing(false);
  };

  const isOverdue = todo.dueDate && todo.status === 'active' && isPast(new Date(todo.dueDate));

  if (isEditing) {
    return (
      <ListItem
        sx={{
          bgcolor: 'background.paper',
          mb: 1,
          borderRadius: 1,
        }}
      >
        <Box sx={{ width: '100%', p: 1 }}>
          <TextField
            fullWidth
            value={editTitle}
            onChange={(e) => setEditTitle(e.target.value)}
            placeholder="Todo title"
            variant="outlined"
            size="small"
            sx={{ mb: 1 }}
          />
          <TextField
            fullWidth
            value={editDescription}
            onChange={(e) => setEditDescription(e.target.value)}
            placeholder="Description (optional)"
            variant="outlined"
            size="small"
            multiline
            rows={2}
            sx={{ mb: 1 }}
          />
          <Box sx={{ display: 'flex', gap: 1 }}>
            <IconButton onClick={handleSave} color="primary" size="small">
              <SaveIcon />
            </IconButton>
            <IconButton onClick={handleCancel} size="small">
              <CancelIcon />
            </IconButton>
          </Box>
        </Box>
      </ListItem>
    );
  }

  return (
    <ListItem
      sx={{
        bgcolor: 'background.paper',
        mb: 1,
        borderRadius: 1,
        opacity: todo.status === 'completed' ? 0.7 : 1,
      }}
      secondaryAction={
        <Box sx={{ display: 'flex', gap: 0.5 }}>
          <IconButton
            edge="end"
            onClick={() => setIsEditing(true)}
            size="small"
          >
            <EditIcon />
          </IconButton>
          <IconButton
            edge="end"
            onClick={() => onDelete(todo.id)}
            size="small"
            color="error"
          >
            <DeleteIcon />
          </IconButton>
        </Box>
      }
      disablePadding
    >
      <ListItemButton
        role={undefined}
        onClick={() => onToggle(todo.id)}
        dense
      >
        <ListItemIcon>
          <Checkbox
            edge="start"
            checked={todo.status === 'completed'}
            tabIndex={-1}
            disableRipple
          />
        </ListItemIcon>
        <ListItemText
          primary={
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Typography
                variant="body1"
                sx={{
                  textDecoration: todo.status === 'completed' ? 'line-through' : 'none',
                  color: isOverdue ? 'error.main' : 'text.primary',
                }}
              >
                {todo.title}
              </Typography>
              <Chip
                label={todo.priority}
                size="small"
                color={priorityColors[todo.priority]}
                variant="outlined"
              />
              {todo.category && (
                <Chip
                  label={todo.category}
                  size="small"
                  variant="outlined"
                />
              )}
            </Box>
          }
          secondary={
            <Box>
              {todo.description && (
                <Typography variant="body2" color="text.secondary">
                  {todo.description}
                </Typography>
              )}
              {todo.dueDate && (
                <Typography
                  variant="caption"
                  color={isOverdue ? 'error' : 'text.secondary'}
                >
                  Due: {format(new Date(todo.dueDate), 'MMM dd, yyyy')}
                </Typography>
              )}
            </Box>
          }
        />
      </ListItemButton>
    </ListItem>
  );
}