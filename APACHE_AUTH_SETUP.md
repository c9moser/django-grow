# Apache Form-Based Authentication with Django mod_wsgi - Setup Guide

This guide explains the Apache AuthForm implementation integrated with Django's session-based authentication via mod_wsgi.

## Overview

The system validates HTTP requests against Django sessions rather than a traditional password file. Features:

- **Session-based auth**: Uses existing Django login sessions
- **Form authentication**: Apache displays login form on 401 responses
- **Transparent to Django**: No changes needed to Django URLs/views
- **Protected paths**: Can protect specific directories (/media/, etc.)

## Components

### 1. Django auth_wsgi.py

Located at: `django_project/auth_wsgi.py`

Key functions for Apache mod_wsgi:

| Function | Purpose |
|----------|---------|
| `check_password()` | Validates session and username match |
| `decode_session()` | Loads session data for Apache |
| `encode_session()` | Saves session modifications |
| `load_session()` | Retrieves raw session data |
| `save_session()` | Persists session to database |
| `groups_for_user()` | Returns user groups (imported from Django) |

### 2. Apache VirtualHost Configuration

Located at: `apacheconf/000-grow.conf`

Key directives:

```apache
<Directory ${GROW_MEDIA_ROOT}>
    Require all granted
    AllowOverride all

    # Enable form-based authentication
    AuthType Form
    AuthName "Controlled Access"
    AuthFormProvider wsgi

    # Redirect unauthenticated users to login
    AuthFormLoginRequiredLocation /accounts/login?next=%{REQUEST_URI}

    # Use Django for authentication
    WSGIAuthUserScript /app/django_project/auth_wsgi.py
    WSGIAuthGroupScript /app/django_project/auth_wsgi.py
</Directory>
```

## How It Works

### Authentication Flow

```
Client Request
    ↓
Apache checks if session cookie exists
    ↓
YES: Call check_password(environ, username, password)
    ↓
    Retrieve Django session from database
        ↓
        Check if SESSION_KEY exists in decoded data
        ↓
        Load User object
        ↓
        Verify username matches
        ↓
        GRANT ACCESS
    ↓
NO: Return 401 → Apache redirects to AuthFormLoginRequiredLocation
    ↓
User logs in via Django (/accounts/login)
    ↓
Django creates session cookie
    ↓
Next request includes session cookie
    ↓
Process repeats, now authenticated
```

### Session Data Flow

1. **Load**: Apache requests `load_session()` → Django session data loaded
2. **Decode**: Apache requests `decode_session()` → Inject username/pw keys
3. **Use**: Session available to mod_wsgi logged-in user
4. **Encode**: Apache requests `encode_session()` → Remove auth keys
5. **Save**: Apache requests `save_session()` → Store in database

## Configuration Options

### Apache Directives

```apache
# Authentication method
AuthType Form

# Name of auth realm (can have multiple)
AuthName "Controlled Access"

# Provider - must be "wsgi" for mod_wsgi
AuthFormProvider wsgi

# Redirect URL for unauthenticated access
AuthFormLoginRequiredLocation /accounts/login?next=%{REQUEST_URI}

# Path to Django auth script
WSGIAuthUserScript /app/django_project/auth_wsgi.py
WSGIAuthGroupScript /app/django_project/auth_wsgi.py
```

### Python Settings (auth_wsgi.py)

```python
APACHE_AUTH_KEY = u"AUTH_NAME"      # HTTP_AUTH_NAME when AuthName set
APACHE_USER_KEY = u"user"            # Key for username in session
APACHE_PASS_KEY = u"pw"              # Key for password in session
```

## Environment Setup

### Required Django Settings

The following must be configured in `settings.py`:

```python
# Session engine (default is fine)
SESSION_ENGINE = 'django.contrib.sessions.models'

# Session cookie name
SESSION_COOKIE_NAME = 'sessionid'

# Your domain
SESSION_COOKIE_DOMAIN = 'grow.example.com'

# Session expiration (in seconds)
SESSION_COOKIE_AGE = 1209600  # 2 weeks
```

### Apache Modules

Required modules:

```bash
a2enmod wsgi           # Python WSGI support
a2enmod authn_core    # Core authentication
a2enmod authz_core    # Authorization
a2enmod session        # Session management
```

### Permissions

The `auth_wsgi.py` script needs database access:

