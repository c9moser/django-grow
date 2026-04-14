# Apache AuthForm Debugging Guide

This guide helps troubleshoot issues with Apache Form-Based Authentication integrated with Django mod_wsgi.

## Quick Diagnosis

### Check Apache Error Logs

```bash
# Real-time error monitoring
tail -f /var/log/apache2/error.log

# Search for specific module
grep "wsgi\|auth" /var/log/apache2/error.log | tail -20

# Check for Python exceptions
grep "Traceback\|Exception\|Error" /var/log/apache2/error.log
```

### Check Apache Access Logs

```bash
# View access attempts
tail -f /var/log/apache2/access.log

# Filter for 401 (Unauthorized)
grep " 401 " /var/log/apache2/access.log

# Filter for protected paths
grep "/media/" /var/log/apache2/access.log
```

## Common Issues and Solutions

### Issue 1: "ModuleNotFoundError: No module named 'django'"

**Symptom**: `ModuleNotFoundError: No module named 'django'` in error.log

**Cause**: Django not installed in Apache's Python environment or path incorrect

**Solution**:

```python
# In auth_wsgi.py, add debugging
import sys
print(f"Python path: {sys.path}", file=sys.stderr)
print(f"Python version: {sys.version}", file=sys.stderr)

# Try importing Django
try:
    import django
    print(f"Django version: {django.VERSION}", file=sys.stderr)
except ImportError as e:
    print(f"Django import failed: {e}", file=sys.stderr)
```

```bash
# Check Apache's Python environment
/usr/bin/python3 -c "import sys; print('\\n'.join(sys.path))"

# Install packages to system Python if using system interpreter
sudo pip install django

# Or use virtualenv from Apache config
# Ensure WSGIDaemonProcess includes python-home
WSGIDaemonProcess grow python-home=/home/c9mos/.cache/pypoetry/virtualenvs/django-grow-FntpUFHn-py3.11
```

### Issue 2: "AttributeError: 'NoneType' object has no attribute 'get_decoded'"

**Symptom**: Session is None when trying to decode

**Cause**: Session cookie not found or session expired

**Solution**: Added None check in fixed auth_wsgi.py:

```python
def check_password(environ, username, password):
    s = __get_session_(environ)
    if s is None:               # ← This check prevents the error
        return False

    session_data = s.get_decoded()
```

**Debug**: Check if cookies are being sent:

```python
def check_password(environ, username, password):
    # Add debugging
    import sys

    sys.stderr.write(f"Cookies: {environ.get('HTTP_COOKIE', 'NONE')}\n")
    sys.stderr.flush()

    s = __get_session_(environ)
    sys.stderr.write(f"Session object: {s}\n")
    sys.stderr.flush()
```

### Issue 3: "ProgrammingError: no such table: django_sessions"

**Symptom**: Error accessing sessions table

**Cause**: Migrations not run or database not configured

**Solution**:

```bash
# Run migrations with Apache user permissions
sudo -u www-data python manage.py migrate

# Check database exists and is readable
ls -la db.sqlite3
sudo -u www-data python manage.py shell -c "from django.contrib.sessions.models import Session; print(Session.objects.count())"
```

### Issue 4: Users can login but still get 401 on /media/

**Symptom**: Django login works, but Apache still denies media access

**Cause**:
1. Session cookie not being sent by browser
2. Session expires between requests
3. Username mismatch

**Debug steps**:

```python
# Add comprehensive logging to auth_wsgi.py
import logging
logger = logging.getLogger('django')

def check_password(environ, username, password):
    logger.debug(f"=== Auth Check Start ===")
    logger.debug(f"Username: {username}")
    logger.debug(f"Cookies: {environ.get('HTTP_COOKIE', 'NONE')}")

    s = __get_session_(environ)
    logger.debug(f"Session: {s}")

    if s is None:
        logger.debug("No session found")
        return False

    session_data = s.get_decoded()
    logger.debug(f"Session keys: {session_data.keys()}")

    from django.contrib.auth import SESSION_KEY
    if SESSION_KEY in session_data:
        user_id = session_data[SESSION_KEY]
        logger.debug(f"User ID from session: {user_id}")

        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.get(pk=user_id)
        logger.debug(f"User: {user.username}")
        logger.debug(f"Username match: {user.username} == {username}")

    # ... rest of function
```

