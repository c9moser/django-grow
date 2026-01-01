from ..exceptions import NotPermitted
from ..enums import PermissionCode

from ..models import Strain, Breeder


def breeder_has_growlogs(user, breeder: Breeder, *args,
                         on_success: PermissionCode.CONTINUE,
                         on_failure: PermissionCode.RAISE_EXCEPTION,
                         **kwargs):

    if breeder.growlog_count == 0:
        return on_success
    if on_failure == PermissionCode.RAISE_EXCEPTION:
        raise NotPermitted()
    return on_failure


def strain_has_growlogs(user, strain: Strain, *args,
                        on_success: PermissionCode.CONTINUE,
                        on_failure: PermissionCode.RAISE_EXCEPTION,
                        **kwargs):

    if strain.growlog_count == 0:
        return on_success
    if on_failure == PermissionCode.RAISE_EXCEPTION:
        raise NotPermitted()
    return on_failure
