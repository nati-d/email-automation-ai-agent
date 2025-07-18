# Add Another Account Endpoint

This document describes the `/oauth/add-another-account` endpoint that allows logged-in users to add additional email accounts to their existing account.

## Overview

The `add_another_account` endpoint enables users to connect multiple Gmail accounts to a single user account. This is useful for users who want to manage emails from different accounts (e.g., personal and work) in one place.

## Endpoint Details

### URL
```
POST /api/oauth/add-another-account
```

### Authentication
- **Required**: Bearer token in Authorization header
- **Token Source**: Valid OAuth session ID

### Request Body
```json
{
  "code": "4/0AfJohXn...",
  "state": "abc123def456..."
}
```

### Parameters
- **`code`** (string, required): OAuth authorization code from Google
- **`state`** (string, required): OAuth state parameter for security

## How It Works

### 1. OAuth Flow
1. User initiates OAuth flow for the new account
2. User completes Google OAuth consent
3. Google returns authorization code and state
4. User calls `/oauth/add-another-account` with code and state

### 2. Account Association
1. System exchanges code for OAuth tokens
2. System retrieves user info from Google
3. System finds existing user by current session
4. System associates new OAuth session with existing user

### 3. Email Import
1. System fetches emails from the new account
2. Emails are stored with correct ownership:
   - `account_owner`: Current logged-in user's email
   - `email_holder`: New account's email address
3. Emails are processed with AI (summarization, categorization)

## Response Format

### Success Response
```json
{
  "success": true,
  "message": "Successfully added account work@company.com to user user@gmail.com",
  "account_added": {
    "email": "work@company.com",
    "name": "Work Account",
    "picture": "https://lh3.googleusercontent.com/...",
    "provider": "google"
  },
  "existing_user": {
    "id": "user123",
    "email": "user@gmail.com",
    "name": "John Doe"
  },
  "oauth_session_id": "session456",
  "email_import": {
    "success": true,
    "emails_imported": 45,
    "emails_summarized": 45,
    "message": "Successfully imported 45 emails"
  }
}
```

### Error Response
```json
{
  "success": false,
  "error": "oauth_error",
  "message": "OAuth error: access_denied"
}
```

## Use Cases

### Example Scenario
1. **User**: `user@gmail.com` (logged-in user)
2. **Adds**: `work@company.com` (work account)
3. **Result**: 
   - `account_owner`: `user@gmail.com`
   - `email_holder`: `work@company.com`

### Multiple Accounts
A user can add multiple accounts:
- Personal: `user@gmail.com` (account_owner: `user@gmail.com`, email_holder: `user@gmail.com`)
- Work: `work@company.com` (account_owner: `user@gmail.com`, email_holder: `work@company.com`)
- Side Project: `side@project.com` (account_owner: `user@gmail.com`, email_holder: `side@project.com`)

## Implementation Details

### AddAnotherAccountUseCase
```python
class AddAnotherAccountUseCase(OAuthUseCaseBase):
    async def execute(
        self, 
        code: str, 
        state: str, 
        current_user_email: str,
        error: Optional[str] = None
    ) -> Dict[str, Any]:
        # 1. Exchange code for tokens
        # 2. Get user info from Google
        # 3. Create OAuth session
        # 4. Associate with existing user
        # 5. Fetch emails with correct ownership
```

### Email Ownership
When emails are fetched from the new account:
```python
email = Email(
    sender=sender,
    recipients=recipients,
    subject=subject,
    body=body,
    # Account ownership fields
    account_owner=current_user_email,  # Logged-in user
    email_holder=user_info.email,      # New account
    metadata={...}
)
```

## Testing

### Manual Testing
1. Get OAuth URL:
   ```bash
   curl -H "Authorization: Bearer YOUR_SESSION_ID" \
        http://localhost:8000/api/oauth/login
   ```

2. Complete OAuth flow in browser

3. Add another account:
   ```bash
   curl -X POST \
        -H "Authorization: Bearer YOUR_SESSION_ID" \
        -H "Content-Type: application/json" \
        -d '{"code": "YOUR_CODE", "state": "YOUR_STATE"}' \
        http://localhost:8000/api/oauth/add-another-account
   ```

### Automated Testing
Use the provided test script:
```bash
python test_add_another_account.py
```

## Security Considerations

### OAuth State Validation
- State parameter is validated to prevent CSRF attacks
- Each OAuth flow generates a unique state

### Session Management
- New OAuth sessions are associated with existing user
- Sessions are properly validated and stored

### Email Access
- Only emails from authorized accounts are accessed
- OAuth tokens are securely stored and managed

## Error Handling

### Common Errors
- **`oauth_error`**: OAuth flow failed (user denied access, invalid code)
- **`user_not_found`**: Current user not found in database
- **`internal_error`**: System error during account addition

### Recovery
- Failed account additions don't affect existing accounts
- Users can retry the OAuth flow
- Error messages provide clear guidance

## Future Enhancements

### Account Management
- List connected accounts
- Remove connected accounts
- Switch between accounts

### Unified Inbox
- View emails from all accounts in one interface
- Filter by account
- Account-specific settings

### Advanced Features
- Account-specific email rules
- Cross-account email forwarding
- Account-specific AI training 