from django.views import View
from rest_framework import viewsets
from rest_framework import permissions
from django.db.models import Q
from .serializers import *
from .models import *
from . import utils
from django.conf import settings

from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
import hashlib

from .permissions import *
from .permissions import _permit_denied, _permit_only_owner, _permit_require_params, _permit_only_owner_for_list
from .validations import *
from .decorators import get_account, getAccount
from .jwt_token import jwt_encode, jwt_decode

from gmail_api import sendmail


class StandardPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 1000


class AuthenticateView(utils.DisabledCRUDMixin):
    queryset = Account.objects.all().order_by("-created_at")
    serializer_class = AccountSerializer

    @action(detail=False, methods=["post"])
    def authenticated(self, request, *args, **kwargs):
        print("a")
        print(request)
        getAccount(request)
        if request.is_authenticated:
            serializer = self.get_serializer(request.account)
            return Response({"status": "success", "data": serializer.data})
        else:
            return Response({"status": "failed", "message": "token is not provided."})

    @action(detail=False, methods=["post"])
    def login(self, request, *args, **kwargs):
        login_query = request.data.get("login_query")
        if not login_query:
            login_query = request.data.get("email")
        encrypted_password = hashlib.sha256(request.data["password"].encode()).hexdigest()

        account = Account.objects.filter(Q(email=login_query)).first()
        if account and account.encrypted_password == encrypted_password:
            serializer = self.get_serializer(account)
            token = jwt_encode(serializer.data)
            return Response({"status": "success", "data": {"token": token}})
        else:
            return Response({"status": "failed", "data": {}})

    @action(detail=False, methods=["post"])
    def signup(self, request, *args, **kwargs):
        self.validate_signup(request)
        email = request.data.get("email")
        encrypted_password = hashlib.sha256(request.data.get("password").encode()).hexdigest()
        username = request.data.get("username")
        Account.objects.create(username=username, email=email, encrypted_password=encrypted_password)

        return self.login(request, *args, **kwargs)

    @action(detail=False, methods=["post"])
    def change_password(self, request, *args, **kwargs):
        getAccount(request)
        success = False
        if request.is_authenticated:
            current_password = request.data.get("current_password")
            new_password = request.data.get("new_password")
            encrypted_current_password = hashlib.sha256(current_password.encode()).hexdigest()
            encrypted_new_password = hashlib.sha256(new_password.encode()).hexdigest()

            if request.account.encrypted_password == encrypted_current_password:
                request.account.encrypted_password = encrypted_new_password
                request.account.save()
                success = True

        if success:
            return Response({"status": "success"})
        else:
            return Response({"status": "failed"})

    @action(detail=False, methods=["post"])
    def change_email(self, request, *args, **kwargs):
        getAccount(request)
        email = request.data.get("email")
        if Account.objects.filter(email=email).count() != 0:
            raise ValidationError({"code": "email_already_exists", "message": "Email already exists."})

        success = False
        if request.is_authenticated:
            request.account.email = email
            request.account.email_verified = False
            request.account.save()
            success = True

        if success:
            return Response({"status": "success"})
        else:
            return Response({"status": "failed"})

    def validate_signup(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        validate_account_duplication(email)
        validate_password(password)


class AccountViewSet(utils.ModelViewSet):
    queryset = Account.objects.all().order_by("-created_at")
    serializer_class = AccountSerializer
    permission_classes = []
    removed_methods = ["partial_update", "destroy"]

    @permit_denied
    def list(self, request, *args, **kwargs):
        _permit_require_params(request, params=["account_id"])

        queryset = self.get_queryset()
        queryset = self.queryset_filter(queryset, request.GET)
        serializer = self.get_serializer(queryset, many=True)
        return Response({"status": "success", "data": serializer.data})

    @permit_denied
    def create(self, request, *args, **kwargs):
        encrypted_password = hashlib.sha256(request.data["password"].encode()).hexdigest()
        account = Account.objects.create(
            username=request.data["username"], email=request.data["email"], encrypted_password=encrypted_password
        )
        serializer = self.get_serializer(account)
        return Response({"status": "success", "data": serializer.data})

    @get_account
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.is_authenticated and request.account.id == instance.id:
            serializer = AccountSerializer(instance, context={"request": request})
        else:
            serializer = self.get_serializer(instance)
        return Response({"status": "success", "data": serializer.data})

    @get_account
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()

        if request.is_authenticated and request.account.id == instance.id:
            serializer = AccountSerializer(instance, data=request.data, partial=partial, context={"request": request})
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response({"status": "success", "data": serializer.data})
        else:
            _permit_denied()
            # serializer = self.get_serializer(instance, data=request.data, partial=partial)


class HistoryViewSet(utils.ModelViewSet):
    queryset = History.objects.all().order_by("-created_at")
    serializer_class = HistorySerializer
    pagination_class = StandardPagination

    def get_queryset(self):
        queryset = self.queryset
        queryset = self.queryset_filter(queryset, self.request.GET)
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset().filter(id=request.GET["account_id"])
        if self.pagination_class:
            queryset = self.pagination_class().paginate_queryset(queryset, request)
        serializer = self.get_serializer(queryset, many=True)
        return Response({"status": "success", "data": serializer.data})

    def create(self, request, *args, **kwargs):
        _permit_only_owner(request)
        account = Account.objects.filter(id=request.data["account_id"])
        if account.count() == 0:
            raise ValidationError({"code": "account_not_found", "message": "Account not found."})
        account = account.first()
        history = History.objects.create(
            account=account,
            word=request.data["word"],
        )
        serializer = self.get_serializer(history)
        return Response({"status": "success", "data": serializer.data})

    # remove history
    @action(detail=False, methods=["post"])
    def remove(self, request, *args, **kwargs):
        _permit_only_owner(request)
        account = Account.objects.filter(id=request.data["account_id"])
        if account.count() == 0:
            raise ValidationError({"code": "account_not_found", "message": "Account not found."})
        account = account.first()
        history = History.objects.filter(account=account, word=request.data["word"])
        if history.count() == 0:
            raise ValidationError({"code": "history_not_found", "message": "History not found."})
        history = history.first()
        history.delete()
        return Response({"status": "success"})


class PostViewSet(utils.ModelViewSet):
    queryset = Post.objects.all().order_by("-created_at")
    serializer_class = PostSerializer
    pagination_class = StandardPagination

    def get_queryset(self):
        queryset = self.queryset
        queryset = self.queryset_filter(queryset, self.request.GET)
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset().filter(id=request.GET["account_id"])
        if self.pagination_class:
            queryset = self.pagination_class().paginate_queryset(queryset, request)
        serializer = self.get_serializer(queryset, many=True)
        return Response({"status": "success", "data": serializer.data})

    def create(self, request, *args, **kwargs):
        _permit_only_owner(request)
        print(request.data)
        account = Account.objects.filter(id=request.data["account_id"]).first()
        post = Post.objects.create(
            account=account,
            content=request.data["content"],
            image=request.data["image"],
        )

        serializer = self.get_serializer(post)
        return Response({"status": "success", "data": serializer.data})

    @action(detail=False, methods=["post"])
    def add_like(self, request, *args, **kwargs):
        # _permit_only_owner(request)
        account = Account.objects.filter(encrypted_password=request.data["token"]).first()
        if account is None:
            return Response({"status": "ng", "message": "Account not found"})
        post = Post.objects.filter(id=request.data["post_id"]).first()
        if post is None:
            return Response({"status": "ng", "message": "Post not found"})

        like = LikePost.objects.create(
            liked_by=account,
            like_post=post,
        )
        serializer = LikePostSetializer(like)
        return Response({"status": "success", "data": serializer.data})

    @action(detail=False, methods=["post"])
    def remove_like(self, request, *args, **kwargs):
        account = Account.objects.filter(encrypted_password=request.data["token"]).first()
        if account is None:
            return Response({"status": "ng", "message": "Account not found"})
        post = Post.objects.filter(id=request.data["post_id"]).first()
        if post is None:
            return Response({"status": "ng", "message": "Post not found"})

        objs = LikePost.objects.filter(
            liked_by=account,
            like_post=post,
        )
        for item in objs:
            item.delete()
        return Response({"status": "success"})


class LikePostViewSet(utils.ModelViewSet):
    queryset = LikePost.objects.all().order_by("-created_at")
    serializer_class = LikePostSetializer
    # removed_methods = ["retrieve", "update", "partial_update", "destroy"]

    def create(self, request, *args, **kwargs):
        account = Account.objects.filter(id=request.data["account_id"]).first()
        like = LikePost.objects.create(
            post_id=request.data["post_id"],
            account=account,
        )

        serializer = self.get_serializer(like)
        return Response({"status": "success", "data": serializer.data})

    @action(detail=False, methods=["post"])
    def remove(self, request, *args, **kwargs):
        account = Account.objects.filter(id=request.data["account_id"]).first()
        likes = LikePost.objects.filter(
            post_id=request.data["post_id"],
            account=account,
        )

        for like in likes:
            like.delete()
        return Response({"status": "success"})
