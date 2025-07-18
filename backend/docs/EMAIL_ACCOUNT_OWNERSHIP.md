# Email Account Ownership

This document describes the email account ownership functionality that allows a single logged-in user to manage multiple email accounts.

## Overview

The email system now supports multiple email accounts under a single user account through two key fields:

- **`account_owner`**: The email address of the logged-in user who owns/manages this email account
- **`email_holder`**: The email address of the account that actually holds these emails

## Use Cases

### Single Account (Default)
When a user registers and connects their Gmail account:
- `account_owner`: `user@gmail.com` (logged-in user)
- `email_holder`: `user@gmail.com` (same as account owner)

### Multiple Accounts
When a user manages multiple email accounts:
- `account_owner`: `user@gmail.com` (logged-in user)
- `email_holder`: `work@company.com` (different email account)

## Implementation Details

### Email Entity
The `Email` entity now includes account ownership fields:

```python
@dataclass
class Email(BaseEntity):
    # ... existing fields ...
    
    # Account ownership fields
    account_owner: Optional[str] = None  # Email of the logged-in user who owns this email account
    email_holder: Optional[str] = None   # Email address of the account that actually holds these emails
```

### Gmail Integration
When emails are fetched from Gmail during user registration:

```python
email = Email(
    sender=sender,
    recipients=recipients,
    subject=subject,
    body=body_text,
    html_body=body_html,
    status=EmailStatus.SENT,
    sent_at=email_date,
    # Account ownership fields
    account_owner=str(user_email),  # The logged-in user's email
    email_holder=str(user_email),   # The email account that holds these emails
    metadata={...}
)
```

### Email Filtering
Emails are now filtered by `account_owner` instead of `recipient`:

```python
# Before: Filter by recipient
emails = await email_repository.find_by_recipient(recipient_email, limit)

# After: Filter by account owner
emails = await email_repository.find_by_account_owner(account_owner, limit)
```

## API Changes

### Email Response Format
All email responses now include account ownership fields:

```json
{
  "id": "email123",
  "sender": "sender@example.com",
  "recipients": ["recipient@example.com"],
  "subject": "Email Subject",
  "body": "Email content...",
  "status": "sent",
  "account_owner": "user@gmail.com",
  "email_holder": "user@gmail.com",
  "summary": "AI-generated summary",
  "main_concept": "Primary topic",
  "sentiment": "positive",
  "key_topics": ["topic1", "topic2"],
  "email_type": "inbox",
  "category": "work"
}
```

### Endpoints
All email endpoints now filter by `account_owner`:

- `GET /api/emails` - Get emails for the authenticated user
- `GET /api/emails/tasks` - Get task emails for the authenticated user
- `GET /api/emails/inbox` - Get inbox emails for the authenticated user
- `GET /api/emails/category/{category_name}` - Get emails by category for the authenticated user

## Database Schema

### Firestore Document Structure
```javascript
{
  "sender": "sender@example.com",
  "recipients": ["recipient@example.com"],
  "subject": "Email Subject",
  "body": "Email content...",
  "status": "sent",
  "account_owner": "user@gmail.com",    // NEW FIELD
  "email_holder": "user@gmail.com",     // NEW FIELD
  "summary": "AI-generated summary",
  "main_concept": "Primary topic",
  "sentiment": "positive",
  "key_topics": ["topic1", "topic2"],
  "email_type": "inbox",
  "category": "work",
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z"
}
```

## Future Enhancements

### Multiple Account Management
To support multiple email accounts per user:

1. **Account Registration**: Allow users to register multiple email accounts
2. **Account Switching**: UI to switch between different email accounts
3. **Unified Inbox**: View emails from all accounts in one place
4. **Account-Specific Settings**: Different settings per email account

### Implementation Example
```python
# User registers multiple accounts
user_accounts = [
    {"email": "personal@gmail.com", "type": "personal"},
    {"email": "work@company.com", "type": "work"},
    {"email": "side@project.com", "type": "side_project"}
]

# Emails are stored with different email_holder values
emails = [
    Email(account_owner="user@gmail.com", email_holder="personal@gmail.com", ...),
    Email(account_owner="user@gmail.com", email_holder="work@company.com", ...),
    Email(account_owner="user@gmail.com", email_holder="side@project.com", ...)
]
```

## Testing

Use the provided test script to verify account ownership functionality:

```bash
python test_email_account_ownership.py
```

The test script will:
1. Test getting emails for the authenticated user
2. Test sending new emails with account ownership fields
3. Test filtering by task and inbox emails
4. Verify that all emails have proper `account_owner` and `email_holder` values

## Migration Notes

### Existing Data
For existing emails without `account_owner` and `email_holder` fields:
- The system will gracefully handle missing fields (they will be `None`)
- New emails will have these fields populated
- Consider running a migration script to populate missing fields

### Backward Compatibility
- All existing API endpoints continue to work
- Missing account ownership fields are treated as `None`
- No breaking changes to existing functionality 