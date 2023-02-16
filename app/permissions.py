from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied
from .decorators import get_account, getAccount


# No one can access including superuser
class PermitDenied(permissions.BasePermission):
    def has_permission(self, request, view):
        return False


class PermitIsAuthenticated(permissions.BasePermission):
    @get_account
    def has_permission(self, request, view):
        if request.is_authenticated:
            return True
        else:
            return False


class PermitOnlyOwner(permissions.BasePermission):
    @get_account
    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):
        try:
            if request.account == obj.account:
                return True
            else:
                return False
        except:
            return False


class PermitIsAuthenticatedOrReadOnly(permissions.BasePermission):
    @get_account
    def has_permission(self, request, view):
        if request.is_authenticated or request.method in permissions.SAFE_METHODS:
            return True
        else:
            return False


# ************************ #
# function based permissions
# ************************ #
def _permit_denied(request=None):
    raise PermissionDenied(detail=None, code=None)


def _permit_is_authenticated(request):
    getAccount(request)

    if not request.is_authenticated:
        raise PermissionDenied(detail=None, code=None)


def _permit_only_owner(request, instance=None):
    getAccount(request)

    if not instance:
        if request.method == 'GET':
            object_account_id = request.GET.get('account_id')
        else:
            object_account_id = request.data.get('account_id')

        try:
            if object_account_id and object_account_id:
                object_account_id = int(object_account_id)
        except:
            pass
    else:
        object_account_id = instance.account.id

    if not request.is_authenticated or request.account.id != object_account_id:
        raise PermissionDenied(detail=None, code=None)


def _permit_only_owner_for_list(request, queryset):
    getAccount(request)

    if request.method == 'GET':
        ids = request.GET.get('ids')
    else:
        ids = request.data.get('ids')

    for id in ids:
        obj = queryset.filter(id=id, account=request.account).first()
        if not obj:
            raise PermissionDenied(detail=None, code=None)


def _permit_require_params(request, params):
    getAccount(request)

    keys = list(request.GET.keys()) + list(request.data.keys())

    for param in params:
        if param not in keys:
            raise PermissionDenied(detail=None, code=None)


# ************************ #
# decorator based permissions
# ************************ #
def permit_denied(func):
    def wrapper(obj, request, *args, **kwargs):
        _permit_denied(request)
        return func(obj, request, *args, **kwargs)

    return wrapper


def permit_is_authenticated(func):
    def wrapper(obj, request, *args, **kwargs):
        _permit_is_authenticated(request)
        return func(obj, request, *args, **kwargs)

    return wrapper


def permit_only_owner(func):
    def wrapper(obj, request, *args, **kwargs):
        _permit_only_owner(request)
        return func(obj, request, *args, **kwargs)

    return wrapper
