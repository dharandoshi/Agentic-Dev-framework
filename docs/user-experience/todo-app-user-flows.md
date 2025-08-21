# Todo Application - User Flow Diagrams

## Overview
This document provides visual representations of key user workflows in the todo application, showing the paths users take to accomplish various tasks.

## Primary User Flows

### 1. New User First Visit Flow
```
[User Opens App]
        |
        v
[Empty State Display]
  "Welcome! Create your first todo"
        |
        v
[Click "Add Todo" or press 'N']
        |
        v
[Todo Creation Form Opens]
        |
        ├─> [Enter Title (Required)]
        |         |
        |         v
        |   [Enter Description (Optional)]
        |         |
        |         v
        |   [Select Priority (Default: Medium)]
        |         |
        |         v
        |   [Select Category (Default: General)]
        |         |
        |         v
        |   [Set Due Date (Optional)]
        |         |
        |         v
        |   [Click Save / Press Enter]
        |         |
        |         v
        |   [Todo Added to List]
        |         |
        |         v
        |   [Saved to Local Storage]
        |         |
        |         v
        |   [Success Notification]
        |
        └─> [Click Cancel / Press Escape]
                  |
                  v
            [Return to List]
```

### 2. Todo Creation Flow
```
[Main Todo List View]
        |
        v
[Initiate Creation]
   ├─> Click FAB (+)
   ├─> Press 'N' key
   └─> Click "Add Todo" button
        |
        v
[Creation Modal/Form]
        |
        v
[Input Required Fields]
   └─> Title (mandatory)
        |
        v
[Input Optional Fields]
   ├─> Description
   ├─> Priority Selection
   ├─> Category Selection
   ├─> Tags (up to 3)
   └─> Due Date
        |
        v
[Validation Check]
        |
   ├─> [Valid] ──> [Save to Storage] ──> [Add to List] ──> [Close Form]
   |                                             |
   |                                             v
   |                                    [Show Success Toast]
   |
   └─> [Invalid] ──> [Show Error] ──> [Highlight Issues] ──> [Stay in Form]
```

### 3. Todo Completion Flow
```
[Todo List View]
        |
        v
[Incomplete Todo Item]
        |
        v
[User Clicks Checkbox]
        |
        v
[Update Status to Complete]
        |
        ├─> [Add Strikethrough Style]
        ├─> [Record Completion Time]
        ├─> [Update Statistics]
        └─> [Save to Storage]
                |
                v
        [Move to Bottom?]
                |
        ├─> [Yes (if preference set)]
        |       |
        |       v
        |   [Animate to Bottom]
        |
        └─> [No (keep position)]
                |
                v
        [Update Complete]

[Reverse Flow - Uncomplete]
[Completed Todo] -> [Click Checkbox] -> [Remove Strikethrough] -> [Update Status] -> [Save]
```

### 4. Search and Filter Flow
```
[Main Todo List]
        |
        v
[User Initiates Search/Filter]
        |
   ├─> [Type in Search Box]
   |         |
   |         v
   |   [Debounce 300ms]
   |         |
   |         v
   |   [Execute Search]
   |         |
   |         v
   |   [Filter Results]
   |         |
   |         v
   |   [Highlight Matches]
   |
   └─> [Click Filter Button]
             |
             v
       [Filter Panel Opens]
             |
             v
       [Select Filters]
          ├─> Status (All/Active/Completed)
          ├─> Priority (High/Medium/Low)
          ├─> Category (Dynamic List)
          └─> Due Date (Overdue/Today/Week)
             |
             v
       [Apply Filters]
             |
             v
       [Update List View]
             |
             v
       [Show Result Count]
             |
             v
       [Display Filter Badges]
```

### 5. Edit Todo Flow
```
[Todo Item in List]
        |
        v
[User Initiates Edit]
   ├─> Click on Todo Text
   ├─> Click Edit Icon
   └─> Select Todo + Press 'E'
        |
        v
[Enter Edit Mode]
        |
        ├─> [Inline Edit]
        |       |
        |       v
        |   [Fields Become Editable]
        |       |
        |       v
        |   [Make Changes]
        |       |
        |       v
        |   [Save or Cancel]
        |       |
        |   ├─> [Save (Enter/Blur)]
        |   |       |
        |   |       v
        |   |   [Validate Changes]
        |   |       |
        |   |       v
        |   |   [Update Storage]
        |   |       |
        |   |       v
        |   |   [Exit Edit Mode]
        |   |
        |   └─> [Cancel (Escape)]
        |           |
        |           v
        |       [Revert Changes]
        |           |
        |           v
        |       [Exit Edit Mode]
        |
        └─> [Modal Edit]
                |
                v
            [Open Edit Modal]
                |
                v
            [Load Current Values]
                |
                v
            [Modify Fields]
                |
                v
            [Save or Cancel]
```

