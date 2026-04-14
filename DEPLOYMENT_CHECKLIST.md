# Apache AuthForm Deployment Checklist

Complete this checklist before deploying Apache Form-Based Authentication with Django mod_wsgi to production.

## Pre-Deployment

### Code Review

- [ ] Reviewed [django_project/auth_wsgi.py](django_project/auth_wsgi.py) for security issues
- [ ] All Python 3 compatibility issues fixed (`.items()` not `.iteritems()`, etc.)
- [ ] Exception handling in place for all database operations
- [ ] No hardcoded credentials or secrets in auth_wsgi.py
- [ ] Docstrings present for all functions
- [ ] Tests pass: `pytest tests/test_apache_auth.py`

### Configuration Review

- [ ] Apache config syntax valid: `apache2ctl configtest`
- [ ] VirtualHost ServerName set correctly
- [ ] AuthFormLoginRequiredLocation points to valid Django URL
- [ ] Protected directories are correct (usually `/media/`, `/private/`, etc.)
- [ ] Unrelated paths (static files, uploads) are not over-protected

### Django Setup

- [ ] Database migrations run: `python manage.py migrate`
- [ ] Sessions table created: `python manage.py dbshell` → `.tables | grep session`
- [ ] Settings configured:
  - [ ] `SESSION_ENGINE = 'django.contrib.sessions.backends.db'`
  - [ ] `SESSION_COOKIE_SECURE = True` (production)
  - [ ] `SESSION_COOKIE_HTTPONLY = True`
  - [ ] `SESSION_COOKIE_AGE` appropriate (e.g., 86400 for 1 day)
  - [ ] `ALLOWED_HOSTS` includes domain
  - [ ] `DEBUG = False`

### Permissions

- [ ] Database file readable by Apache user
  ```bash
  sudo chown www-data:www-data db.sqlite3
  sudo chmod 660 db.sqlite3
  ```

- [ ] auth_wsgi.py readable by Apache
  ```bash
  sudo chown root:root django_project/auth_wsgi.py
  sudo chmod 644 django_project/auth_wsgi.py
  ```

- [ ] Project directory accessible
  ```bash
  sudo chmod 755 /app /app/django_project
  ```

- [ ] Media directory permissions
  ```bash
  sudo chown www-data:www-data /var/www/grow/media
  sudo chmod 750 /var/www/grow/media
  ```

### Apache Modules

- [ ] Required modules installed and enabled:
  ```bash
  a2enmod wsgi
  a2enmod authn_core
  a2enmod authz_core
  a2enmod session
  a2enmod auth_form
  ```

- [ ] Verified with: `apache2ctl -M | grep wsgi`

### SSL/TLS Configuration

