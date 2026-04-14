# Apache AuthForm Quick Reference

**TL;DR - Apache Form-Based Auth with Django mod_wsgi**

## What It Does

Protects `/media/` (or other paths) with Apache authentication backed by Django sessions. Users must login via Django before accessing protected files.

## Quick Setup

### 1. Django Settings

```python
# settings.py
INSTALLED_APPS = [
    'django.contrib.sessions',  # Required
    'django.contrib.auth',       # Required
    # ...
]

SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = True  # Production only
```

### 2. Run Migrations

```bash
python manage.py migrate
```

### 3. Check auth_wsgi.py

```bash
# No changes needed if using included fixed version
cat django_project/auth_wsgi.py | head -25
```

### 4. Enable Apache Modules

```bash
sudo a2enmod authn_core authz_core session auth_form wsgi
sudo apache2ctl graceful
```

### 5. Test

```bash
# Should get 401
curl -v http://localhost/media/

# Login via Django, then test with session cookie
curl -b cookies.txt http://localhost/media/
```

## Common Tasks

### Protect a Directory

In `apacheconf/000-grow.conf`:

```apache
<Directory /var/www/grow/media>
    Require all granted

    AuthType Form
    AuthName "Controlled Access"
    AuthFormProvider wsgi
    AuthFormLoginRequiredLocation /accounts/login?next=%{REQUEST_URI}

    WSGIAuthUserScript /app/django_project/auth_wsgi.py
    WSGIAuthGroupScript /app/django_project/auth_wsgi.py
</Directory>
```

Then reload: `sudo apache2ctl graceful`

### Create Test User

```bash
python manage.py createsuperuser
```

### Test Authentication

```bash
# Unauthenticated - should be 401
curl -v http://localhost/media/test.pdf

# Get session cookie (login via Django first)
# Then use it to access
curl -b SESSION_COOKIE http://localhost/media/test.pdf
```

### Clear Sessions (Force Re-login)

```bash
python manage.py clearsessions
```

### Check Session Database

```bash
python manage.py shell
>>> from django.contrib.sessions.models import Session
>>> Session.objects.count()
5
>>> for s in Session.objects.all():
...     print(s.pk, s.expire_date)
```

## Troubleshooting

### Users can't access after login

**Check:** Does Django create a session?

```bash
python manage.py shell
from django.contrib.sessions.models import Session
print(Session.objects.count())  # Should be > 0 after login
```

**Fix:** Usually SESSION_COOKIE_DOMAIN or SECURE flag issue

### 502 Bad Gateway

**Check:** Apache error log

```bash
tail -20 /var/log/apache2/error.log
```

**Fix:** Usually Python import error or database issue

### 401 Even With Session Cookie

**Check:** Does cookie match exactly?

```python
curl -b sessionid=abc123 http://localhost/media/
# vs
curl -b "sessionid=abc123" http://localhost/media/
```

### Performance Issues

**Check:** Session lookups are per-request database hits

**Fix:** Add caching:

```python
# settings.py
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
```

## File Reference

| File | Purpose |
|------|---------|
| [django_project/auth_wsgi.py](django_project/auth_wsgi.py) | Auth handler (FIXED) |
| [apacheconf/000-grow.conf](apacheconf/000-grow.conf) | Apache config (already has auth) |
| [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) | What was done |
| [APACHE_AUTH_SETUP.md](APACHE_AUTH_SETUP.md) | Full setup guide |
| [APACHE_AUTH_DEBUG.md](APACHE_AUTH_DEBUG.md) | Troubleshooting |
| [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) | Deploy steps |
| [tests/test_apache_auth.py](tests/test_apache_auth.py) | Test suite |

## Key Functions in auth_wsgi.py

```python
check_password(environ, username, password)
    # Called by Apache on every protected request
    # Returns True if session is valid, False otherwise

load_session(environ)
    # Load session data from Django database

decode_session(environ, data)
    # Convert to bytes format Apache expects

encode_session(environ, data)
    # Remove auth keys before saving session

save_session(environ, data)
    # Persist session changes to database
```

## FAQ

**Q: Does the user need to login for each request?**
A: No, login creates a session with a cookie. Browser sends cookie on each request, so login is one-time.

**Q: Can I use this with multiple domains?**
A: Yes, set `SESSION_COOKIE_DOMAIN` and deploy multiple auth realms with different `AuthName` values.

**Q: Is it secure?**
A: Yes if you:
- Use HTTPS (`SESSION_COOKIE_SECURE = True`)
- Disable JavaScript access (`SESSION_COOKIE_HTTPONLY = True`)
- Don't expose auth_wsgi.py publicly

**Q: Does it work with file downloads?**
A: Yes, Apache serves files after authentication passes.

**Q: Can I cache sessions?**
A: Yes, use Redis or Memcached for better performance under load.

**Q: What about CSRF protection?**
A: Django forms have CSRF built-in. API endpoints need explicit token validation.

**Q: Can I use group-based authorization?**
A: Yes, Apache can check groups with `Require group` directive. Function `groups_for_user()` returns user's groups.

## One-Liner Tests

```bash
# Verify protected (should 401)
curl -w "\nStatus: %{http_code}\n" http://localhost/media/

# After login, verify access (should 200/304)
curl -b cookies.txt -w "\nStatus: %{http_code}\n" http://localhost/media/

# Check Apache modules
apache2ctl -M | grep wsgi

# Check auth_wsgi syntax
python -m py_compile django_project/auth_wsgi.py && echo "OK"

# Quick Django shell test
python manage.py shell -c "from django_project import auth_wsgi; print('OK')"
```

## Production Checklist (5-Minute)

- [ ] Django migrations run: `python manage.py migrate`
- [ ] Apache modules enabled: `a2enmod wsgi`
- [ ] Settings configured: `SESSION_COOKIE_SECURE = True`
- [ ] Test works: `curl -v http://localhost/media/` → 401
- [ ] Error logs clean: `tail /var/log/apache2/error.log`

## Emergency Recovery

```bash
# Disable auth temporarily
sudo sed -i 's/AuthType Form/#AuthType Form/g' /etc/apache2/sites-available/000-grow.conf
sudo apache2ctl graceful

# Force re-authentication
python manage.py clearsessions
sudo systemctl restart apache2

# Restart Apache
sudo systemctl restart apache2
```

## Get Help

1. Check [APACHE_AUTH_DEBUG.md](APACHE_AUTH_DEBUG.md) for your specific issue
2. Review Apache error logs: `sudo tail -50 /var/log/apache2/error.log`
3. Test session database: `python manage.py shell`
4. Check Apache config: `apache2ctl -S`
5. Look for Python tracebacks in error log

## Performance Tips

Typical response times:
- **First request (cold)**: 50-100ms
- **Subsequent requests (cached)**: 5-10ms

To optimize:
1. Add Redis caching
2. Use `SESSION_ENGINE = 'django.contrib.sessions.backends.cache'`
3. Monitor with: `curl -w "Time: %{time_total}s\n"`

---

See [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) for details on what was fixed and created.