### 6. Bulk Operations Flow
```
[Todo List View]
        |
        v
[Enable Selection Mode]
   ├─> Click "Select" button
   └─> Press Ctrl+Click on item
        |
        v
[Checkboxes Appear]
        |
        v
[Select Items]
   ├─> Click individual checkboxes
   ├─> Shift+Click for range
   └─> Ctrl+A for all
        |
        v
[Show Bulk Action Bar]
   "X items selected"
        |
        v
[Choose Bulk Action]
        |
   ├─> [Mark Complete]
   |       |
   |       v
   |   [Update All Selected]
   |       |
   |       v
   |   [Save Changes]
   |
   ├─> [Delete Selected]
   |       |
   |       v
   |   [Confirm Dialog]
   |       |
   |   ├─> [Confirm]
   |   |       |
   |   |       v
   |   |   [Delete Items]
   |   |       |
   |   |       v
   |   |   [Update Storage]
   |   |
   |   └─> [Cancel]
   |           |
   |           v
   |       [Close Dialog]
   |
   └─> [Change Priority]
           |
           v
       [Select New Priority]
           |
           v
       [Update All Selected]
           |
           v
       [Save Changes]
```

### 7. Data Export Flow
```
[Main View]
        |
        v
[Click Export Button]
        |
        v
[Export Dialog Opens]
        |
        v
[Select Export Options]
        |
   ├─> [Choose Format]
   |    ├─> JSON (Full Data)
   |    ├─> CSV (Simplified)
   |    ├─> Markdown (Formatted)
   |    └─> PDF (Print)
   |
   ├─> [Select Scope]
   |    ├─> All Todos
   |    ├─> Active Only
   |    ├─> Completed Only
   |    └─> Filtered Results
   |
   └─> [Date Range (Optional)]
        ├─> Today
        ├─> This Week
        ├─> This Month
        └─> Custom Range
            |
            v
[Preview Export]
        |
        v
[Confirm Export]
        |
        v
[Generate File]
        |
        v
[Browser Download]
        |
        v
[Success Notification]
```

### 8. Theme Toggle Flow
```
[Current Theme Active]
        |
        v
[User Clicks Theme Toggle]
   └─> Location: Header toolbar
        |
        v
[Determine Next Theme]
        |
   ├─> [Light -> Dark]
   └─> [Dark -> Light]
        |
        v
[Apply Theme Transition]
   ├─> Fade out (200ms)
   ├─> Update CSS Variables
   └─> Fade in (200ms)
        |
        v
[Save Preference]
        |
        v
[Update Local Storage]
        |
        v
[Theme Applied]
```

### 9. Statistics View Flow
```
[Main Todo List]
        |
        v
[Click Statistics Icon/Panel]
        |
        v
[Statistics Panel Opens]
        |
        v
[Load Calculations]
   ├─> Total Tasks
   ├─> Completed Today
   ├─> Completion Rate
   ├─> Overdue Count
   └─> Category Distribution
        |
        v
[Display Metrics]
        |
        v
[User Interactions]
   ├─> [Change Time Period]
   |    ├─> Today
   |    ├─> This Week
   |    ├─> This Month
   |    └─> All Time
   |         |
   |         v
   |    [Recalculate]
   |         |
   |         v
   |    [Update Display]
   |
   └─> [View Details]
        └─> [Drill Down]
             |
             v
        [Filter by Metric]
             |
             v
        [Show Related Todos]
```

### 10. Keyboard Navigation Flow
```
[User on Any Screen]
        |
        v
[Press Keyboard Shortcut]
        |
        v
[Capture Key Event]
        |
        v
[Check Shortcut Map]
        |
   ├─> [N] -> Create New Todo
   ├─> [F] -> Focus Search
   ├─> [1/2/3] -> Set Priority
   ├─> [Space] -> Toggle Complete
   ├─> [Delete] -> Delete Selected
   ├─> [Ctrl+Z] -> Undo Last
   ├─> [Ctrl+A] -> Select All
   ├─> [Escape] -> Cancel/Close
   ├─> [?] -> Show Help
   └─> [Ctrl+D] -> Toggle Theme
        |
        v
[Execute Action]
        |
        v
[Provide Feedback]
   ├─> Visual indication
   ├─> Focus change
   └─> Notification
```

## Error Handling Flows

