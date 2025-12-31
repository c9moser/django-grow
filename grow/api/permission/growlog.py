
from ..models.growlog import Growlog
from ..enums import PermissionCode, PermissionType
from ..exceptions import NotPermitted


def growlog_is_public(user, growlog: Growlog, *args,
                      on_success: PermissionCode.ALLOW,
                      on_failure: PermissionCode.CONTINUE,
                      **kwargs) -> PermissionCode:
    if growlog.is_public:
        return on_success
    if on_failure == PermissionCode.RAISE_EXCEPTION:
        raise NotPermitted()
    return on_failure


def growlog_user_is_owner(user, growlog: Growlog, *args,
                          on_success: PermissionCode.ALLOW,
                          on_failure: PermissionCode.CONTINUE,
                          **kwargs) -> PermissionCode:
    if user.pk == growlog.grower.pk:
        return on_success
    if on_failure == PermissionCode.RAISE_EXCEPTION:
        raise NotPermitted()
    return on_failure


def growlog_user_is_friend(user, growlog: Growlog, *args,
                           on_success: PermissionCode.ALLOW,
                           on_failure: PermissionCode.CONTINUE) -> PermissionCode:
    if (growlog.permission == PermissionType.FRIENDS_ONLY
            and user.groups.filter(f"user-{growlog.grower.id}-friends")):
        return on_success
    if on_failure == PermissionCode.RAISE_EXCEPTION:
        raise NotPermitted()
    return on_failure


def growlog_user_is_member(user, growlog: Growlog, *args,
                           on_success: PermissionCode.ALLOW,
                           on_failure: PermissionCode.CONTINUE) -> PermissionCode:
    if (growlog.permission == PermissionType.MEMBERS_ONLY and user.is_authenticated):
        return on_success
    if on_failure == PermissionCode.RAISE_EXCEPTION:
        raise NotPermitted()
    return PermissionCode


def growlog_user_is_editor(user, growlog: Growlog, *args,
                           on_success: PermissionCode.ALLOW,
                           on_failure: PermissionCode.RAISE_EXCEPTION) -> PermissionCode:
    if user.groups.filter(f"user-{growlog.grower.id}-growlogeditor"):
        return on_success
    if on_failure == PermissionCode.RAISE_EXCEPTION:
        raise NotPermitted
    return on_failure
