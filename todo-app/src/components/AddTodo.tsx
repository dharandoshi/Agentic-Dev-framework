'use client';

import { useState } from 'react';
import {
  Box,
  TextField,
  Button,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Chip,
  Paper,
  Collapse,
  IconButton,
  Typography,
} from '@mui/material';
import {
  Add as AddIcon,
  ExpandMore as ExpandIcon,
  ExpandLess as CollapseIcon,
} from '@mui/icons-material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { Priority } from '@/types/todo';

interface AddTodoProps {
  onAdd: (
    title: string,
    description?: string,
    priority?: Priority,
    category?: string,
    tags?: string[],
    dueDate?: string
  ) => void;
  categories: string[];
}

export default function AddTodo({ onAdd, categories }: AddTodoProps) {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [priority, setPriority] = useState<Priority>('medium');
  const [category, setCategory] = useState('');
  const [newCategory, setNewCategory] = useState('');
  const [tags, setTags] = useState<string[]>([]);
  const [tagInput, setTagInput] = useState('');
  const [dueDate, setDueDate] = useState<Date | null>(null);
  const [showAdvanced, setShowAdvanced] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (title.trim()) {
      const finalCategory = newCategory.trim() || category;
      onAdd(
        title.trim(),
        description.trim() || undefined,
        priority,
        finalCategory || undefined,
        tags.length > 0 ? tags : undefined,
        dueDate ? dueDate.toISOString() : undefined
      );
      handleReset();
    }
  };

  const handleReset = () => {
    setTitle('');
    setDescription('');
    setPriority('medium');
    setCategory('');
    setNewCategory('');
    setTags([]);
    setTagInput('');
    setDueDate(null);
  };

  const handleAddTag = () => {
    if (tagInput.trim() && !tags.includes(tagInput.trim())) {
      setTags([...tags, tagInput.trim()]);
      setTagInput('');
    }
  };

  const handleRemoveTag = (tagToRemove: string) => {
    setTags(tags.filter(tag => tag !== tagToRemove));
  };

  return (
    <Paper sx={{ p: 2, mb: 2 }}>
      <form onSubmit={handleSubmit}>
        <Box sx={{ display: 'flex', gap: 1, mb: 1 }}>
          <TextField
            fullWidth
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="What needs to be done?"
            variant="outlined"
            size="small"
          />
          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>Priority</InputLabel>
            <Select
              value={priority}
              onChange={(e) => setPriority(e.target.value as Priority)}
              label="Priority"
            >
              <MenuItem value="low">Low</MenuItem>
              <MenuItem value="medium">Medium</MenuItem>
              <MenuItem value="high">High</MenuItem>
            </Select>
          </FormControl>
          <Button
            type="submit"
            variant="contained"
            startIcon={<AddIcon />}
            disabled={!title.trim()}
          >
            Add
          </Button>
        </Box>

        <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
          <IconButton
            size="small"
            onClick={() => setShowAdvanced(!showAdvanced)}
          >
            {showAdvanced ? <CollapseIcon /> : <ExpandIcon />}
          </IconButton>
          <Typography variant="caption" color="text.secondary">
            {showAdvanced ? 'Hide' : 'Show'} advanced options
          </Typography>
        </Box>

        <Collapse in={showAdvanced}>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
            <TextField
              fullWidth
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Description (optional)"
              variant="outlined"
              size="small"
              multiline
              rows={2}
            />

            <Box sx={{ display: 'flex', gap: 1 }}>
              {categories.length > 0 && (
                <FormControl size="small" sx={{ minWidth: 150 }}>
                  <InputLabel>Category</InputLabel>
                  <Select
                    value={category}
                    onChange={(e) => setCategory(e.target.value)}
                    label="Category"
                  >
                    <MenuItem value="">None</MenuItem>
                    {categories.map(cat => (
                      <MenuItem key={cat} value={cat}>{cat}</MenuItem>
                    ))}
                  </Select>
                </FormControl>
              )}
              <TextField
                value={newCategory}
                onChange={(e) => setNewCategory(e.target.value)}
                placeholder="New category"
                variant="outlined"
                size="small"
                sx={{ flex: 1 }}
              />
              <LocalizationProvider dateAdapter={AdapterDateFns}>
                <DatePicker
                  label="Due date"
                  value={dueDate}
                  onChange={setDueDate}
                  slotProps={{
                    textField: {
                      size: 'small',
                      variant: 'outlined',
                    },
                  }}
                />
              </LocalizationProvider>
            </Box>

            <Box>
              <Box sx={{ display: 'flex', gap: 1, mb: 1 }}>
                <TextField
                  value={tagInput}
                  onChange={(e) => setTagInput(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), handleAddTag())}
                  placeholder="Add tags"
                  variant="outlined"
                  size="small"
                  sx={{ flex: 1 }}
                />
                <Button onClick={handleAddTag} size="small">
                  Add Tag
                </Button>
              </Box>
              {tags.length > 0 && (
                <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                  {tags.map(tag => (
                    <Chip
                      key={tag}
                      label={tag}
                      size="small"
                      onDelete={() => handleRemoveTag(tag)}
                    />
                  ))}
                </Box>
              )}
            </Box>
          </Box>
        </Collapse>
      </form>
    </Paper>
  );
}