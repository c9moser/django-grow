# -*- coding: utf-8 -*-

import sys
import os

APACHE_AUTH_KEY = u"AUTH_NAME"
APACHE_USER_KEY = u"user"
APACHE_PASS_KEY = u"pw"

sys.path.insert(0, os.path.dirname(__file__))
os.environ['DJANGO_SETTINGS_MODULE'] = 'myapp.settings'

def __get_apache_keys_(environ):
    user_key = APACHE_USER_KEY
    pw_key = APACHE_PASS_KEY
    if APACHE_AUTH_KEY in environ:
        authname = environ[APACHE_AUTH_KEY]
        if authname is not None:
            user_key = authname + u"-" + user_key
            pw_key = authname + u"-" + pw_key

    return (user_key, pw_key)

def __get_session_id_(environ):
    from django.conf import settings
    from django.http import parse_cookie

    if u"HTTP_COOKIE" in environ:
        cookies = parse_cookie(environ[u"HTTP_COOKIE"])
        if settings.SESSION_COOKIE_NAME in cookies:
            return cookies[settings.SESSION_COOKIE_NAME]

def __get_session_(environ):
    from django.contrib.sessions.models import Session

    s = None

    session_id = __get_session_id_(environ)
    if session_id is not None:
        try:
            s = Session.objects.get(pk = session_id)
        except Session.DoesNotExists:
            pass

    return s

def __encode_data_(data):
    from importlib import import_module
    from django.conf import settings

    SessionStore = import_module(settings.SESSION_ENGINE).SessionStore
    s = SessionStore()
    return s.encode(data)

def __decode_data_(data):
    from importlib import import_module
    from django.conf import settings

    SessionStore = import_module(settings.SESSION_ENGINE).SessionStore
    s = SessionStore()
    return s.decode(data)

def check_password(environ, username, password):
    s = __get_session_(environ)
    session_data = s.get_decoded()

    from django.contrib.auth import SESSION_KEY
    if SESSION_KEY in session_data and session_data[SESSION_KEY] is not None:
        from django.contrib.auth import get_user_model
        UserModel = get_user_model()

        try:
            user = UserModel.objects.get(pk = session_data[SESSION_KEY])
            return True
        except UserModel.DoesNotExist:
            pass

    return False

def load_session(environ):
    s = __get_session_(environ)
    if s is not None:
        return s.session_data

def decode_session(environ, data):
    session_data = __decode_data_(data)

    (user_key, pw_key) = __get_apache_keys_(environ)
    if user_key not in session_data:
        from django.contrib.auth import SESSION_KEY
        from django.contrib.auth import get_user_model
        UserModel = get_user_model()

        user = None
        if SESSION_KEY in session_data:
            uid = session_data[SESSION_KEY]
            if uid is not None:
                try:
                    user = UserModel.objects.get(pk = uid)
                except UserModel.DoesNotExist:
                    pass

        if user is not None:
            session_data[user_key] = user.get_username()
            if pw_key not in session_data:
                session_data[pw_key] = u"<fake>"

    return {k.encode(u"utf-8"):v.encode(u"utf-8") for (k,v) in session_data.iteritems() if no$

def encode_session(environ, data):
    (user_key, pw_key) = __get_apache_keys_(environ)
    if user_key in data:
        del data[user_key]
    if pw_key in data:
        del data[pw_key]

    s = __get_session_(environ)
    session_data = __decode_data_(s.session_data)
    for key in data:
        if not key.startswith(u"_"):
            session_data[key] = data[key]

    return __encode_data_(session_data)

def save_session(environ, data):
    s = __get_session_(environ)
    if s is not None:
        s.session_data = data
        s.save()
        return True

    return False