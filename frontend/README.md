# Email Agent Frontend

A modern, Gmail-inspired email management frontend built with Next.js, featuring AI-powered email automation and smart organization.

## 🚀 Features

- **Gmail-inspired UI** - Clean, familiar interface with modern design
- **Google OAuth Authentication** - Secure login with Google accounts
- **Real-time Email Management** - View, compose, and organize emails
- **Responsive Design** - Works seamlessly on desktop and mobile
- **Modern Tech Stack** - Built with Next.js 15, React 19, and TypeScript
- **State Management** - Zustand for global state, TanStack Query for server state
- **UI Components** - ShadCN UI for consistent, accessible components

## 🛠️ Tech Stack

- **Framework**: Next.js 15 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: ShadCN UI
- **State Management**: Zustand
- **Data Fetching**: TanStack Query (React Query)
- **Form Handling**: React Hook Form with Zod validation
- **Authentication**: Google OAuth 2.0

## 📁 Project Structure

```
frontend/
├── app/                          # Next.js App Router
│   ├── auth-success/            # OAuth callback page
│   ├── login/                   # Login page
│   ├── globals.css              # Global styles
│   ├── layout.tsx               # Root layout
│   └── page.tsx                 # Home page
├── components/                   # React components
│   ├── auth/                    # Authentication components
│   │   ├── auth-guard.tsx       # Route protection
│   │   └── login-page.tsx       # Login interface
│   ├── email/                   # Email management components
│   │   ├── compose-email.tsx    # Email composition modal
│   │   ├── email-layout.tsx     # Main email interface
│   │   ├── email-list.tsx       # Email list with pagination
│   │   ├── email-list-item.tsx  # Individual email item
│   │   ├── email-sidebar.tsx    # Navigation sidebar
│   │   └── email-view.tsx       # Email reading interface
│   ├── providers/               # Context providers
│   │   └── query-provider.tsx   # TanStack Query provider
│   └── ui/                      # ShadCN UI components
├── hooks/                       # Custom React hooks
├── lib/                         # Utility libraries
│   ├── api.ts                   # API client
│   ├── queries.ts               # TanStack Query hooks
│   ├── store.ts                 # Zustand stores
│   ├── types.ts                 # TypeScript types
│   └── utils.ts                 # Utility functions
└── public/                      # Static assets
```

## 🚦 Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn
- Backend API running on `http://localhost:8000`

### Installation

1. **Clone and navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Set up environment variables**
   ```bash
   cp .env.local.example .env.local
   ```
   
   Edit `.env.local` with your configuration:
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000/api
   NEXT_PUBLIC_APP_NAME="Email Agent"
   NEXT_PUBLIC_APP_VERSION="1.0.0"
   ```

4. **Start the development server**
   ```bash
   npm run dev
   ```

5. **Open your browser**
   Navigate to [http://localhost:3000](http://localhost:3000)

## 🔐 Authentication Flow

1. **Login Page** - Users click "Continue with Google"
2. **OAuth Redirect** - Redirected to Google for authentication
3. **Callback Handling** - `/auth-success` processes the OAuth response
4. **Session Management** - User session stored with Zustand
5. **Route Protection** - `AuthGuard` protects authenticated routes

## 📧 Email Management Features

### Sidebar Navigation
- **Inbox** - Incoming emails
- **Starred** - Important emails
- **Sent** - Outgoing emails
- **Drafts** - Unsent emails
- **Trash** - Deleted emails
- **Custom Labels** - Organized categories

### Email List
- **Search & Filter** - Find emails quickly
- **Bulk Actions** - Select multiple emails
- **Pagination** - Handle large email volumes
- **Real-time Updates** - Live email synchronization

### Email Composition
- **Rich Text Editor** - Format emails beautifully
- **Attachments** - File upload support
- **Recipients** - To, CC, BCC fields
- **Draft Saving** - Auto-save functionality
- **Send Scheduling** - Schedule emails for later

### Email Reading
- **Full Email View** - Complete email display
- **Attachment Handling** - Download and preview
- **Reply Actions** - Reply, Reply All, Forward
- **Email Actions** - Star, Archive, Delete

## 🎨 UI Components

Built with ShadCN UI for consistency and accessibility:

- **Button** - Various styles and sizes
- **Input** - Form inputs with validation
- **Card** - Content containers
- **Dialog** - Modal dialogs
- **Avatar** - User profile images
- **Badge** - Status indicators
- **Separator** - Visual dividers
- **Skeleton** - Loading placeholders

## 🔄 State Management

### Zustand Stores

- **Auth Store** - User authentication state
- **Email Store** - Email management state
- **UI Store** - Interface preferences

### TanStack Query

- **Server State** - API data caching and synchronization
- **Mutations** - Email operations (send, delete, etc.)
- **Background Updates** - Automatic data refreshing

## 🌐 API Integration

The frontend communicates with the backend through a clean API client:

```typescript
// Example API usage
const { data: emails, isLoading } = useEmails({ folder: 'inbox' })
const sendEmail = useCreateAndSendEmail()

// Send an email
await sendEmail.mutateAsync({
  to: ['recipient@example.com'],
  subject: 'Hello World',
  body: 'Email content'
})
```

## 🎯 Key Features Implementation

### Responsive Design
- **Mobile-first** approach
- **Adaptive layouts** for different screen sizes
- **Touch-friendly** interactions

### Accessibility
- **Keyboard navigation** support
- **Screen reader** compatibility
- **ARIA labels** and roles
- **Focus management**

### Performance
- **Code splitting** with Next.js
- **Image optimization** 
- **Lazy loading** for large lists
- **Efficient re-rendering** with React Query

## 🧪 Development

### Available Scripts

```bash
npm run dev          # Start development server
npm run build        # Build for production
npm run start        # Start production server
npm run lint         # Run ESLint
```

### Code Quality

- **TypeScript** for type safety
- **ESLint** for code linting
- **Prettier** for code formatting
- **Husky** for git hooks (if configured)

## 🚀 Deployment

### Build for Production

```bash
npm run build
npm run start
```

### Environment Variables

Ensure all environment variables are set in your production environment:

```env
NEXT_PUBLIC_API_URL=https://your-api-domain.com/api
NEXT_PUBLIC_APP_NAME="Email Agent"
NEXT_PUBLIC_APP_VERSION="1.0.0"
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions:
- Check the documentation
- Open an issue on GitHub
- Contact the development team

---

Built with ❤️ using Next.js, React, and modern web technologies.