**Check session cookies in browser**:

```bash
# In browser developer tools (F12 → Application → Cookies)
# Look for "sessionid" or name matching SESSION_COOKIE_NAME

# Or check programmatically
python manage.py shell
>>> from django.contrib.sessions.models import Session
>>> for s in Session.objects.all():
...     print(f"Session {s.pk}: expires {s.expire_date}")
```

### Issue 5: "502 Bad Gateway"

**Symptom**: Blank 502 error

**Cause**: WSGI daemon process crashed

**Solution**:

```bash
# Check if daemon process is running
ps aux | grep WSGIDaemonProcess

# Check for obvious errors in Apache config
apache2ctl configtest

# Check detailed Apache error log
journalctl -u apache2 -n 50

# Manually test auth_wsgi.py
python /app/django_project/auth_wsgi.py
```

### Issue 6: "Timeout waiting for auth response"

**Symptom**: Requests hang when accessing /media/

**Cause**:
1. Database connection timeout
2. Django setup() hangs
3. Infinite loop in auth functions

**Solution**:

```python
# Add timeout protection
import signal

def timeout_handler(signum, frame):
    raise TimeoutError("Auth check timed out")

def check_password(environ, username, password):
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(5)  # 5 second timeout

    try:
        # ... auth logic
    finally:
        signal.alarm(0)  # Cancel alarm
```

## Manual Testing

### Test 1: Django Session Creation

```bash
python manage.py shell

from django.contrib.auth import get_user_model
from django.contrib.sessions.models import Session

User = get_user_model()
user = User.objects.first()

# Create session
from django.contrib.sessions.backends.db import SessionStore
session = SessionStore()
session[SESSION_KEY] = user.pk
session.save()

print(f"Session ID: {session.session_key}")
print(f"Session data: {session.get_decoded()}")
```

### Test 2: Simulate Apache Request

```bash
python manage.py shell

import sys
sys.path.insert(0, '/app')

from django_project.auth_wsgi import check_password
from django.conf import settings

# Get a valid session
from django.contrib.sessions.models import Session
session_obj = Session.objects.first()

# Simulate environ
environ = {
    'HTTP_COOKIE': f'{settings.SESSION_COOKIE_NAME}={session_obj.pk}'
}

# Test authentication
result = check_password(environ, 'username', 'password')
print(f"Auth result: {result}")
```

### Test 3: Check Session Data Format

```bash
python manage.py shell

from django.contrib.sessions.models import Session
from django.contrib.auth import SESSION_KEY

session = Session.objects.first()
decoded = session.get_decoded()

print("Session contents:")
for key, value in decoded.items():
    print(f"  {key}: {value}")

print(f"\nSession KEY constant: {SESSION_KEY}")
```

## Apache Configuration Issues

### Check Virtual Host Configuration

```bash
# Verify config syntax
apache2ctl -S

# Look for auth directives
apache2ctl -D DUMP_VHOSTS | grep -A 20 "media"

# Manually test with curl
curl -v http://localhost/media/
# Should see "401 Unauthorized" if auth required
```

### Enable Apache Debug Logging

```apache
# In /etc/apache2/sites-available/000-grow.conf

<VirtualHost *:80>
    # ... existing config ...

    LogLevel debug

    <Directory ${GROW_MEDIA_ROOT}>
        AuthType Form
        AuthName "Controlled Access"
        # ... auth config ...

        # Debug authentication
        LogLevel auth:debug
    </Directory>
</VirtualHost>
```

