# 🚀 Quick Start: Test Google OAuth

This guide will get you up and running with the Google OAuth test interface in under 5 minutes.

## Prerequisites

- ✅ FastAPI server running
- ✅ Google OAuth credentials configured
- ✅ Python 3.7+ installed

## Step 1: Setup Environment

Copy the example environment file and configure it:

```bash
cp env.example .env
```

Edit `.env` and set your Google OAuth credentials:

```env
GOOGLE_CLIENT_ID=your-actual-google-client-id
GOOGLE_CLIENT_SECRET=your-actual-google-client-secret
GOOGLE_REDIRECT_URI=http://localhost:3000/auth-success
FRONTEND_URL=http://localhost:3000
```

> 📝 **Note**: Make sure these match your Google OAuth configuration in Google Cloud Console.

## Step 2: Start the FastAPI Server

```bash
cd backend
python main.py
```

You should see:
```
🚀 Email Agent API starting...
📡 Server running at: http://localhost:8000
```

## Step 3: Start the OAuth Test Server

In a new terminal:

```bash
cd backend/templates
python serve.py
```

You should see:
```
🌐 Starting OAuth test server...
🔗 Server running at: http://localhost:3000
🧪 OAuth test page: http://localhost:3000/oauth_test.html
```

## Step 4: Test OAuth Flow

1. **Open the test page**: Navigate to `http://localhost:3000/oauth_test.html`

2. **Check API status**: The page should show "API Connected" in the top right

3. **Click "Sign in with Google"**: This will:
   - Call the FastAPI backend
   - Redirect you to Google OAuth
   - Ask for permissions

4. **Complete Google OAuth**: 
   - Sign in with your Google account
   - Grant the requested permissions

5. **Return to test page**: You should see:
   - Your user information displayed
   - Profile picture (if available)
   - Login timestamp
   - Whether you're a new user

6. **Test logout**: Click the logout button to test token revocation

## 🎯 What to Expect

### Successful Flow
- ✅ Green "API Connected" indicator
- ✅ Smooth redirect to Google
- ✅ User info displayed after login
- ✅ Successful logout

### Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| "API Disconnected" | Start FastAPI server: `python main.py` |
| OAuth redirect errors | Check `GOOGLE_REDIRECT_URI` in both `.env` and Google Console |
| CORS errors | Use the provided `serve.py` script, not `file://` URLs |
| "Invalid client" | Verify `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` |

## 🔧 Troubleshooting

### API Issues
```bash
# Check if FastAPI is running
curl http://localhost:8000/api/health

# Expected response:
{"message": "Email Agent API is healthy", "data": {...}}
```

### OAuth Issues
1. **Check Google Console setup**:
   - Authorized redirect URIs: `http://localhost:3000/auth-success`
   - Enabled APIs: Google+ API, Gmail API
   - OAuth consent screen configured

2. **Check environment variables**:
   ```bash
   # In backend directory
   python -c "from app.infrastructure.config.settings import get_settings; s = get_settings(); print(f'Client ID: {s.google_client_id[:10]}...')"
   ```

### Browser Issues
- **CORS errors**: Use `serve.py` instead of opening HTML file directly
- **Redirect loops**: Clear browser cache and cookies
- **Console errors**: Check browser developer tools

## 🧪 Testing Different Scenarios

### Test New User Registration
1. Use a Google account that hasn't logged in before
2. Check that `New User: Yes` is displayed
3. Verify user is created in Firestore

### Test Existing User Login
1. Login with the same Google account again
2. Check that `New User: No` is displayed
3. Verify existing user data is retrieved

### Test Error Handling
1. Stop the FastAPI server while on the test page
2. Try to login - should show "API Disconnected"
3. Restart server and try again

## 📱 Mobile Testing

The OAuth test interface is responsive and works on mobile devices:

```bash
# Find your local IP
ifconfig | grep "inet 192"  # macOS/Linux
ipconfig | findstr "IPv4"   # Windows

# Start servers with your IP
python serve.py 3000
# Then visit: http://YOUR_IP:3000/oauth_test.html
```

## 🎉 Success!

If everything works correctly, you now have:
- ✅ Working Google OAuth integration
- ✅ User registration and authentication
- ✅ Token management and revocation
- ✅ Clean architecture implementation
- ✅ Firestore user storage

Ready to integrate OAuth into your frontend application! 🚀 