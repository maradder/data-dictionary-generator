# Data Dictionary Frontend

A modern, type-safe React application for managing and exploring data dictionaries. Built with React 19, TypeScript, and a carefully selected stack of production-ready libraries.

## Table of Contents

- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Architecture Patterns](#architecture-patterns)
- [Component Guide](#component-guide)
- [API Integration](#api-integration)
- [State Management](#state-management)
- [Styling Guide](#styling-guide)
- [Features](#features)
- [Troubleshooting](#troubleshooting)
- [Contributing Guidelines](#contributing-guidelines)

---

## Tech Stack

### Core Framework
- **React 19.1** - Latest React with improved concurrent features
- **TypeScript 5.9** - Strict type safety throughout the application
- **Vite 7.1** - Lightning-fast build tool with HMR

### Routing & Navigation
- **React Router v7.9** - Client-side routing with nested layouts

### UI & Styling
- **TailwindCSS 3.4** - Utility-first CSS framework
- **shadcn/ui** - High-quality, accessible component primitives built on Radix UI
- **Lucide React** - Beautiful, consistent icon library

### State Management
- **TanStack Query v5** (React Query) - Server state management with automatic caching, background refetching, and optimistic updates
- **React Hook Form 7.66** - Performant form state management
- **Zod 4.1** - TypeScript-first schema validation

### Data & Visualization
- **TanStack Table v8** - Headless table library with sorting, filtering, and pagination
- **Recharts 3.3** - Composable charting library (limited usage in Phase 1)
- **date-fns 4.1** - Modern date utility library

### HTTP & File Handling
- **Axios 1.13** - Promise-based HTTP client with interceptors
- **react-dropzone 14.3** - Drag-and-drop file upload with validation

### UX Enhancements
- **react-hot-toast 2.6** - Elegant toast notifications
- **class-variance-authority** - Type-safe variant styling
- **clsx + tailwind-merge** - Conditional class name composition

---

## Project Structure

```
frontend/
├── src/
│   ├── api/                    # API client layer
│   │   ├── client.ts          # Axios instance with interceptors
│   │   ├── dictionaries.ts    # Dictionary endpoints
│   │   ├── fields.ts          # Field endpoints
│   │   ├── versions.ts        # Version endpoints
│   │   ├── search.ts          # Search endpoints
│   │   └── index.ts           # Unified API exports
│   │
│   ├── components/
│   │   ├── ui/                # shadcn/ui base components (17 components)
│   │   │   ├── button.tsx
│   │   │   ├── card.tsx
│   │   │   ├── dialog.tsx
│   │   │   ├── table.tsx
│   │   │   └── ...
│   │   │
│   │   ├── layout/            # Application layout components
│   │   │   ├── MainLayout.tsx     # Main app shell with header/nav
│   │   │   ├── DocsDrawer.tsx     # Documentation sidebar
│   │   │   └── DocsContent.tsx    # Documentation content renderer
│   │   │
│   │   ├── common/            # Shared utility components
│   │   │   ├── EmptyState.tsx     # No data placeholder
│   │   │   ├── ErrorBoundary.tsx  # Error boundary wrapper
│   │   │   └── InfoModal.tsx      # Information modal
│   │   │
│   │   ├── dictionaries/      # Dictionary-specific components
│   │   │   ├── FieldExplorer.tsx      # Main data grid with TanStack Table
│   │   │   └── FieldDetailPanel.tsx   # Field metadata drawer
│   │   │
│   │   ├── fields/            # Field-related components
│   │   │   ├── FieldStatistics.tsx    # Field stats visualization
│   │   │   └── index.ts
│   │   │
│   │   ├── versions/          # Version management components
│   │   │   ├── VersionSelector.tsx    # Version dropdown
│   │   │   ├── VersionTimeline.tsx    # Version history timeline
│   │   │   ├── VersionComparison.tsx  # Side-by-side comparison
│   │   │   └── index.ts
│   │   │
│   │   └── upload/            # File upload components
│   │       ├── UploadProgress.tsx     # Upload progress indicator
│   │       └── index.ts
│   │
│   ├── hooks/                 # Custom React hooks
│   │   ├── useDictionaries.ts     # Dictionary CRUD operations
│   │   ├── useFields.ts           # Field querying and filtering
│   │   ├── useVersions.ts         # Version management
│   │   ├── useSearch.ts           # Global search
│   │   └── useUploadProgress.ts   # Upload progress polling
│   │
│   ├── lib/                   # Utility functions
│   │   ├── utils.ts          # cn() helper, common utilities
│   │   └── queryClient.ts    # TanStack Query configuration
│   │
│   ├── pages/                 # Route-level page components
│   │   ├── dictionaries/
│   │   │   ├── DictionariesListPage.tsx   # Dictionary listing
│   │   │   ├── DictionaryDetailPage.tsx   # Field explorer view
│   │   │   └── DictionaryUploadPage.tsx   # Upload wizard
│   │   │
│   │   └── search/
│   │       └── GlobalSearchPage.tsx       # Global search UI
│   │
│   ├── types/                 # TypeScript type definitions
│   │   └── api.ts            # API response types matching backend
│   │
│   ├── App.tsx               # Root component with routing
│   ├── main.tsx              # Application entry point
│   └── index.css             # Global styles + Tailwind directives
│
├── public/                   # Static assets
├── .env.example             # Environment variable template
├── components.json          # shadcn/ui configuration
├── package.json             # Dependencies and scripts
├── tsconfig.json            # TypeScript configuration
├── tailwind.config.js       # Tailwind customization
├── vite.config.ts           # Vite build configuration
└── README.md                # This file
```

---

## Getting Started

### Prerequisites

- **Node.js 18+** (LTS recommended)
- **npm 9+** or **yarn 1.22+**
- Backend API running on `http://localhost:8000` (or custom URL)

### Installation

1. **Install dependencies:**

```bash
npm install
```

2. **Configure environment variables:**

```bash
cp .env.example .env
```

Edit `.env` to point to your backend API:

```env
VITE_API_BASE_URL=http://localhost:8000
```

3. **Start development server:**

```bash
npm run dev
```

The application will be available at `http://localhost:5173`

### Verify Setup

1. Open `http://localhost:5173` in your browser
2. You should see the Data Dictionary homepage
3. Check browser console for any API connection errors
4. If the backend is running, you should see the dictionaries list (may be empty)

---

## Development Workflow

### Available Scripts

```bash
# Development
npm run dev              # Start Vite dev server with hot reload (port 5173)

# Building
npm run build            # TypeScript compilation + production build
npm run preview          # Preview production build locally

# Code Quality
npm run lint             # Run ESLint on entire codebase
npm run type-check       # TypeScript type checking (via tsc -b)
```

### Development Server Features

- **Hot Module Replacement (HMR)**: Changes reflect instantly without full page reload
- **Fast Refresh**: React components preserve state during updates
- **TypeScript Checking**: Type errors shown in terminal and browser
- **Path Aliases**: Use `@/` imports for cleaner import paths

### Build Output

Production builds are output to the `dist/` directory:

```
dist/
├── assets/
│   ├── index-[hash].js     # Bundled JavaScript
│   └── index-[hash].css    # Bundled CSS
└── index.html              # Entry HTML file
```

---

## Architecture Patterns

### Component Hierarchy

```
App (ErrorBoundary + QueryClientProvider)
└── BrowserRouter
    └── Routes
        └── MainLayout (Outlet wrapper)
            ├── DictionariesListPage
            ├── DictionaryDetailPage
            ├── DictionaryUploadPage
            └── GlobalSearchPage
```

### Data Flow Pattern

```
User Interaction
    ↓
Component Event Handler
    ↓
Custom Hook (useDictionaries, useFields, etc.)
    ↓
TanStack Query (cache check)
    ↓
API Client (Axios)
    ↓
Backend API
    ↓
Response → Query Cache → Component Re-render
```

### File Organization Principles

1. **Colocation**: Related files grouped by feature, not type
2. **Index Exports**: Public APIs exposed through `index.ts` files
3. **Type Safety**: All API responses have corresponding TypeScript types
4. **Separation of Concerns**:
   - Components render UI
   - Hooks manage state/side effects
   - API layer handles HTTP requests

---

## Component Guide

### Base UI Components (shadcn/ui)

All UI components are located in `src/components/ui/` and are based on Radix UI primitives. These are **copy-paste components**, not npm packages.

**Available Components:**

| Component | Purpose | Key Props |
|-----------|---------|-----------|
| `Button` | Interactive buttons | `variant`, `size`, `asChild` |
| `Card` | Container with header/content/footer | `className` |
| `Dialog` | Modal dialogs | `open`, `onOpenChange` |
| `Sheet` | Side panel/drawer | `side`, `open`, `onOpenChange` |
| `Table` | Semantic HTML tables | Styled `<table>` elements |
| `Tabs` | Tabbed interfaces | `value`, `onValueChange` |
| `Input` | Form text inputs | Standard input props |
| `Select` | Dropdown selections | `value`, `onValueChange`, `items` |
| `Badge` | Status indicators | `variant` |
| `Progress` | Progress bars | `value` (0-100) |
| `Tooltip` | Hover tooltips | `content`, `side` |
| `Alert` | Notification banners | `variant`, `title`, `description` |
| `Skeleton` | Loading placeholders | `className` |
| `Avatar` | User avatars | `src`, `fallback` |
| `Separator` | Visual dividers | `orientation` |
| `Label` | Form labels | `htmlFor` |
| `Collapsible` | Expandable sections | `open`, `onOpenChange` |

**Adding New shadcn/ui Components:**

The project uses the shadcn CLI for adding components:

```bash
# Add a single component
npx shadcn@latest add dropdown-menu

# Add multiple components
npx shadcn@latest add dropdown-menu switch checkbox
```

Configuration is in `components.json`:
- Style: `default`
- Base color: `slate`
- CSS variables: `enabled`
- Path aliases: `@/components`, `@/lib`, etc.

### Layout Components

**MainLayout** (`src/components/layout/MainLayout.tsx`)

Main application shell that wraps all pages:

```tsx
// Provides:
// - Top navigation bar
// - Documentation drawer (toggle with hamburger icon)
// - Outlet for nested routes
// - Responsive container

<MainLayout>
  <Outlet /> {/* Page components render here */}
</MainLayout>
```

**DocsDrawer** (`src/components/layout/DocsDrawer.tsx`)

Collapsible sidebar for documentation navigation.

### Feature Components

**FieldExplorer** (`src/components/dictionaries/FieldExplorer.tsx`)

The core data grid component built with TanStack Table:

```tsx
<FieldExplorer
  dictionaryId="abc-123"
  versionId="v1" // Optional: show specific version
/>
```

**Features:**
- Column sorting (multi-column with shift-click)
- Global text search across all fields
- Column-specific filters
- Pagination
- Row selection
- Column visibility toggle
- Responsive design (horizontal scroll on mobile)

**FieldDetailPanel** (`src/components/dictionaries/FieldDetailPanel.tsx`)

Sheet/drawer that shows detailed field metadata:

```tsx
<FieldDetailPanel
  field={selectedField}
  isOpen={isOpen}
  onClose={() => setIsOpen(false)}
/>
```

Displays:
- Full field name and description
- Data type and format
- Statistics (if available)
- PII classification
- Annotations
- Related metadata

### Custom Hooks

All custom hooks follow React Query patterns and are located in `src/hooks/`.

**useDictionaries** (`src/hooks/useDictionaries.ts`)

```tsx
import { useDictionaries, useCreateDictionary, useDeleteDictionary } from '@/hooks/useDictionaries'

// Fetch dictionaries list
const { data, isLoading, error } = useDictionaries(limit, offset)

// Create dictionary
const createMutation = useCreateDictionary()
createMutation.mutate({ file, name, description, generateAiDescriptions })

// Delete dictionary
const deleteMutation = useDeleteDictionary()
deleteMutation.mutate(dictionaryId)

// Export to Excel
const exportMutation = useExportDictionaryExcel()
exportMutation.mutate({ id, options: { include_statistics: true } })
```

**useFields** (`src/hooks/useFields.ts`)

```tsx
import { useFields } from '@/hooks/useFields'

const { data, isLoading } = useFields(dictionaryId, {
  versionId: 'optional-version-id',
  search: 'email',
  limit: 50,
  offset: 0
})
```

**useVersions** (`src/hooks/useVersions.ts`)

```tsx
import { useVersions } from '@/hooks/useVersions'

const { data: versions } = useVersions(dictionaryId)
```

All hooks automatically:
- Handle loading and error states
- Cache responses
- Refetch on window focus
- Invalidate related queries on mutations
- Show toast notifications on success/error

---

## API Integration

### API Client Configuration

The Axios client is configured in `src/api/client.ts`:

```typescript
import { apiClient } from '@/api/client'

// Base URL from environment variable
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

// Features:
// - 30-second timeout
// - Request/response interceptors
// - Automatic error handling
// - Auth token support (future)
```

### API Module Structure

Each feature has its own API module:

**src/api/dictionaries.ts**

```typescript
export const dictionariesApi = {
  list: (params) => apiClient.get('/api/v1/dictionaries', { params }),
  get: (id, includeVersions) => apiClient.get(`/api/v1/dictionaries/${id}`),
  create: (file, name, description, generateAiDescriptions) => { /* FormData */ },
  update: (id, data) => apiClient.patch(`/api/v1/dictionaries/${id}`, data),
  delete: (id) => apiClient.delete(`/api/v1/dictionaries/${id}`),
  exportExcel: (id, options) => apiClient.get(`/api/v1/dictionaries/${id}/export/excel`, {
    params: options,
    responseType: 'blob'
  }),
}
```

**src/api/fields.ts**

```typescript
export const fieldsApi = {
  list: (dictionaryId, params) => apiClient.get(`/api/v1/dictionaries/${dictionaryId}/fields`, { params }),
  get: (dictionaryId, fieldId) => apiClient.get(`/api/v1/dictionaries/${dictionaryId}/fields/${fieldId}`),
  getStatistics: (dictionaryId, fieldId) => apiClient.get(`/api/v1/dictionaries/${dictionaryId}/fields/${fieldId}/statistics`),
}
```

### Type Definitions

All API types are defined in `src/types/api.ts` and match the backend Pydantic models:

```typescript
export interface Dictionary {
  id: string
  name: string
  description?: string
  version: string
  created_at: string
  updated_at: string
  field_count: number
  versions?: DictionaryVersion[]
}

export interface Field {
  id: string
  dictionary_id: string
  name: string
  data_type: string
  description?: string
  is_required: boolean
  is_pii?: boolean
  statistics?: FieldStatistics
  annotations: Annotation[]
}

// ... more types
```

### Error Handling

API errors are handled at three levels:

1. **Axios Interceptor** (global): Logs errors to console
2. **React Query** (hook level): Manages error state, shows toast
3. **Component** (UI level): Displays error messages to user

```tsx
const { data, error, isError } = useDictionaries()

if (isError) {
  return <Alert variant="destructive">{error.message}</Alert>
}
```

---

## State Management

### Server State (TanStack Query)

All server data is managed by TanStack Query with these patterns:

**Query Keys** (defined in each hook file):

```typescript
export const dictionaryKeys = {
  all: ['dictionaries'] as const,
  lists: () => [...dictionaryKeys.all, 'list'] as const,
  list: (filters) => [...dictionaryKeys.lists(), filters] as const,
  details: () => [...dictionaryKeys.all, 'detail'] as const,
  detail: (id, includeVersions) => [...dictionaryKeys.details(), id, includeVersions] as const,
}
```

**Query Configuration** (`src/lib/queryClient.ts`):

```typescript
export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5,        // 5 minutes
      cacheTime: 1000 * 60 * 30,       // 30 minutes
      retry: 1,
      refetchOnWindowFocus: true,
      refetchOnReconnect: true,
    },
  },
})
```

**Mutation Pattern with Optimistic Updates:**

```typescript
const updateMutation = useUpdateDictionary()

updateMutation.mutate(
  { id, data },
  {
    onMutate: async (newData) => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries({ queryKey: dictionaryKeys.detail(id) })

      // Snapshot previous value
      const previous = queryClient.getQueryData(dictionaryKeys.detail(id))

      // Optimistically update
      queryClient.setQueryData(dictionaryKeys.detail(id), newData)

      return { previous }
    },
    onError: (err, newData, context) => {
      // Rollback on error
      queryClient.setQueryData(dictionaryKeys.detail(id), context?.previous)
    },
    onSettled: () => {
      // Refetch to ensure sync
      queryClient.invalidateQueries({ queryKey: dictionaryKeys.detail(id) })
    },
  }
)
```

### Form State (React Hook Form + Zod)

Forms use React Hook Form with Zod validation:

```typescript
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'

const uploadSchema = z.object({
  file: z.instanceof(File).refine((file) => file.size <= 50 * 1024 * 1024, {
    message: 'File must be less than 50MB',
  }),
  name: z.string().min(1, 'Name is required').max(255),
  description: z.string().optional(),
  generateAiDescriptions: z.boolean().default(true),
})

type UploadFormData = z.infer<typeof uploadSchema>

const form = useForm<UploadFormData>({
  resolver: zodResolver(uploadSchema),
  defaultValues: {
    generateAiDescriptions: true,
  },
})
```

### Local UI State

Ephemeral UI state uses standard React hooks:

```typescript
// Component-level state
const [isOpen, setIsOpen] = useState(false)
const [selectedField, setSelectedField] = useState<Field | null>(null)

// TanStack Table state
const [sorting, setSorting] = useState<SortingState>([])
const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([])
const [globalFilter, setGlobalFilter] = useState('')
```

---

## Styling Guide

### TailwindCSS Configuration

Custom configuration in `tailwind.config.js`:

```javascript
module.exports = {
  darkMode: ['class'],
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        border: 'hsl(var(--border))',
        input: 'hsl(var(--input))',
        ring: 'hsl(var(--ring))',
        background: 'hsl(var(--background))',
        foreground: 'hsl(var(--foreground))',
        primary: { /* ... */ },
        secondary: { /* ... */ },
        // ... shadcn color system
      },
      borderRadius: {
        lg: 'var(--radius)',
        md: 'calc(var(--radius) - 2px)',
        sm: 'calc(var(--radius) - 4px)',
      },
    },
  },
  plugins: [require('tailwindcss-animate')],
}
```

### CSS Variables

Global theme variables in `src/index.css`:

```css
@layer base {
  :root {
    --background: 0 0% 100%;
    --foreground: 222.2 84% 4.9%;
    --primary: 222.2 47.4% 11.2%;
    --primary-foreground: 210 40% 98%;
    /* ... more variables */
  }

  .dark {
    --background: 222.2 84% 4.9%;
    --foreground: 210 40% 98%;
    /* ... dark mode overrides */
  }
}
```

### Styling Patterns

**cn() Utility for Class Merging:**

```typescript
import { cn } from '@/lib/utils'

<div className={cn(
  'base-classes',
  isActive && 'active-classes',
  className // Allow prop overrides
)} />
```

**Component Variants with CVA:**

```typescript
import { cva, type VariantProps } from 'class-variance-authority'

const buttonVariants = cva(
  'inline-flex items-center justify-center rounded-md',
  {
    variants: {
      variant: {
        default: 'bg-primary text-primary-foreground hover:bg-primary/90',
        destructive: 'bg-destructive text-destructive-foreground',
        outline: 'border border-input bg-background hover:bg-accent',
      },
      size: {
        default: 'h-10 px-4 py-2',
        sm: 'h-9 px-3',
        lg: 'h-11 px-8',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'default',
    },
  }
)

export interface ButtonProps extends VariantProps<typeof buttonVariants> {
  // ...
}
```

### Responsive Design

Mobile-first breakpoints:

```tsx
<div className="
  grid grid-cols-1        // Mobile: 1 column
  md:grid-cols-2          // Tablet: 2 columns
  lg:grid-cols-3          // Desktop: 3 columns
  gap-4
">
  {/* Content */}
</div>
```

Standard breakpoints:
- `sm`: 640px
- `md`: 768px
- `lg`: 1024px
- `xl`: 1280px
- `2xl`: 1536px

---

## Features

### Implemented Features (Phase 1 - ~80% Complete)

#### Dictionary Management
- List all dictionaries with pagination
- View dictionary details
- Upload new dictionaries (Excel/CSV)
- Delete dictionaries
- Export to Excel with options

#### Field Explorer
- Advanced data table with TanStack Table
- Global search across all fields
- Column-specific filters
- Multi-column sorting
- Pagination (client-side)
- Column visibility toggles
- Responsive horizontal scroll

#### Field Details
- Comprehensive metadata display
- Statistics visualization
- PII classification indicators
- Annotation viewing
- Related field information

#### Version Management
- Version selector dropdown
- Version timeline visualization
- Basic version comparison (side-by-side)
- Version metadata display

#### File Upload
- Drag-and-drop interface
- File validation (type, size)
- Upload progress indicator
- Optional AI description generation
- Excel/CSV format support

#### User Experience
- Toast notifications for all actions
- Loading skeletons during data fetch
- Empty states with helpful messages
- Error boundaries for crash recovery
- Responsive mobile/tablet/desktop layouts

### Intentionally Missing Features

These features are planned for future phases:

#### Advanced Version Comparison
- Visual diff highlighting
- Field-level change detection
- Merge conflict resolution
- Comment threads on changes

#### Annotation Editing
- CRUD operations for annotations
- Rich text editor
- Mentions and tagging
- Annotation history

#### Statistics Charts
- Recharts integration (library installed)
- Field distribution charts
- Trend analysis over versions
- Custom report builder

#### Real-time Updates
- WebSocket integration
- Live upload progress
- Collaborative editing indicators
- Push notifications

#### Global Search Enhancements
- Advanced filters UI
- Search history
- Saved searches
- Faceted search results

#### Authentication & Authorization
- User login/logout
- Role-based access control
- API key management
- Audit logging

---

## Troubleshooting

### Common Issues

#### 1. API Connection Errors

**Symptom:** "Network Error: No response from server" toast

**Solutions:**
```bash
# Check backend is running
curl http://localhost:8000/api/v1/health

# Verify .env configuration
cat .env
# Should contain: VITE_API_BASE_URL=http://localhost:8000

# Restart dev server after .env changes
npm run dev
```

#### 2. TypeScript Errors After Dependency Updates

**Symptom:** Type errors in `node_modules` or component files

**Solutions:**
```bash
# Clear TypeScript cache
rm -rf node_modules/.vite

# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install

# Verify TypeScript version
npm list typescript
# Should be ~5.9.3
```

#### 3. Vite Build Failures

**Symptom:** Build errors with `Cannot find module '@/...'`

**Solutions:**
```bash
# Check tsconfig.json has path aliases
cat tsconfig.app.json
# Should have: "paths": { "@/*": ["./src/*"] }

# Verify vite.config.ts has resolve.alias
cat vite.config.ts
# Should have: resolve: { alias: { '@': path.resolve(__dirname, './src') } }

# Clean build cache
rm -rf dist node_modules/.vite
npm run build
```

#### 4. shadcn/ui Component Styling Issues

**Symptom:** Components render but have no styling

**Solutions:**
```bash
# Verify Tailwind is processing src/index.css
cat src/index.css
# Should have: @tailwind base; @tailwind components; @tailwind utilities;

# Check tailwind.config.js content paths
cat tailwind.config.js
# Should include: './src/**/*.{ts,tsx}'

# Rebuild CSS
npm run dev
```

#### 5. React Query Devtools Not Appearing

**Solution:**
Install React Query Devtools (optional):

```bash
npm install @tanstack/react-query-devtools --save-dev
```

Add to `App.tsx`:
```tsx
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'

<QueryClientProvider client={queryClient}>
  {/* ... */}
  <ReactQueryDevtools initialIsOpen={false} />
</QueryClientProvider>
```

#### 6. Hot Reload Not Working

**Symptoms:** Changes require manual refresh

**Solutions:**
```bash
# Check Vite server is running on correct port
# Output should show: Local: http://localhost:5173

# Verify no errors in terminal
# Look for TypeScript or ESLint errors

# Clear browser cache and hard reload
# Chrome/Edge: Ctrl+Shift+R or Cmd+Shift+R

# Restart Vite dev server
npm run dev
```

### Performance Optimization

#### Large Dictionary Performance

If working with dictionaries containing 10,000+ fields:

```tsx
// Enable virtualization in FieldExplorer
import { useVirtualizer } from '@tanstack/react-virtual'

// Increase pagination size
const { data } = useFields(dictionaryId, { limit: 100 })

// Implement server-side pagination
// (requires backend API changes)
```

#### Slow Initial Load

```bash
# Analyze bundle size
npm run build
npx vite-bundle-visualizer

# Consider code splitting
# Lazy load routes in App.tsx
const DictionaryDetailPage = lazy(() => import('./pages/dictionaries/DictionaryDetailPage'))
```

---

## Contributing Guidelines

### Code Style

**TypeScript:**
- Use `interface` for public APIs, `type` for unions/intersections
- Prefer explicit return types for public functions
- Use `const` for immutable values, `let` only when necessary
- Avoid `any`; use `unknown` for truly dynamic types

**React:**
- Prefer function components with hooks
- Use `React.FC` sparingly (only when you need `children` typing)
- Extract complex logic into custom hooks
- Keep components under 300 lines (split if larger)

**Naming Conventions:**
- Components: `PascalCase` (e.g., `FieldExplorer.tsx`)
- Hooks: `camelCase` with `use` prefix (e.g., `useDictionaries.ts`)
- Utilities: `camelCase` (e.g., `formatDate.ts`)
- Types: `PascalCase` (e.g., `Dictionary`, `FieldStatistics`)
- Constants: `UPPER_SNAKE_CASE` (e.g., `API_BASE_URL`)

### Component Creation Checklist

When adding a new component:

1. **Create component file** in appropriate directory
2. **Define TypeScript interface** for props
3. **Add JSDoc comments** for complex components
4. **Export from index.ts** if in a feature directory
5. **Add to Storybook** (if applicable)
6. **Write unit tests** (future: Vitest + React Testing Library)
7. **Update documentation** if it's a reusable component

### Adding New API Endpoints

1. **Define types in `src/types/api.ts`:**
```typescript
export interface NewResource {
  id: string
  name: string
  // ...
}
```

2. **Create API function in `src/api/newResource.ts`:**
```typescript
export const newResourceApi = {
  list: () => apiClient.get<NewResource[]>('/api/v1/new-resource'),
  // ...
}
```

3. **Create custom hook in `src/hooks/useNewResource.ts`:**
```typescript
export function useNewResources() {
  return useQuery({
    queryKey: ['newResources'],
    queryFn: () => newResourceApi.list(),
  })
}
```

4. **Export from barrel files:**
```typescript
// src/api/index.ts
export * from './newResource'

// src/hooks/index.ts (create if needed)
export * from './useNewResource'
```

### Git Workflow

```bash
# Create feature branch
git checkout -b feature/add-field-comparison

# Make changes, commit frequently
git add .
git commit -m "feat: add field comparison component"

# Before pushing, ensure build succeeds
npm run build
npm run lint

# Push and create PR
git push origin feature/add-field-comparison
```

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] New feature
- [ ] Bug fix
- [ ] Refactoring
- [ ] Documentation

## Testing
- [ ] Tested locally
- [ ] No console errors
- [ ] Responsive design verified
- [ ] TypeScript compiles without errors

## Screenshots (if applicable)
[Add screenshots for UI changes]

## Related Issues
Closes #123
```

---

## Additional Resources

### Documentation
- [React 19 Docs](https://react.dev/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [TanStack Query](https://tanstack.com/query/latest)
- [TanStack Table](https://tanstack.com/table/latest)
- [shadcn/ui](https://ui.shadcn.com/)
- [TailwindCSS](https://tailwindcss.com/)
- [React Router](https://reactrouter.com/)

### Tools
- [Vite Documentation](https://vitejs.dev/)
- [Axios Documentation](https://axios-http.com/)
- [Zod Documentation](https://zod.dev/)
- [React Hook Form](https://react-hook-form.com/)

### VSCode Extensions (Recommended)
- **ES7+ React/Redux/React-Native snippets** - Code snippets
- **Tailwind CSS IntelliSense** - Tailwind autocomplete
- **Pretty TypeScript Errors** - Better error messages
- **Error Lens** - Inline error highlighting
- **Auto Rename Tag** - Rename paired HTML/JSX tags

---

## License

This project is part of the Data Dictionary application. See the root README for license information.

---

## Questions or Issues?

For bug reports, feature requests, or questions:
1. Check the [Troubleshooting](#troubleshooting) section
2. Review existing GitHub issues
3. Create a new issue with detailed reproduction steps
4. Include browser console logs and network tab screenshots

**Happy coding!**