```bash
# Reload and test
apache2ctl graceful

# View detailed auth logs
tail -f /var/log/apache2/error.log | grep auth
```

## Database Issues

### Check Django Session Table

```bash
# Inspect database directly
sqlite3 db.sqlite3

# See sessions table structure
.schema django_sessions

# Count sessions
SELECT COUNT(*) FROM django_sessions;

# See session details
SELECT session_key, session_data, expire_date FROM django_sessions LIMIT 5;

# Clean expired sessions
DELETE FROM django_sessions WHERE expire_date < datetime('now');
```

### Permissions

```bash
# Check file permissions
ls -la /app/db.sqlite3
ls -la /app/django_project/auth_wsgi.py
ls -la /app/django_project/

# Fix ownership
sudo chown www-data:www-data /app/db.sqlite3
sudo chmod 660 /app/db.sqlite3

sudo chown www-data:www-data /app/django_project/auth_wsgi.py
sudo chmod 640 /app/django_project/auth_wsgi.py
```

## Performance Debugging

### Slow Authentication

```python
# In auth_wsgi.py, add timing
import time
import logging

logger = logging.getLogger('django')

def check_password(environ, username, password):
    start = time.time()

    s = __get_session_(environ)
    logger.debug(f"Get session: {(time.time() - start)*1000:.1f}ms")

    if s is None:
        return False

    # ... decode logic ...

    logger.debug(f"Total auth time: {(time.time() - start)*1000:.1f}ms")
    return result
```

Check log for slow operations:

```bash
tail -f /var/log/django/auth.log | grep "ms"
```

### Database Query Analysis

```python
# Debug database queries
from django.db import connection
from django.test.utils import override_settings

def check_password(environ, username, password):
    from django.conf import settings

    with override_settings(DEBUG=True):
        # ... auth logic ...

        for query in connection.queries:
            print(f"Query time: {query['time']}ms")
            print(f"SQL: {query['sql']}\n")
```

## Validation Checklist

Before deploying to production:

- [ ] Django setup() completes without errors
- [ ] Session table exists and is accessible
- [ ] Apache can read auth_wsgi.py file
- [ ] Apache has database file permissions
- [ ] SSL/HTTPS is configured (if in production)
- [ ] SESSION_COOKIE_SECURE set appropriately
- [ ] AuthFormLoginRequiredLocation points to valid URL
- [ ] Test user can login and access /media/
- [ ] Logout works and revokes access
- [ ] Session expiration is tested
- [ ] Multiple concurrent users tested
- [ ] Load testing with expected traffic

## Emergency Recovery

### Reset Authentication

```bash
# Clear all sessions (forces re-login)
python manage.py shell -c "from django.contrib.sessions.models import Session; Session.objects.all().delete()"

# Restart Apache
sudo systemctl restart apache2

# Check status
sudo systemctl status apache2
```

### Disable Authentication (Temporary)

```apache
# Comment out auth directives
<Directory ${GROW_MEDIA_ROOT}>
    # AuthType Form
    # AuthName "Controlled Access"
    # ... other auth config ...
</Directory>
```

### Revert to Last Known Good

```bash
# Check git history
git log --oneline django_project/auth_wsgi.py

# Revert if needed
git checkout <commit-hash> -- django_project/auth_wsgi.py
```

## Getting Help

When reporting issues, collect:

```bash
# System info
echo "=== System ==="
uname -a
apache2 -v
python3 --version

# Apache info
echo "=== Apache ==="
apache2ctl -M | grep wsgi
apache2ctl -S

# Django info
python manage.py --version
python -c "import django; print(django.VERSION)"

# Error logs (last 50 lines)
echo "=== Error Log ==="
tail -50 /var/log/apache2/error.log

# Config
echo "=== Apache Config ==="
cat /etc/apache2/sites-enabled/000-grow.conf
```
