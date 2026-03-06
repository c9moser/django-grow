
from ..enums import PermissionCode
from ..exceptions import NotPermitted


def growlog_user_is_allowed_to_view(user, growlog, permission_mapping=None) -> bool:
    from .growlog import (
        growlog_is_public,
        growlog_user_is_member,
        growlog_user_is_friend,
        growlog_user_is_owner,
        growlog_user_is_editor,
    )

    if permission_mapping is None:
        permission_mapping = (
            (growlog_user_is_owner, {
                'on_success': PermissionCode.ALLOW,
                'on_failure': PermissionCode.CONTINUE
            }),
            (growlog_is_public, {
                'on_success': PermissionCode.ALLOW,
                'on_failure': PermissionCode.CONTINUE
            }),
            (growlog_user_is_member, {
                'on_success': PermissionCode.ALLOW,
                'on_failure': PermissionCode.CONTINUE
            }),
            (growlog_user_is_friend, {
                'on_success': PermissionCode.ALLOW,
                'on_failure': PermissionCode.CONTINUE
            }),
            (growlog_user_is_editor, {
                'on_success': PermissionCode.ALLOW,
                'on_failure': PermissionCode.RESTRICT
            }),
        )
    for perm_func, kwargs in permission_mapping:
        try:
            permission = perm_func(user, growlog, **kwargs)
            if permission == PermissionCode.CONTINUE:
                continue
            elif permission == PermissionCode.ALLOW:
                return True
            elif permission == PermissionCode.RESTRICT:
                return False
        except NotPermitted:
            return False
    return False


def growlog_user_is_allowed_to_edit(user, growlog, permission_mapping=None) -> bool:
    from .growlog import (
        growlog_user_is_owner,
        growlog_user_is_editor,
    )

    if permission_mapping is None:
        permission_mapping = [
            (growlog_user_is_owner, {
                'on_success': PermissionCode.ALLOW,
                'on_failure': PermissionCode.CONTINUE
            }),
            (growlog_user_is_editor, {
                'on_success': PermissionCode.ALLOW,
                'on_failure': PermissionCode.RAISE_EXCEPTION
            }),
        ]
    for perm_func, kwargs in permission_mapping:
        try:
            permission = perm_func(user, growlog, **kwargs)
            if permission == PermissionCode.CONTINUE:
                continue
            elif permission == PermissionCode.ALLOW:
                return True
            elif permission == PermissionCode.RESTRICT:
                return False
        except NotPermitted:
            return False
    return False
