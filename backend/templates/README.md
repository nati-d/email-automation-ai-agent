# Google OAuth Test Template

This directory contains a simple HTML template to test the Google OAuth functionality of the Email Agent API.

## Setup

### 1. Start the FastAPI Server

Make sure your FastAPI server is running:

```bash
cd backend
python main.py
```

The API should be available at `http://localhost:8000`

### 2. Set up Google OAuth Configuration

Make sure you have the following environment variables set in your `.env` file:

```
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_REDIRECT_URI=http://localhost:3000/auth-success
FRONTEND_URL=http://localhost:3000
```

### 3. Serve the HTML Template

You have several options to serve the HTML template:

#### Option A: Using Python's built-in server

```bash
cd backend/templates
python -m http.server 3000
```

Then open: `http://localhost:3000/oauth_test.html`

#### Option B: Using Node.js serve

```bash
npm install -g serve
cd backend/templates
serve -p 3000
```

Then open: `http://localhost:3000/oauth_test.html`

#### Option C: Using any other static file server

Just make sure the template is served on `http://localhost:3000` (or update the `FRONTEND_URL` in your settings to match your chosen port).

## Usage

1. Open the HTML template in your browser
2. The page will automatically check if the API is running
3. Click "Sign in with Google" to start the OAuth flow
4. You'll be redirected to Google for authentication
5. After successful authentication, you'll be redirected back with user information
6. You can then test the logout functionality

## Features

The test template includes:

- ✅ **API Status Indicator**: Shows if the FastAPI server is running
- ✅ **OAuth Login**: Initiates Google OAuth flow
- ✅ **User Information Display**: Shows user data after successful login
- ✅ **Logout Functionality**: Tests token revocation
- ✅ **Error Handling**: Displays authentication errors
- ✅ **Responsive Design**: Works on mobile and desktop
- ✅ **Loading States**: Visual feedback during operations

## OAuth Flow

1. **Initiate Login**: Calls `GET /api/auth/google/login`
2. **Redirect to Google**: User completes OAuth on Google
3. **Handle Callback**: Google redirects to `GET /api/auth/google/callback`
4. **Success Redirect**: API redirects back to frontend with user data
5. **Display User Info**: Template shows authenticated user information

## Troubleshooting

### API Connection Issues

- Make sure the FastAPI server is running on `http://localhost:8000`
- Check the console for CORS errors
- Verify the API health endpoint is accessible

### OAuth Configuration Issues

- Verify your Google OAuth credentials are correct
- Make sure the redirect URI in Google Console matches your configuration
- Check that all required scopes are enabled

### Redirect Issues

- Ensure `FRONTEND_URL` matches where you're serving the HTML template
- Verify the redirect URI in your Google OAuth configuration
- Check browser console for any JavaScript errors

## API Endpoints Used

- `GET /api/health` - API health check
- `GET /api/auth/google/login` - Initiate OAuth flow
- `GET /api/auth/google/callback` - Handle OAuth callback
- `GET /api/auth/me` - Get current user info (requires Bearer token)
- `POST /api/auth/refresh` - Refresh OAuth token (requires Bearer token)
- `POST /api/auth/logout` - Logout and revoke tokens (requires Bearer token)

## Bearer Token Authentication

The API now supports Bearer token authentication for protected endpoints. After successful OAuth login, you'll receive a session ID that should be used as a Bearer token.

### Using Bearer Tokens

```javascript
// Example: Get current user info
const response = await fetch('/api/auth/me', {
    headers: {
        'Authorization': 'Bearer your_session_id_here'
    }
});
```

### Protected Endpoints

The following endpoints require Bearer token authentication:

- `GET /api/auth/me` - Get current user information
- `POST /api/auth/refresh` - Refresh OAuth token
- `POST /api/auth/logout` - Logout and revoke tokens
- `GET /api/emails/my-emails` - Get user's emails
- `POST /api/emails/send` - Send email

### Authentication Flow

1. **Login**: Complete OAuth flow to get session ID
2. **Use Bearer Token**: Include session ID in Authorization header
3. **Automatic Validation**: Middleware validates token and provides user context
4. **Logout**: Revoke token when done

## Security Notes

- The template stores OAuth state in localStorage for CSRF protection
- All API calls are made over HTTP (use HTTPS in production)
- Session management is handled by the backend API
- Tokens are not exposed to the frontend JavaScript
- Bearer tokens provide secure authentication for API endpoints 