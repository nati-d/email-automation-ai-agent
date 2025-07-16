# Email Agent Frontend - Development Guide

## 🏗️ Architecture Overview

This frontend follows a modular, component-based architecture inspired by Gmail's interface, built with modern React patterns and best practices.

### Key Architectural Decisions

- **Component Modularity**: Each feature is broken into reusable, focused components
- **State Management**: Zustand for client state, TanStack Query for server state
- **Type Safety**: Full TypeScript implementation with strict typing
- **Authentication**: Session-based OAuth with Google
- **UI Consistency**: ShadCN UI components for design system consistency

## 📁 Detailed Project Structure

```
frontend/
├── app/                          # Next.js 15 App Router
│   ├── auth-success/page.tsx     # OAuth callback handler
│   ├── login/page.tsx           # Login route
│   ├── globals.css              # Global styles with CSS variables
│   ├── layout.tsx               # Root layout with providers
│   └── page.tsx                 # Main app entry point
│
├── components/
│   ├── auth/                    # Authentication components
│   │   ├── auth-guard.tsx       # Route protection HOC
│   │   └── login-page.tsx       # Google OAuth login interface
│   │
│   ├── email/                   # Core email functionality
│   │   ├── compose-email.tsx    # Email composition modal
│   │   ├── email-layout.tsx     # Main 3-panel Gmail-like layout
│   │   ├── email-list.tsx       # Email list with search/pagination
│   │   ├── email-list-item.tsx  # Individual email row component
│   │   ├── email-search.tsx     # Search functionality
│   │   ├── email-sidebar.tsx    # Left navigation panel
│   │   └── email-view.tsx       # Email reading pane
│   │
│   ├── providers/               # React context providers
│   │   ├── query-provider.tsx   # TanStack Query setup
│   │   ├── theme-provider.tsx   # Dark/light mode support
│   │   └── toast-provider.tsx   # Notification system
│   │
│   └── ui/                      # Reusable UI components (ShadCN)
│       ├── button.tsx           # Button variants
│       ├── input.tsx            # Form inputs
│       ├── card.tsx             # Content containers
│       ├── dialog.tsx           # Modal dialogs
│       ├── avatar.tsx           # User avatars
│       ├── badge.tsx            # Status indicators
│       ├── loading.tsx          # Loading states
│       ├── error-boundary.tsx   # Error handling
│       ├── theme-toggle.tsx     # Theme switcher
│       └── toast.tsx            # Notification components
│
├── lib/                         # Core utilities and logic
│   ├── api.ts                   # HTTP client for backend communication
│   ├── queries.ts               # TanStack Query hooks and mutations
│   ├── store.ts                 # Zustand state management
│   ├── types.ts                 # TypeScript type definitions
│   └── utils.ts                 # Utility functions
│
└── hooks/                       # Custom React hooks
    └── use-mobile.ts           # Mobile detection hook
```

## 🔄 State Management Strategy

### Zustand Stores

1. **Auth Store** (`useAuthStore`)
   - User authentication state
   - Session management
   - Login/logout actions

2. **Email Store** (`useEmailStore`)
   - Selected folder/view
   - Email selection state
   - Search queries and filters
   - Compose modal state

3. **UI Store** (`useUIStore`)
   - Theme preferences
   - Sidebar collapse state
   - UI-specific settings

### TanStack Query Integration

- **Queries**: Data fetching with caching and background updates
- **Mutations**: Email operations (send, delete, star, etc.)
- **Optimistic Updates**: Immediate UI feedback
- **Error Handling**: Automatic retry and error states

## 🎨 Component Design Patterns

### 1. Container/Presentation Pattern
```typescript
// Container component handles logic
export function EmailListContainer() {
  const { data, isLoading } = useEmails()
  return <EmailList emails={data} loading={isLoading} />
}

// Presentation component handles UI
export function EmailList({ emails, loading }) {
  // Pure UI rendering
}
```

### 2. Custom Hooks for Logic
```typescript
// Custom hook encapsulates complex logic
export function useEmailActions() {
  const markAsRead = useMarkAsRead()
  const starEmail = useStarEmail()
  
  return { markAsRead, starEmail }
}
```

### 3. Compound Components
```typescript
// Compose email with sub-components
<ComposeEmail>
  <ComposeEmail.Header />
  <ComposeEmail.Recipients />
  <ComposeEmail.Body />
  <ComposeEmail.Actions />
</ComposeEmail>
```

## 🔐 Authentication Flow

### OAuth Implementation
1. **Login Initiation**: User clicks "Sign in with Google"
2. **Backend Request**: Frontend requests auth URL from backend
3. **Google Redirect**: User redirected to Google OAuth
4. **Callback Handling**: Google redirects to `/auth-success`
5. **Session Storage**: User data and session ID stored in Zustand
6. **Route Protection**: `AuthGuard` protects authenticated routes

