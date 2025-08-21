# Todo Application - Wireframes

## Overview
This document contains ASCII-art wireframes for all major screens and components of the todo application, following Material Design principles.

## Desktop Layout (1440px width)

### Main Application View - Empty State
```
┌────────────────────────────────────────────────────────────────────────────┐
│ ┌──────────────────────────────────────────────────────────────────────┐   │
│ │  ☰  Todo App                                    🔍 Search  ☀️ 📊 ⚙️   │   │
│ └──────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│ ┌─────────────────┬────────────────────────────────────────────────────┐   │
│ │                 │                                                     │   │
│ │  FILTERS        │                                                     │   │
│ │                 │         ┌──────────────────────────────┐           │   │
│ │  Status         │         │                              │           │   │
│ │  ○ All (0)      │         │     📝                       │           │   │
│ │  ○ Active (0)   │         │                              │           │   │
│ │  ○ Done (0)     │         │     No todos yet!           │           │   │
│ │                 │         │                              │           │   │
│ │  Priority       │         │     Create your first todo   │           │   │
│ │  □ High         │         │     to get started          │           │   │
│ │  □ Medium       │         │                              │           │   │
│ │  □ Low          │         │     [ + Add Todo ]          │           │   │
│ │                 │         │                              │           │   │
│ │  Categories     │         └──────────────────────────────┘           │   │
│ │  □ Work         │                                                     │   │
│ │  □ Personal     │                                                     │   │
│ │  □ Shopping     │                                                     │   │
│ │  □ Health       │                                                     │   │
│ │                 │                                                     │   │
│ │  Due Date       │                                                     │   │
│ │  ○ Any Time     │                                                     │   │
│ │  ○ Overdue      │                                                     │   │
│ │  ○ Today        │                                                     │   │
│ │  ○ This Week    │                                                     │   │
│ │                 │                                                     │   │
│ │  [Clear Filters]│                                          [+]        │   │
│ └─────────────────┴────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────────────────────┘

Legend:
☰ - Menu/Hamburger    🔍 - Search    ☀️ - Theme Toggle
📊 - Statistics       ⚙️ - Settings   [+] - Floating Action Button
```

### Main Application View - With Todos
```
┌────────────────────────────────────────────────────────────────────────────┐
│ ┌──────────────────────────────────────────────────────────────────────┐   │
│ │  ☰  Todo App                           🔍 Search todos...  ☀️ 📊 ⚙️   │   │
│ └──────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│ ┌─────────────────┬────────────────────────────────────────────────────┐   │
│ │  FILTERS        │  Showing 5 todos              Sort: Priority ↓      │   │
│ │                 │ ┌──────────────────────────────────────────────┐   │   │
│ │  Status         │ │ □ Complete project documentation              │   │   │
│ │  ● All (5)      │ │   🔴 High  📁 Work  📅 Today                 │   │   │
│ │  ○ Active (3)   │ │   Click to expand details...          ⋮ ✏️ 🗑️│   │   │
│ │  ○ Done (2)     │ └──────────────────────────────────────────────┘   │   │
│ │                 │                                                     │   │
│ │  Priority       │ ┌──────────────────────────────────────────────┐   │   │
│ │  ☑ High (2)     │ │ □ Review pull requests                       │   │   │
│ │  □ Medium (2)   │ │   🔴 High  📁 Work  📅 Overdue (2 days)      │   │   │
│ │  □ Low (1)      │ │   Need to review 3 pending PRs        ⋮ ✏️ 🗑️│   │   │
│ │                 │ └──────────────────────────────────────────────┘   │   │
│ │  Categories     │                                                     │   │
│ │  ☑ Work (3)     │ ┌──────────────────────────────────────────────┐   │   │
│ │  ☑ Personal (2) │ │ □ Buy groceries                              │   │   │
│ │  □ Shopping     │ │   🟠 Medium  📁 Personal  📅 Tomorrow        │   │   │
│ │  □ Health       │ │   Milk, eggs, bread, coffee          ⋮ ✏️ 🗑️│   │   │
│ │                 │ └──────────────────────────────────────────────┘   │   │
│ │  Due Date       │                                                     │   │
│ │  ● Any Time     │ ┌──────────────────────────────────────────────┐   │   │
│ │  ○ Overdue (1)  │ │ ☑ ̶C̶a̶l̶l̶ ̶d̶e̶n̶t̶i̶s̶t̶                             │   │   │
│ │  ○ Today (1)    │ │   🟢 Low  📁 Personal  ✓ Completed today     │   │   │
│ │  ○ This Week    │ │   Appointment scheduled for next week ⋮ ✏️ 🗑️│   │   │
│ │                 │ └──────────────────────────────────────────────┘   │   │
│ │  [Clear]        │                                                     │   │
│ │                 │ ┌──────────────────────────────────────────────┐   │   │
│ │  STATISTICS     │ │ ☑ ̶F̶i̶n̶i̶s̶h̶ ̶r̶e̶p̶o̶r̶t̶                           │   │   │
│ │  ─────────      │ │   🟠 Medium  📁 Work  ✓ Completed yesterday  │   │   │
│ │  Total: 5       │ │   Q3 report submitted to management   ⋮ ✏️ 🗑️│   │   │
│ │  Active: 3      │ └──────────────────────────────────────────────┘   │   │
│ │  Done: 2        │                                                     │   │
│ │  Today: 1       │                                          [+]        │   │
│ └─────────────────┴────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────────────────────┘
```

