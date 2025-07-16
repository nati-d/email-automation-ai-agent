# Bearer Token Authentication

This document describes the Bearer token authentication system implemented in the Email Agent API.

## Overview

The API now supports Bearer token authentication for protected endpoints. After successful OAuth login, users receive a session ID that serves as a Bearer token for subsequent API calls.

## How It Works

### 1. OAuth Login Flow

1. User initiates OAuth login via `/api/auth/google/login`
2. User completes authentication on Google
3. Google redirects to `/api/auth/google/callback`
4. API creates OAuth session and returns session ID
5. Frontend receives session ID as Bearer token

### 2. Bearer Token Usage

```javascript
// Example: Get current user info
const response = await fetch('/api/auth/me', {
    headers: {
        'Authorization': 'Bearer your_session_id_here'
    }
});
```

### 3. Middleware Validation

The authentication middleware:
- Extracts Bearer token from Authorization header
- Validates session ID against OAuth repository
- Provides user context to protected endpoints
- Returns 401 for invalid/expired tokens

## Protected Endpoints

The following endpoints require Bearer token authentication:

### Authentication Endpoints
- `GET /api/auth/me` - Get current user information
- `POST /api/auth/refresh` - Refresh OAuth token
- `POST /api/auth/logout` - Logout and revoke tokens

### Email Endpoints
- `GET /api/emails/my-emails` - Get user's emails
- `POST /api/emails/send` - Send email

### Test Endpoints
- `GET /api/auth-test/protected` - Protected test endpoint
- `GET /api/auth-test/user-info` - Get user info test endpoint

## Implementation Details

### Middleware Functions

#### `get_current_user`
- **Purpose**: Required authentication middleware
- **Returns**: `UserDTO` object
- **Error**: 401 if no valid session found

#### `get_optional_current_user`
- **Purpose**: Optional authentication middleware
- **Returns**: `Optional[UserDTO]` or `None`
- **Error**: Returns `None` for any authentication errors

#### `get_current_user_with_session_id`
- **Purpose**: Provides both user and session ID
- **Returns**: `tuple[UserDTO, str]`
- **Error**: 401 if no valid session found

### Security Features

1. **Token Validation**: Session IDs are validated against OAuth repository
2. **Expiration Check**: Expired sessions are automatically rejected
3. **CSRF Protection**: State parameter prevents CSRF attacks
4. **Secure Headers**: Bearer tokens in Authorization header
5. **Error Handling**: Proper error responses for authentication failures

## Error Responses

### Missing Token (401)
```json
{
    "error": "MISSING_SESSION_ID",
    "message": "Session ID is required. Provide it as Bearer token in Authorization header or session_id query parameter."
}
```

### Invalid Token (401)
```json
{
    "error": "INVALID_SESSION",
    "message": "Invalid or expired session. Please login again."
}
```

### Session Error (401)
```json
{
    "error": "SESSION_ERROR",
    "message": "Session validation failed"
}
```

## Testing

### Manual Testing

Use the provided test script:
```bash
python examples/test_me_endpoint.py
```

### cURL Examples

```bash
# Test without authentication (should fail)
curl http://localhost:8000/api/auth/me

# Test with invalid token (should fail)
curl -H "Authorization: Bearer invalid_token" http://localhost:8000/api/auth/me

# Test with valid token
curl -H "Authorization: Bearer your_session_id" http://localhost:8000/api/auth/me

# Test logout
curl -X POST -H "Authorization: Bearer your_session_id" http://localhost:8000/api/auth/logout

# Test token refresh
curl -X POST -H "Authorization: Bearer your_session_id" http://localhost:8000/api/auth/refresh
```

### Frontend Integration

```javascript
// Store session ID after OAuth login
localStorage.setItem('session_id', sessionId);

// Use in API calls
const sessionId = localStorage.getItem('session_id');
const response = await fetch('/api/auth/me', {
    headers: {
        'Authorization': `Bearer ${sessionId}`
    }
});

// Handle authentication errors
if (response.status === 401) {
    // Redirect to login
    window.location.href = '/login';
}
```

## Migration from Query Parameters

The API maintains backward compatibility with query parameter authentication:

```bash
# Old way (still works)
curl "http://localhost:8000/api/auth/me?session_id=your_session_id"

# New way (recommended)
curl -H "Authorization: Bearer your_session_id" http://localhost:8000/api/auth/me
```

## Security Best Practices

1. **HTTPS Only**: Use HTTPS in production
2. **Token Storage**: Store tokens securely (not in localStorage for production)
3. **Token Expiration**: Handle token expiration gracefully
4. **Logout**: Always logout to revoke tokens
5. **Error Handling**: Implement proper error handling for 401 responses

## Future Enhancements

- JWT token support
- Refresh token rotation
- Rate limiting for authentication endpoints
- Audit logging for authentication events
- Multi-factor authentication support 