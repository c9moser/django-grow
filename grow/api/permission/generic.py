from ..exceptions import NotPermitted
from ..enums import PermissionCode


def user_is_active(user, *args,
                   on_success: PermissionCode = PermissionCode.ALLOW,
                   on_failure: PermissionCode = PermissionCode.RAISE_EXCEPTION,
                   **kwargs) -> PermissionCode:
    if user.is_active:
        return on_success
    if on_failure == PermissionCode.RAISE_EXCEPTION:
        raise NotPermitted()
    return on_failure


def user_is_staff(user, *args,
                  on_success: PermissionCode = PermissionCode.ALLOW,
                  on_failure: PermissionCode = PermissionCode.CONTINUE,
                  **kwargs) -> PermissionCode:
    if user.is_staff:
        return on_success
    if on_failure == PermissionCode.RAISE_EXCEPTION:
        raise NotPermitted()
    return on_failure


def user_is_superuser(user, *args,
                      on_success: PermissionCode = PermissionCode.ALLOW,
                      on_failure: PermissionCode = PermissionCode.CONTINUE,
                      **kwargs) -> PermissionCode:
    if user.is_superuser:
        return on_success
    if on_failure == PermissionCode.RAISE_EXCEPTION:
        raise NotPermitted()
    return on_failure
