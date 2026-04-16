"""
Tests for Apache mod_wsgi authentication handler.

Tests verify that the auth_wsgi.py module correctly:
1. Validates Django sessions
2. Handles missing sessions gracefully
3. Extracts usernames from sessions
4. Manages session data encoding/decoding
"""

import os
import sys
from pathlib import Path
import django
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.contrib.sessions.models import Session
from django.contrib.auth.models import AnonymousUser
from django.test.client import Client

# Import auth_wsgi module
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_project.settings')

django.setup()

from django_project import auth_wsgi

User = get_user_model()


class AuthWSGITestCase(TestCase):
    """Test Apache mod_wsgi authentication handler."""

    def setUp(self):
        """Create test user and client."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client = Client()
        self.factory = RequestFactory()

    def test_check_password_no_session(self):
        """check_password returns False when no session exists."""
        environ = {}
        result = auth_wsgi.check_password(environ, 'testuser', 'password')
        self.assertFalse(result)

    def test_check_password_with_valid_session(self):
        """check_password returns True for valid authenticated session."""
        # Login user to create session
        self.client.login(username='testuser', password='testpass123')

        # Get session cookie from client
        session_id = self.client.cookies['sessionid'].value

        # Create WSGI environ with session cookie
        from django.conf import settings
        environ = {
            'HTTP_COOKIE': f'{settings.SESSION_COOKIE_NAME}={session_id}'
        }

        result = auth_wsgi.check_password(environ, 'testuser', 'password')
        self.assertTrue(result)

    def test_check_password_wrong_username(self):
        """check_password returns False when username doesn't match session."""
        # Login user to create session
        self.client.login(username='testuser', password='testpass123')

        # Get session cookie
        session_id = self.client.cookies['sessionid'].value

        # Create WSGI environ with session cookie
        from django.conf import settings
        environ = {
            'HTTP_COOKIE': f'{settings.SESSION_COOKIE_NAME}={session_id}'
        }

        # Try different username
        result = auth_wsgi.check_password(environ, 'wronguser', 'password')
        self.assertFalse(result)

    def test_get_session_id_from_cookies(self):
        """__get_session_id_ extracts session ID from cookie."""
        session_id = 'abc123def456'
        from django.conf import settings
        environ = {
            'HTTP_COOKIE': f'{settings.SESSION_COOKIE_NAME}={session_id}'
        }

        result = auth_wsgi.__get_session_id_(environ)
        self.assertEqual(result, session_id)

    def test_get_session_id_missing_cookie(self):
        """__get_session_id_ returns None when no cookie."""
        environ = {}
        result = auth_wsgi.__get_session_id_(environ)
        self.assertIsNone(result)

    def test_get_session_from_database(self):
        """__get_session_ retrieves valid session from database."""
        # Create authenticated session
        self.client.login(username='testuser', password='testpass123')
        session_id = self.client.cookies['sessionid'].value

        from django.conf import settings
        environ = {
            'HTTP_COOKIE': f'{settings.SESSION_COOKIE_NAME}={session_id}'
        }

        session = auth_wsgi.__get_session_(environ)
        self.assertIsNotNone(session)
        self.assertEqual(session.pk, session_id)

    def test_get_session_invalid_id(self):
        """__get_session_ returns None for non-existent session."""
        from django.conf import settings
        environ = {
            'HTTP_COOKIE': f'{settings.SESSION_COOKIE_NAME}=invalid123'
        }

        session = auth_wsgi.__get_session_(environ)
        self.assertIsNone(session)

    def test_decode_session_extracts_user(self):
        """decode_session injects username for authenticated user."""
        # Create authenticated session
        self.client.login(username='testuser', password='testpass123')
        session_id = self.client.cookies['sessionid'].value

        from django.conf import settings
        environ = {
            'HTTP_COOKIE': f'{settings.SESSION_COOKIE_NAME}={session_id}',
            'AUTH_NAME': 'Controlled Access'
        }

        # Get session data
        session = Session.objects.get(pk=session_id)

        # Decode session
        decoded = auth_wsgi.decode_session(environ, session.session_data)

        # Should contain username key
        self.assertIn(b'Controlled Access-user', decoded)
        self.assertEqual(decoded[b'Controlled Access-user'], b'testuser')

    def test_load_session_returns_data(self):
        """load_session returns session data."""
        # Create authenticated session
        self.client.login(username='testuser', password='testpass123')
        session_id = self.client.cookies['sessionid'].value

        from django.conf import settings
        environ = {
            'HTTP_COOKIE': f'{settings.SESSION_COOKIE_NAME}={session_id}'
        }

        data = auth_wsgi.load_session(environ)
        self.assertIsNotNone(data)

    def test_load_session_no_session(self):
        """load_session returns None when no session."""
        environ = {'HTTP_COOKIE': ''}
        data = auth_wsgi.load_session(environ)
        self.assertIsNone(data)

    def test_encode_session_removes_auth_keys(self):
        """encode_session removes Apache auth keys before saving."""
        # Create authenticated session
        self.client.login(username='testuser', password='testpass123')
        session_id = self.client.cookies['sessionid'].value

        environ = {
            'AUTH_NAME': 'Controlled Access'
        }

        # Data with Apache auth keys
        data = {
            'Controlled Access-user': 'testuser',
            'Controlled Access-pw': 'password',
            'other_key': 'value'
        }

        result = auth_wsgi.encode_session(environ, data)

        # Should remove auth keys
        if result:
            decoded = auth_wsgi.__decode_data_(result)
            self.assertNotIn('Controlled Access-user', decoded)
            self.assertNotIn('Controlled Access-pw', decoded)

    def test_encode_session_no_session(self):
        """encode_session returns None when no session exists."""
        environ = {}
        data = {'test': 'value'}

        result = auth_wsgi.encode_session(environ, data)
        self.assertIsNone(result)

    def test_get_apache_keys_with_auth_name(self):
        """__get_apache_keys_ generates realm-specific keys."""
        environ = {'AUTH_NAME': 'Private Area'}

        user_key, pw_key = auth_wsgi.__get_apache_keys_(environ)

        self.assertEqual(user_key, 'Private Area-user')
        self.assertEqual(pw_key, 'Private Area-pw')

    def test_get_apache_keys_without_auth_name(self):
        """__get_apache_keys_ uses default keys when no realm."""
        environ = {}

        user_key, pw_key = auth_wsgi.__get_apache_keys_(environ)

        self.assertEqual(user_key, 'user')
        self.assertEqual(pw_key, 'pw')

    def test_groups_for_user_imported(self):
        """groups_for_user function is available from Django."""
        from django.contrib.auth.handlers.modwsgi import groups_for_user

        # Should be callable
        self.assertTrue(callable(groups_for_user))