### Todo Creation Modal
```
┌────────────────────────────────────────────────────────────────────────────┐
│ ┌──────────────────────────────────────────────────────────────────────┐   │
│ │  Create New Todo                                                  [X] │   │
│ ├──────────────────────────────────────────────────────────────────────┤   │
│ │                                                                        │   │
│ │  Title *                                                              │   │
│ │  ┌──────────────────────────────────────────────────────────────┐    │   │
│ │  │ Enter todo title...                                          │    │   │
│ │  └──────────────────────────────────────────────────────────────┘    │   │
│ │                                                                        │   │
│ │  Description                                                          │   │
│ │  ┌──────────────────────────────────────────────────────────────┐    │   │
│ │  │ Add more details...                                          │    │   │
│ │  │                                                              │    │   │
│ │  │                                                              │    │   │
│ │  └──────────────────────────────────────────────────────────────┘    │   │
│ │                                                                        │   │
│ │  Priority              Category                                       │   │
│ │  ┌─────────────┐      ┌─────────────────┐                           │   │
│ │  │ Medium    ▼ │      │ General       ▼ │                           │   │
│ │  └─────────────┘      └─────────────────┘                           │   │
│ │                                                                        │   │
│ │  Due Date                           Time (Optional)                   │   │
│ │  ┌─────────────────┐               ┌─────────────┐                   │   │
│ │  │ 📅 Select date  │               │ 🕐 --:--    │                   │   │
│ │  └─────────────────┘               └─────────────┘                   │   │
│ │                                                                        │   │
│ │  Tags (Optional, max 3)                                              │   │
│ │  ┌──────────────────────────────────────────────────────────────┐    │   │
│ │  │ Type to add tags...                                          │    │   │
│ │  └──────────────────────────────────────────────────────────────┘    │   │
│ │  Suggestions: urgent, important, quick, recurring                     │   │
│ │                                                                        │   │
│ │  ┌─────────────────────┐  ┌─────────────────────┐                   │   │
│ │  │      Cancel         │  │    Create Todo      │                   │   │
│ │  └─────────────────────┘  └─────────────────────┘                   │   │
│ └──────────────────────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────────────────────┘
```