```bash
# Ensure readable by Apache worker
chown www-data:www-data django_project/auth_wsgi.py
chmod 640 django_project/auth_wsgi.py

# Database file permissions
chown www-data:www-data db.sqlite3
chmod 660 db.sqlite3
```

## Troubleshooting

### Users can't access protected content after login

1. **Check session cookie**: Verify Django creates session on login
   ```bash
   # In Django shell
   from django.contrib.sessions.models import Session
   Session.objects.all().count()  # Should have entries
   ```

2. **Verify Apache logs**:
   ```bash
   tail -f /var/log/apache2/error.log
   ```

3. **Check username match**: Ensure `user.get_username()` returns expected value

### 502 Bad Gateway

1. Check Apache error log for Python errors
2. Verify Django setup() completes successfully
3. Ensure database is accessible from Apache process

### Session data lost

1. **Session expiration**: Check `SESSION_COOKIE_AGE`
2. **Database cleanup**: Django periodically cleans expired sessions
   ```bash
   python manage.py clearsessions
   ```

3. **Multiple auth realms**: Different `AuthName` values need different keys

## Security Considerations

### Form-Based Auth

- **HTTPS Required**: Always use HTTPS in production
  ```apache
  # Redirect HTTP to HTTPS
  Redirect permanent / https://grow.example.com/
  ```

- **Secure Cookie Flag**: Set in Django settings
  ```python
  SESSION_COOKIE_SECURE = True      # Only send over HTTPS
  SESSION_COOKIE_HTTPONLY = True    # Prevent JS access
  ```

- **CSRF Protection**: Already enabled in Django forms

### Protected Directories

- **Don't protect**: Static files, public downloads
- **Protect**: User uploads, sensitive media, private files

```apache
# Example: Protect only user uploads
<Directory /var/www/grow/media/uploads>
    AuthType Form
    AuthName "Controlled Access"
    ...
</Directory>
```

## Testing

### Manual Test

```bash
# 1. Login via Django web interface
# Visit: http://localhost:8000/accounts/login

# 2. Try accessing protected media
curl -b cookies.txt http://localhost/media/protected.pdf

# 3. Check Apache logs
tail -f /var/log/apache2/access.log
```

### Automated Test

```python
# tests/test_apache_auth.py
import os
from django.test import Client
from django.contrib.sessions.models import Session

class ApacheAuthTest(TestCase):
    def test_session_auth(self):
        # Create and login user
        user = User.objects.create_user('testuser', 'test@example.com', 'password')
        client = Client()
        client.login(username='testuser', password='password')

        # Session should exist
        sessions = Session.objects.all()
        self.assertTrue(sessions.exists())
```

## Performance Optimization

### Caching

Session lookups are database hits. Optimize with caching:

```python
# In settings.py
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'django-session-cache',
    }
}

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
```

### Direct Cache Backend

Avoids database on every request:

```python
SESSION_ENGINE = 'django.contrib.sessions.backends.cache_db'
```

## Multiple Auth Realms

Support multiple protected areas with different auth:

```apache
<Directory /var/www/grow/media>
    AuthName "Media Access"
    WSGIAuthUserScript /app/django_project/auth_wsgi.py
</Directory>

<Directory /var/www/grow/private>
    AuthName "Private Access"
    WSGIAuthUserScript /app/django_project/auth_wsgi.py
</Directory>
```

The `auth_wsgi.py` handles realm selection via `APACHE_AUTH_KEY`.

## Debugging Hooks

Enable debug logging in `auth_wsgi.py`:

```python
import logging
logger = logging.getLogger('django')

def check_password(environ, username, password):
    logger.debug(f"Auth check: user={username}")
    # ... rest of function
```

Check Django logs:

```bash
# In settings.py
LOGGING = {
    'version': 1,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '/var/log/django/auth.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'DEBUG',
        },
    },
}
```

## References

- [Apache mod_wsgi](https://modwsgi.readthedocs.io/)
- [Apache Authentication](https://httpd.apache.org/docs/current/howto/auth.html)
- [Django Sessions](https://docs.djangoproject.com/en/stable/topics/http/sessions/)
- [Django mod_wsgi Handler](https://docs.djangoproject.com/en/stable/ref/contrib/auth/#django.contrib.auth.handlers.modwsgi)