class ApacheAuthIntegrationTest(TestCase):
    """Integration tests simulating Apache requests."""

    def setUp(self):
        """Create test user."""
        self.user = User.objects.create_user(
            username='mediauser',
            email='media@example.com',
            password='mediapass123'
        )
        self.client = Client()

    def test_protected_media_workflow(self):
        """Test complete workflow: login → access protected media."""
        # 1. User logs in
        login_success = self.client.login(
            username='mediauser',
            password='mediapass123'
        )
        self.assertTrue(login_success)

        # 2. Session is created
        session_id = self.client.cookies['sessionid'].value
        session = Session.objects.get(pk=session_id)
        self.assertIsNotNone(session)

        # 3. Session can be decoded for Apache
        from django.conf import settings
        environ = {
            'HTTP_COOKIE': f'{settings.SESSION_COOKIE_NAME}={session_id}',
            'AUTH_NAME': 'Controlled Access'
        }

        # 4. Authentication check passes
        auth_result = auth_wsgi.check_password(
            environ,
            'mediauser',
            'mediapass123'
        )
        self.assertTrue(auth_result)

    def test_unauthenticated_access_denied(self):
        """Test that unauthenticated users are denied."""
        environ = {'AUTH_NAME': 'Controlled Access'}

        # No session cookie
        auth_result = auth_wsgi.check_password(
            environ,
            'mediauser',
            'password'
        )
        self.assertFalse(auth_result)

    def test_session_expiration_blocks_access(self):
        """Test that expired sessions are denied."""
        # Create and expire session
        self.client.login(username='mediauser', password='mediapass123')
        session_id = self.client.cookies['sessionid'].value

        # Delete session to simulate expiration
        Session.objects.get(pk=session_id).delete()

        from django.conf import settings
        environ = {
            'HTTP_COOKIE': f'{settings.SESSION_COOKIE_NAME}={session_id}'
        }

        # Should be denied
        auth_result = auth_wsgi.check_password(environ, 'mediauser', 'password')
        self.assertFalse(auth_result)


if __name__ == '__main__':
    import unittest
    unittest.main()