### Statistics Panel (Expanded)
```
┌────────────────────────────────────────────────────────────────────────────┐
│ ┌──────────────────────────────────────────────────────────────────────┐   │
│ │  Statistics Dashboard                           Period: This Week [▼] │   │
│ ├──────────────────────────────────────────────────────────────────────┤   │
│ │                                                                        │   │
│ │  ┌───────────┬───────────┬───────────┬───────────┐                   │   │
│ │  │  Total    │  Active   │ Completed │  Overdue  │                   │   │
│ │  │    25     │    15     │    10     │     3     │                   │   │
│ │  │  tasks    │   60%     │   40%     │   12%     │                   │   │
│ │  └───────────┴───────────┴───────────┴───────────┘                   │   │
│ │                                                                        │   │
│ │  Completion Rate                    Daily Average                      │   │
│ │  ┌────────────────────────┐       ┌────────────────────────┐         │   │
│ │  │ ████████████░░░░  67%  │       │ Created: 3.5          │         │   │
│ │  └────────────────────────┘       │ Completed: 2.1        │         │   │
│ │                                    └────────────────────────┘         │   │
│ │                                                                        │   │
│ │  Tasks by Priority                 Tasks by Category                  │   │
│ │  ┌────────────────────────┐       ┌────────────────────────┐         │   │
│ │  │ High    ████ 8         │       │ Work     ████████ 12   │         │   │
│ │  │ Medium  ██████ 12      │       │ Personal ████ 8        │         │   │
│ │  │ Low     ██ 5           │       │ Shopping ██ 3          │         │   │
│ │  └────────────────────────┘       │ Health   █ 2          │         │   │
│ │                                    └────────────────────────┘         │   │
│ │                                                                        │   │
│ │  Productivity Trend (7 days)                                          │   │
│ │  ┌────────────────────────────────────────────────────────┐          │   │
│ │  │    10 │     ╱╲                                         │          │   │
│ │  │     8 │    ╱  ╲    ╱╲                                 │          │   │
│ │  │     6 │   ╱    ╲  ╱  ╲                                │          │   │
│ │  │     4 │  ╱      ╲╱    ╲                               │          │   │
│ │  │     2 │ ╱              ╲___╱                          │          │   │
│ │  │     0 └────┬───┬───┬───┬───┬───┬───┐                 │          │   │
│ │  │       Mon  Tue Wed Thu Fri Sat Sun                    │          │   │
│ │  └────────────────────────────────────────────────────────┘          │   │
│ │                                                                        │   │
│ │  Current Streak: 🔥 5 days          Best Streak: 12 days             │   │
│ │                                                           [Close]      │   │
│ └──────────────────────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────────────────────┘
```

## Mobile Layout (375px width)

### Mobile Main View
```
┌─────────────────────────┐
│ ┌─────────────────────┐ │
│ │ ☰ Todo App      ⋮  │ │
│ ├─────────────────────┤ │
│ │ 🔍 Search todos...  │ │
│ └─────────────────────┘ │
│                          │
│ ┌─────────────────────┐ │
│ │ Active (3) ▼        │ │
│ └─────────────────────┘ │
│                          │
│ ┌─────────────────────┐ │
│ │ □ Project docs      │ │
│ │ 🔴 Work • Today     │ │
│ ├─────────────────────┤ │
│ │ □ Review PRs        │ │
│ │ 🔴 Work • Overdue   │ │
│ ├─────────────────────┤ │
│ │ □ Buy groceries     │ │
│ │ 🟠 Personal • Tmrw  │ │
│ ├─────────────────────┤ │
│ │ ☑ Call dentist      │ │
│ │ 🟢 Personal • Done  │ │
│ └─────────────────────┘ │
│                          │
│         [ + ]            │
│                          │
│ ┌─────────────────────┐ │
│ │ 🏠  📊  🔍  ⚙️     │ │
│ └─────────────────────┘ │
└─────────────────────────┘

Bottom Navigation:
🏠 - Home
📊 - Stats  
🔍 - Search
⚙️ - Settings
```