- [ ] SSL certificate obtained (Let's Encrypt or commercial)
- [ ] HTTPS VirtualHost configured
- [ ] HTTP → HTTPS redirect in place
- [ ] SESSION_COOKIE_SECURE = True
- [ ] SESSION_COOKIE_HTTPONLY = True
- [ ] SECURE_HSTS_SECONDS configured
- [ ] Security headers in place (CSP, X-Frame-Options, etc.)

## Testing

### Unit Tests

- [ ] All tests pass:
  ```bash
  python manage.py test tests.test_apache_auth
  ```

- [ ] Tests cover:
  - [ ] Valid session authentication
  - [ ] Missing session rejection
  - [ ] Expired session rejection
  - [ ] Username mismatch rejection
  - [ ] Session data encoding/decoding

### Manual Integration Tests

- [ ] Create test user
  ```bash
  python manage.py createsuperuser
  ```

- [ ] Test 1: Unauthenticated access denied
  ```bash
  curl -v http://localhost/media/
  # Expected: 401 Unauthorized
  ```

- [ ] Test 2: Login creates session
  ```bash
  # Use Django admin or login form
  # Verify session in database
  python manage.py shell -c "from django.contrib.sessions.models import Session; print(Session.objects.count())"
  ```

- [ ] Test 3: Authenticated access granted
  ```bash
  # With session cookie
  curl -b cookies.txt http://localhost/media/
  # Expected: 200 or 304
  ```

- [ ] Test 4: Logout revokes access
  ```bash
  # Logout, verify session deleted
  curl -v http://localhost/media/
  # Expected: 401 Unauthorized again
  ```

### Performance Tests

- [ ] Response time acceptable (< 100ms)
  ```bash
  for i in {1..10}; do curl -w "Time: %{time_total}s\n" -o /dev/null http://localhost/media/test.txt; done
  ```

- [ ] Load testing with expected traffic
  ```bash
  ab -n 1000 -c 10 https://grow.example.com/media/
  ```

- [ ] Database query performance acceptable
  - [ ] No N+1 queries
  - [ ] Session lookups use indexes

### Edge Cases

- [ ] Multiple simultaneous users
- [ ] Very long-running sessions
- [ ] Session expiration behavior
- [ ] Cookie handling (strict, lax, none)
- [ ] CORS requests (if applicable)
- [ ] Large file downloads
- [ ] Concurrent file access

## Deployment

### Pre-Deployment Backup

- [ ] Database backed up
  ```bash
  cp db.sqlite3 db.sqlite3.backup.$(date +%Y%m%d)
  ```

- [ ] Configuration backed up
  ```bash
  sudo cp /etc/apache2/sites-available/000-grow.conf /etc/apache2/sites-available/000-grow.conf.backup
  ```

- [ ] Code repository tagged
  ```bash
  git tag -a deploy-$(date +%Y%m%d) -m "Apache auth deployment"
  ```

### Deployment Steps

1. [ ] Stop Apache (dev only, use graceful for prod)
   ```bash
   sudo systemctl stop apache2  # dev
   sudo systemctl reload apache2  # prod
   ```

2. [ ] Deploy code
   ```bash
   git pull origin main
   ```

3. [ ] Run migrations (if needed)
   ```bash
   python manage.py migrate
   ```

4. [ ] Clear sessions if resetting
   ```bash
   python manage.py clearsessions
   ```

5. [ ] Verify permissions
   ```bash
   sudo chown www-data:www-data db.sqlite3
   sudo chmod 660 db.sqlite3
   ```

6. [ ] Start Apache
   ```bash
   sudo systemctl start apache2
   ```

7. [ ] Verify running
   ```bash
   sudo systemctl status apache2
   curl -v https://grow.example.com/
   ```

### Post-Deployment Verification

- [ ] Apache is running
  ```bash
  systemctl is-active apache2
  ps aux | grep apache2
  ```

- [ ] No errors in log
  ```bash
  sudo tail -20 /var/log/apache2/error.log
  ```

- [ ] Authentication works
  ```bash
  # Test unauthenticated
  curl -v https://grow.example.com/media/ | grep "401\|200"

  # Login and test authenticated
  # (Use browser or curl with cookies)
  ```

- [ ] Session table has entries
  ```bash
  python manage.py shell -c "from django.contrib.sessions.models import Session; print(f'Sessions: {Session.objects.count()}')"
  ```

- [ ] Monitoring alerts configured
  - [ ] 401 rate spike detection
  - [ ] 502 gateway errors
  - [ ] Database connectivity
  - [ ] Disk space

## Production Monitoring

### Daily Checks

- [ ] Apache running
  ```bash
  systemctl is-active apache2
  ```

- [ ] No excessive errors
  ```bash
  grep "ERROR\|CRITICAL" /var/log/apache2/error.log | wc -l
  ```

- [ ] Session table not growing unbounded
  ```bash
  python manage.py shell -c "from django.contrib.sessions.models import Session; print(f'Sessions: {Session.objects.count()}')"
  ```

### Weekly Tasks

- [ ] Clear expired sessions
  ```bash
  python manage.py clearsessions
  ```

- [ ] Review authentication logs
  ```bash
  grep "401" /var/log/apache2/access.log | tail -20
  ```

- [ ] Check database size
  ```bash
  du -h db.sqlite3
  ```

### Monthly Tasks

- [ ] Analyze performance trends
- [ ] Review and rotate logs
- [ ] Update SSL certificate (if needed)
- [ ] Security audit of auth_wsgi.py
- [ ] User access patterns review

## Rollback Plan

If deployment fails:

### Option 1: Revert Code

```bash
git checkout <previous-commit> -- django_project/auth_wsgi.py
sudo systemctl reload apache2
```

### Option 2: Disable Auth

```bash
# Temporarily comment out auth in Apache config
sudo nano /etc/apache2/sites-available/000-grow.conf
# Comment: # AuthType Form
sudo apache2ctl graceful
```

### Option 3: Restore Backup

```bash
# Restore database
cp db.sqlite3.backup db.sqlite3

# Restore apache config
sudo cp /etc/apache2/sites-available/000-grow.conf.backup /etc/apache2/sites-available/000-grow.conf

# Restart
sudo systemctl restart apache2
```

## Known Limitations

- [ ] Form-based auth requires cookies (no token auth)
- [ ] Session data limited by browser cookie size (typically 4KB)
- [ ] Cannot authenticate across different Django instances without shared session backend
- [ ] Performance depends on database performance
- [ ] SQLite not recommended for high-concurrency production

## Post-Deployment Notes

- [ ] Document any custom settings
- [ ] Record admin user credentials securely
- [ ] Brief operations team on maintenance procedures
- [ ] Schedule training if needed
- [ ] Create runblock for common troubleshooting

---

**Deployment Date**: ________________

**Deployed By**: ________________

**Verified By**: ________________

**Notes**: ________________________________________________________________
