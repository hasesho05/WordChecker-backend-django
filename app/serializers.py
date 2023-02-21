from .models import *
from rest_framework import serializers


class AccountSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Account
        fields = [
            "id",
            "username",
            "email",
            "cover_image",
            "user_icon",
            "profile",
            "twitter_link",
        ]

    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            if value or value == "":
                setattr(instance, key, value)
        instance.save()
        return instance


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
