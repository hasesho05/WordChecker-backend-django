from .models import *
from rest_framework import serializers


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = "__all__"


class HistorySerializer(serializers.ModelSerializer):
    account = AccountSerializer(read_only=True)

    class Meta:
        model = History
        fields = "__all__"

    def create(self, validated_data):
        return History.objects.create(**validated_data)


class PostSerializer(serializers.ModelSerializer):
    account = AccountSerializer(read_only=True)

    class Meta:
        model = Post
        fields = "__all__"


class LikePostSetializer(serializers.ModelSerializer):
    account = AccountSerializer()
    post = PostSerializer()

    class Meta:
        model = LikePost
        fields = "__all__"


class LikeCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = LikeComment
        fields = "__all__"


class CommentPostSerializer(serializers.ModelSerializer):
    account = AccountSerializer()
    like = LikeCommentSerializer(many=True, read_only=True)

    class Meta:
        model = CommentPost
        fields = ["id", "account", "content", "like", "created_at"]