### Storage Quota Exceeded Flow
```
[Save Operation]
        |
        v
[Check Storage Space]
        |
        v
[Quota Exceeded?]
        |
   ├─> [No] -> [Save Normally]
   |
   └─> [Yes]
        |
        v
   [Show Warning Dialog]
   "Storage 80% full"
        |
        v
   [Offer Options]
        |
   ├─> [Clear Old Completed]
   |       |
   |       v
   |   [Select Items >30 days]
   |       |
   |       v
   |   [Confirm Deletion]
   |       |
   |       v
   |   [Free Space]
   |
   ├─> [Export & Clear]
   |       |
   |       v
   |   [Export All Data]
   |       |
   |       v
   |   [Clear Selected]
   |
   └─> [Cancel]
           |
           v
       [Abort Save]
```

### Data Recovery Flow
```
[App Loads]
        |
        v
[Read Local Storage]
        |
        v
[Data Corrupted?]
        |
   ├─> [No] -> [Load Normally]
   |
   └─> [Yes]
        |
        v
   [Check Backup]
        |
        v
   [Backup Available?]
        |
   ├─> [Yes]
   |      |
   |      v
   |  [Restore from Backup]
   |      |
   |      v
   |  [Verify Integrity]
   |      |
   |      v
   |  [Load App]
   |
   └─> [No]
          |
          v
      [Show Recovery Options]
          |
      ├─> [Start Fresh]
      |      |
      |      v
      |  [Initialize Empty State]
      |
      └─> [Import Backup]
             |
             v
         [File Upload]
             |
             v
         [Validate & Import]
```

## Mobile-Specific Flows

### Touch Gesture Flow
```
[Todo Item Display]
        |
        v
[Touch Interaction]
        |
   ├─> [Tap] -> Toggle Expand/Collapse
   |
   ├─> [Long Press] -> Enter Selection Mode
   |
   ├─> [Swipe Right] -> Mark Complete
   |       |
   |       v
   |   [Show Completion Animation]
   |       |
   |       v
   |   [Update Status]
   |
   └─> [Swipe Left] -> Show Actions
           |
           v
       [Action Buttons Reveal]
           |
       ├─> Edit
       ├─> Delete
       └─> Priority
```

### Responsive Layout Flow
```
[Detect Screen Size]
        |
        v
[Apply Breakpoint Rules]
        |
   ├─> [Mobile: 320-767px]
   |       |
   |       v
   |   [Stack Layout]
   |   [Hide Sidebar]
   |   [Hamburger Menu]
   |   [Bottom FAB]
   |
   ├─> [Tablet: 768-1023px]
   |       |
   |       v
   |   [Collapsible Sidebar]
   |   [2-Column Grid]
   |   [Touch Optimized]
   |
   └─> [Desktop: 1024px+]
           |
           v
       [Full Layout]
       [Persistent Sidebar]
       [Hover States]
       [Keyboard Focus]
```

## State Transitions

### Todo Item State Machine
```
States:
- DRAFT (being created)
- ACTIVE (saved, not complete)
- COMPLETED (marked done)
- DELETED (soft delete, recoverable)
- PURGED (permanently removed)

Transitions:
DRAFT -> ACTIVE: Save
DRAFT -> DELETED: Cancel
ACTIVE -> COMPLETED: Mark Complete
COMPLETED -> ACTIVE: Mark Incomplete
ACTIVE -> DELETED: Delete
COMPLETED -> DELETED: Delete
DELETED -> ACTIVE: Undo (within 5 seconds)
DELETED -> PURGED: After timeout
```

## Decision Points

### Priority Assignment Logic
```
[Create/Edit Todo]
        |
        v
[Priority Selected?]
        |
   ├─> [No]
   |      |
   |      v
   |  [Has Due Date?]
   |      |
   |  ├─> [Yes]
   |  |      |
   |  |      v
   |  |  [Due < 24hrs?]
   |  |      |
   |  |  ├─> [Yes] -> Set HIGH
   |  |  └─> [No] -> Set MEDIUM
   |  |
   |  └─> [No] -> Set MEDIUM (default)
   |
   └─> [Yes] -> Use Selected Priority
```

### Auto-Save Decision Tree
```
[User Makes Change]
        |
        v
[Start 500ms Timer]
        |
        v
[Another Change?]
        |
   ├─> [Yes] -> [Reset Timer]
   |                 ^
   |                 |
   |            [Loop Back]
   |
   └─> [No]
        |
        v
   [Timer Expires]
        |
        v
   [Save to Storage]
        |
        v
   [Update UI State]
```

---

*Document Version: 1.0.0*  
*Last Updated: 2025-01-21*  
*Status: Complete*