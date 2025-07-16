# Email Sending Guide

This guide explains how to fix email sending issues in the Email Agent API.

## 🔍 **Problem Diagnosis**

If you're getting a "success" response but emails are not being delivered, the issue is likely one of the following:

1. **SMTP Not Configured**: Email service is in development mode
2. **Invalid SMTP Credentials**: Wrong username/password
3. **Gmail App Password Required**: Regular password won't work
4. **Network/Firewall Issues**: SMTP port blocked

## ✅ **Solution 1: Configure SMTP for Real Email Sending**

### Step 1: Set up Gmail App Password

1. **Enable 2-Factor Authentication** on your Gmail account
2. **Generate App Password**:
   - Go to Google Account settings
   - Security → 2-Step Verification → App passwords
   - Generate password for "Mail"
   - Copy the 16-character password

### Step 2: Configure Environment Variables

Add these to your `.env` file:

```bash
# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-16-char-app-password
SMTP_USE_TLS=true
```

### Step 3: Test Configuration

Restart your server and try sending an email. You should see detailed logs:

```
📧 Sending email via SMTP:
   Server: smtp.gmail.com:587
   From: your-email@gmail.com
   To: recipient@example.com
   Subject: Test Email
   🔐 Starting TLS...
   🔑 Logging in as your-email@gmail.com...
   📤 Sending message...
   ✅ Email sent successfully!
```

## ✅ **Solution 2: Alternative Email Providers**

### Outlook/Hotmail
```bash
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
SMTP_USERNAME=your-email@outlook.com
SMTP_PASSWORD=your-password
SMTP_USE_TLS=true
```

### Yahoo Mail
```bash
SMTP_SERVER=smtp.mail.yahoo.com
SMTP_PORT=587
SMTP_USERNAME=your-email@yahoo.com
SMTP_PASSWORD=your-app-password
SMTP_USE_TLS=true
```

### Custom SMTP Server
```bash
SMTP_SERVER=your-smtp-server.com
SMTP_PORT=587
SMTP_USERNAME=your-username
SMTP_PASSWORD=your-password
SMTP_USE_TLS=true
```

## 🔧 **Troubleshooting**

### Error: "SMTP Authentication failed"

**Causes:**
- Wrong username/password
- Using regular password instead of app password
- 2FA not enabled

**Solutions:**
1. Double-check your credentials
2. Use app password for Gmail
3. Enable 2FA if required

### Error: "SMTP Recipients refused"

**Causes:**
- Invalid recipient email address
- Recipient server rejecting emails
- Sender domain not authorized

**Solutions:**
1. Verify recipient email addresses
2. Check spam/junk folders
3. Use a verified sender domain

### Error: "SMTP Server disconnected"

**Causes:**
- Wrong SMTP server/port
- Network connectivity issues
- Firewall blocking SMTP

**Solutions:**
1. Verify SMTP settings
2. Check network connection
3. Allow SMTP port (587/465) through firewall

### Error: "SMTP not configured"

**Causes:**
- Missing environment variables
- Empty SMTP credentials

**Solutions:**
1. Set all required SMTP environment variables
2. Restart the server after configuration

## 🧪 **Testing Email Configuration**

### Test Script

Create a test script to verify your SMTP configuration:

```python
#!/usr/bin/env python3
"""
Test SMTP Configuration
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

def test_smtp_config():
    # Get SMTP settings from environment
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_username = os.getenv("SMTP_USERNAME", "")
    smtp_password = os.getenv("SMTP_PASSWORD", "")
    smtp_use_tls = os.getenv("SMTP_USE_TLS", "true").lower() == "true"
    
    print(f"🔧 Testing SMTP Configuration:")
    print(f"   Server: {smtp_server}:{smtp_port}")
    print(f"   Username: {smtp_username}")
    print(f"   TLS: {smtp_use_tls}")
    
    if not smtp_username or not smtp_password:
        print("❌ SMTP_USERNAME or SMTP_PASSWORD not set")
        return False
    
    try:
        # Create test message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "SMTP Test Email"
        msg['From'] = smtp_username
        msg['To'] = smtp_username  # Send to yourself for testing
        
        text_part = MIMEText("This is a test email to verify SMTP configuration.", 'plain')
        msg.attach(text_part)
        
        # Connect and send
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            if smtp_use_tls:
                print("   🔐 Starting TLS...")
                server.starttls()
            
            print("   🔑 Logging in...")
            server.login(smtp_username, smtp_password)
            
            print("   📤 Sending test email...")
            server.send_message(msg)
            
            print("   ✅ SMTP configuration is working!")
            return True
            
    except Exception as e:
        print(f"   ❌ SMTP test failed: {e}")
        return False

if __name__ == "__main__":
    test_smtp_config()
```

### API Test

Test the email sending API:

```bash
# Test email sending
curl -X POST "http://localhost:8000/api/emails/send" \
  -H "Authorization: Bearer your_session_id" \
  -H "Content-Type: application/json" \
  -d '{
    "recipients": ["test@example.com"],
    "subject": "Test Email",
    "body": "This is a test email to verify the API is working."
  }'
```

## 📊 **Monitoring Email Status**

### Check Email Status

After sending an email, check its status:

```bash
# Get email details
curl -H "Authorization: Bearer your_session_id" \
  "http://localhost:8000/api/emails/{email_id}"
```

### Status Meanings

- **`draft`**: Email created but not sent
- **`sending`**: Email is currently being sent
- **`sent`**: Email sent successfully
- **`failed`**: Email failed to send
- **`scheduled`**: Email scheduled for future sending

## 🚀 **Production Considerations**

### Security

1. **Use Environment Variables**: Never hardcode SMTP credentials
2. **App Passwords**: Use app passwords instead of regular passwords
3. **TLS**: Always use TLS for SMTP connections
4. **Rate Limiting**: Implement rate limiting for email sending

### Monitoring

1. **Log Email Events**: Log all email sending attempts
2. **Monitor Failures**: Set up alerts for email sending failures
3. **Track Delivery**: Monitor email delivery rates
4. **Bounce Handling**: Handle email bounces and invalid addresses

### Scaling

1. **Email Queues**: Use message queues for high-volume sending
2. **Multiple SMTP Providers**: Use multiple SMTP providers for redundancy
3. **Connection Pooling**: Reuse SMTP connections
4. **Async Processing**: Process emails asynchronously

## 📝 **Common Issues and Solutions**

| Issue | Cause | Solution |
|-------|-------|----------|
| Emails not delivered | SMTP not configured | Set up SMTP credentials |
| Authentication failed | Wrong password | Use app password for Gmail |
| Connection refused | Wrong port/server | Verify SMTP settings |
| Emails in spam | Poor sender reputation | Use verified domain |
| Rate limited | Too many emails | Implement rate limiting |

## 🔗 **Additional Resources**

- [Gmail SMTP Settings](https://support.google.com/mail/answer/7126229)
- [Gmail App Passwords](https://support.google.com/accounts/answer/185833)
- [SMTP Ports](https://en.wikipedia.org/wiki/Simple_Mail_Transfer_Protocol#Ports)
- [Email Authentication](https://en.wikipedia.org/wiki/Email_authentication) 