### Session Management
```typescript
// Session-based authentication
const { sessionId, user, setAuth, clearAuth } = useAuthStore()

// API calls include session ID
const getCurrentUser = (sessionId: string) => 
  apiClient.request(`/auth/me?session_id=${sessionId}`)
```

## 📧 Email Management Features

### Core Functionality
- **Email List**: Paginated, searchable email list
- **Email View**: Full email reading with attachments
- **Compose**: Rich email composition with attachments
- **Search**: Real-time email search across all fields
- **Folders**: Gmail-like folder organization
- **Actions**: Star, archive, delete, move operations

### Advanced Features
- **Bulk Operations**: Select multiple emails for batch actions
- **Keyboard Shortcuts**: Gmail-like keyboard navigation
- **Responsive Design**: Mobile-optimized interface
- **Real-time Updates**: Live email synchronization
- **Offline Support**: Cached data for offline viewing

## 🎯 Performance Optimizations

### React Query Optimizations
```typescript
// Stale-while-revalidate pattern
export function useEmails() {
  return useQuery({
    queryKey: ['emails'],
    queryFn: fetchEmails,
    staleTime: 30 * 1000,      // 30 seconds
    cacheTime: 5 * 60 * 1000,  // 5 minutes
  })
}
```

### Component Optimizations
- **React.memo**: Prevent unnecessary re-renders
- **useMemo/useCallback**: Memoize expensive calculations
- **Lazy Loading**: Code splitting for large components
- **Virtual Scrolling**: Handle large email lists efficiently

## 🧪 Testing Strategy

### Component Testing
```typescript
// Example test structure
describe('EmailList', () => {
  it('renders emails correctly', () => {
    render(<EmailList emails={mockEmails} />)
    expect(screen.getByText('Test Subject')).toBeInTheDocument()
  })
})
```

### Integration Testing
- **API Integration**: Mock backend responses
- **User Flows**: Test complete user journeys
- **Error Scenarios**: Test error handling and recovery

## 🚀 Deployment Considerations

### Environment Configuration
```env
# Production environment variables
NEXT_PUBLIC_API_URL=https://api.yourdomain.com/api
NEXT_PUBLIC_APP_NAME="Email Agent"
NEXT_PUBLIC_APP_VERSION="1.0.0"
```

### Build Optimizations
- **Bundle Analysis**: Monitor bundle size
- **Image Optimization**: Next.js automatic optimization
- **Static Generation**: Pre-render static pages
- **CDN Integration**: Serve static assets from CDN

## 🔧 Development Workflow

### Getting Started
1. Clone repository and install dependencies
2. Set up environment variables
3. Start development server
4. Run backend API server
5. Test OAuth flow

### Code Quality
- **ESLint**: Code linting and formatting
- **TypeScript**: Strict type checking
- **Prettier**: Code formatting
- **Husky**: Pre-commit hooks

### Debugging
- **React DevTools**: Component inspection
- **TanStack Query DevTools**: Query debugging
- **Network Tab**: API request monitoring
- **Console Logging**: Strategic logging for debugging

## 📚 Key Libraries and Tools

### Core Dependencies
- **Next.js 15**: React framework with App Router
- **React 19**: Latest React with concurrent features
- **TypeScript**: Type safety and developer experience
- **Tailwind CSS**: Utility-first styling

### State Management
- **Zustand**: Lightweight state management
- **TanStack Query**: Server state management
- **React Hook Form**: Form handling
- **Zod**: Schema validation

### UI Components
- **ShadCN UI**: Accessible component library
- **Lucide React**: Icon library
- **Radix UI**: Headless UI primitives

## 🎨 Design System

### Color Palette
- Uses CSS custom properties for theming
- Supports light/dark mode
- Accessible color contrasts

### Typography
- Geist Sans for UI text
- Geist Mono for code
- Responsive font scaling

### Spacing and Layout
- Consistent spacing scale
- Responsive grid system
- Mobile-first approach

## 🔮 Future Enhancements

### Planned Features
- **AI Integration**: Smart email categorization
- **Advanced Search**: Full-text search with filters
- **Email Templates**: Reusable email templates
- **Scheduling**: Send emails at specific times
- **Collaboration**: Share and collaborate on emails

### Technical Improvements
- **PWA Support**: Offline functionality
- **Push Notifications**: Real-time email alerts
- **Performance**: Virtual scrolling for large lists
- **Accessibility**: Enhanced screen reader support

This development guide provides a comprehensive overview of the email agent frontend architecture, patterns, and best practices implemented in this project.