### Mobile Todo Expanded
```
┌─────────────────────────┐
│ ┌─────────────────────┐ │
│ │ ← Todo Details      │ │
│ └─────────────────────┘ │
│                          │
│ ┌─────────────────────┐ │
│ │ □ Complete project  │ │
│ │    documentation    │ │
│ │                     │ │
│ │ 🔴 High Priority    │ │
│ │ 📁 Work             │ │
│ │ 📅 Due Today 5pm    │ │
│ │                     │ │
│ │ Description:        │ │
│ │ Need to finish the  │ │
│ │ requirements doc    │ │
│ │ and user stories    │ │
│ │ before standup.     │ │
│ │                     │ │
│ │ Tags:               │ │
│ │ [urgent] [docs]     │ │
│ │                     │ │
│ │ Created: 2 days ago │ │
│ │ Updated: 1 hour ago │ │
│ │                     │ │
│ │ ┌─────────────────┐ │ │
│ │ │   ✏️ Edit       │ │ │
│ │ └─────────────────┘ │ │
│ │ ┌─────────────────┐ │ │
│ │ │   🗑️ Delete    │ │ │
│ │ └─────────────────┘ │ │
│ └─────────────────────┘ │
└─────────────────────────┘
```

### Mobile Filter Drawer
```
┌─────────────────────────┐
│ ┌─────────────────────┐ │
│ │ Filters          X  │ │
│ ├─────────────────────┤ │
│ │                     │ │
│ │ Status              │ │
│ │ ● All               │ │
│ │ ○ Active            │ │
│ │ ○ Completed         │ │
│ │                     │ │
│ │ Priority            │ │
│ │ □ High              │ │
│ │ ☑ Medium            │ │
│ │ □ Low               │ │
│ │                     │ │
│ │ Categories          │ │
│ │ ☑ Work              │ │
│ │ ☑ Personal          │ │
│ │ □ Shopping          │ │
│ │ □ Health            │ │
│ │ □ Finance           │ │
│ │                     │ │
│ │ Due Date            │ │
│ │ ○ Any Time          │ │
│ │ ● Today             │ │
│ │ ○ This Week         │ │
│ │ ○ Overdue           │ │
│ │                     │ │
│ │ ┌─────────────────┐ │ │
│ │ │  Clear Filters  │ │ │
│ │ └─────────────────┘ │ │
│ │ ┌─────────────────┐ │ │
│ │ │  Apply Filters  │ │ │
│ │ └─────────────────┘ │ │
│ └─────────────────────┘ │
└─────────────────────────┘
```

## Component Details

### Todo Item States
```
Normal State:
┌────────────────────────────────────┐
│ □ Todo title text                  │
│   🔴 Priority  📁 Category  📅 Due │
└────────────────────────────────────┘

Hover State:
┌────────────────────────────────────┐
│ □ Todo title text          ⋮ ✏️ 🗑️│
│   🔴 Priority  📁 Category  📅 Due │
└────────────────────────────────────┘

Selected State:
┌────────────────────────────────────┐
│ ☑ Todo title text          ⋮ ✏️ 🗑️│ ← Highlighted background
│   🔴 Priority  📁 Category  📅 Due │
└────────────────────────────────────┘

Completed State:
┌────────────────────────────────────┐
│ ☑ ̶T̶o̶d̶o̶ ̶t̶i̶t̶l̶e̶ ̶t̶e̶x̶t̶          ⋮ ✏️ 🗑️│
│   ✓ Completed 2 hours ago         │
└────────────────────────────────────┘

Overdue State:
┌────────────────────────────────────┐
│ □ Todo title text          ⋮ ✏️ 🗑️│ ← Red tinted background
│   🔴 High  📁 Work  ⚠️ 2 days late│
└────────────────────────────────────┘
```

### Priority Indicators
```
🔴 High Priority - #F44336
🟠 Medium Priority - #FF9800  
🟢 Low Priority - #4CAF50
```

### Action Buttons
```
Primary Action (Material FAB):
     ┌─────┐
     │  +  │  Elevation: 6dp
     └─────┘  Color: Primary

Secondary Actions:
[Button Text]  - Contained button
[ Button ]     - Outlined button
 Button        - Text button

Icon Buttons:
✏️ Edit     🗑️ Delete    ⋮ More
📊 Stats    ⚙️ Settings  🔍 Search
```

