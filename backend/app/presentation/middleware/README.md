# Authentication Middleware

This directory contains middleware components for handling authentication in the presentation layer.

## Overview

The authentication middleware provides a clean way to extract and validate authenticated users from OAuth sessions. It follows clean architecture principles by keeping authentication logic in the presentation layer.

## Components

### `auth_middleware.py`

Contains two main middleware functions:

1. **`get_current_user`** - Required authentication middleware
2. **`get_optional_current_user`** - Optional authentication middleware

## Usage

### Required Authentication

Use `get_current_user` when an endpoint requires authentication:

```python
from ..middleware.auth_middleware import get_current_user
from ...application.dto.user_dto import UserDTO

@router.get("/protected-endpoint")
async def protected_endpoint(
    current_user: UserDTO = Depends(get_current_user)
):
    # current_user will always be a valid UserDTO
    return {"message": f"Hello {current_user.name}!"}
```

### Optional Authentication

Use `get_optional_current_user` when an endpoint can work with or without authentication:

```python
from ..middleware.auth_middleware import get_optional_current_user
from ...application.dto.user_dto import UserDTO
from typing import Optional

@router.get("/public-endpoint")
async def public_endpoint(
    current_user: Optional[UserDTO] = Depends(get_optional_current_user)
):
    if current_user:
        return {"message": f"Hello {current_user.name}!"}
    else:
        return {"message": "Hello anonymous user!"}
```

## Session ID Sources

The middleware can extract the session ID from two sources:

1. **Header**: `X-Session-ID` header
2. **Query Parameter**: `session_id` query parameter

### Examples

#### Using Header
```bash
curl -H "X-Session-ID: abc123" http://localhost:8000/api/emails/my-emails
```

#### Using Query Parameter
```bash
curl http://localhost:8000/api/emails/my-emails?session_id=abc123
```

## Error Handling

### Required Authentication (`get_current_user`)

- **Missing Session ID**: Returns 401 with `MISSING_SESSION_ID` error
- **Invalid Session**: Returns 401 with `INVALID_SESSION` error
- **Session Error**: Returns 401 with `SESSION_ERROR` error
- **Internal Error**: Returns 500 with `INTERNAL_ERROR` error

### Optional Authentication (`get_optional_current_user`)

- **Any Error**: Returns `None` instead of raising an exception

## Example Endpoints

The email controller includes example endpoints that demonstrate both types of middleware:

- **`/api/emails/my-emails`** - Requires authentication
- **`/api/emails/public`** - Optional authentication

## Security Notes

- Session IDs are validated against the OAuth repository
- Expired sessions are automatically rejected
- Invalid session IDs return appropriate error messages
- The middleware follows the principle of least privilege

## Integration with Clean Architecture

The middleware integrates seamlessly with the clean architecture:

1. **Presentation Layer**: Handles HTTP concerns (headers, query params)
2. **Application Layer**: Uses use cases for business logic
3. **Domain Layer**: Leverages domain exceptions for error handling
4. **Infrastructure Layer**: Uses dependency injection for services

## Testing

To test the middleware:

1. First authenticate via OAuth to get a session ID
2. Use the session ID in subsequent requests
3. Test both authenticated and unauthenticated scenarios

Example test flow:
```bash
# 1. Get session ID from OAuth callback
# 2. Test protected endpoint
curl -H "X-Session-ID: YOUR_SESSION_ID" http://localhost:8000/api/emails/my-emails

# 3. Test public endpoint (works without session)
curl http://localhost:8000/api/emails/public

# 4. Test public endpoint with session (personalized)
curl -H "X-Session-ID: YOUR_SESSION_ID" http://localhost:8000/api/emails/public
``` 