### Form Elements
```
Text Input:
┌──────────────────────────┐
│ Label                    │
│ ________________________ │
│ Helper text              │
└──────────────────────────┘

Select Dropdown:
┌──────────────────────────┐
│ Selected Option       ▼  │
└──────────────────────────┘

Date Picker Trigger:
┌──────────────────────────┐
│ 📅 DD/MM/YYYY           │
└──────────────────────────┘

Checkbox:
□ Unchecked
☑ Checked
⬜ Indeterminate

Radio Button:
○ Unselected
● Selected
```

### Notification States
```
Success Toast:
┌────────────────────────────┐
│ ✓ Todo created successfully│
└────────────────────────────┘

Error Toast:
┌────────────────────────────┐
│ ⚠️ Failed to save todo     │
│ [Retry]  [Dismiss]         │
└────────────────────────────┘

Info Snackbar:
┌────────────────────────────┐
│ ℹ️ 3 todos marked complete │
│                    [Undo]  │
└────────────────────────────┘
```

### Empty States
```
No Todos:
┌──────────────────────┐
│                      │
│         📝           │
│                      │
│   No todos yet!      │
│                      │
│ Create your first    │
│ todo to get started  │
│                      │
│   [+ Add Todo]       │
│                      │
└──────────────────────┘

No Search Results:
┌──────────────────────┐
│                      │
│         🔍           │
│                      │
│   No matches found   │
│                      │
│ Try different search │
│ terms or filters     │
│                      │
│  [Clear Search]      │
│                      │
└──────────────────────┘

Error State:
┌──────────────────────┐
│                      │
│         ⚠️           │
│                      │
│  Something went      │
│  wrong               │
│                      │
│  [Try Again]         │
│                      │
└──────────────────────┘
```

### Loading States
```
Skeleton Screen:
┌────────────────────────┐
│ ▭▭▭▭▭▭▭▭▭▭▭▭▭▭▭▭      │
│ ▭▭▭▭▭  ▭▭▭▭  ▭▭▭▭     │
├────────────────────────┤
│ ▭▭▭▭▭▭▭▭▭▭▭▭▭▭▭       │
│ ▭▭▭▭▭  ▭▭▭▭  ▭▭▭▭     │
├────────────────────────┤
│ ▭▭▭▭▭▭▭▭▭▭▭▭▭▭        │
│ ▭▭▭▭▭  ▭▭▭▭  ▭▭▭▭     │
└────────────────────────┘

Progress Indicator:
Linear: ████████░░░░░░░░ 50%
Circular: ◐ Loading...
```

## Responsive Breakpoints

### Layout Grid
```
Mobile (320-767px):
- Single column
- 16px margins
- 8px gutters
- Bottom navigation

Tablet (768-1023px):
- 12 column grid
- Sidebar: 3 cols
- Content: 9 cols
- 24px margins

Desktop (1024-1439px):
- 12 column grid
- Sidebar: 3 cols
- Content: 9 cols
- 24px margins

Large Desktop (1440px+):
- 12 column grid
- Sidebar: 2 cols
- Content: 10 cols
- 24px margins
- Max width: 1920px
```

## Accessibility Considerations

### Focus States
```
Keyboard Focus Indicator:
┌────────────────────────┐
│ ┃ Focused Element    ┃ │ ← 2px solid outline
└────────────────────────┘

Tab Order:
1. Skip to main content
2. Header navigation
3. Search input
4. Filter panel
5. Todo list items
6. Floating action button
7. Footer navigation
```

### Screen Reader Landmarks
```
<header> - Application header
<nav> - Filter sidebar
<main> - Todo list container
<footer> - Statistics/navigation

ARIA Labels:
- aria-label="Create new todo"
- aria-label="Mark as complete"
- aria-label="Filter by priority"
- role="button"
- role="navigation"
- aria-live="polite" for updates
```

---

*Document Version: 1.0.0*  
*Last Updated: 2025-01-21*  
*Status: Complete*