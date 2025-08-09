# serializers.py
from rest_framework import serializers

from .models import Post, SubPost


class SubPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubPost
        fields = ['id', 'title', 'body', 'post', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class PostSerializer(serializers.ModelSerializer):
    subposts = SubPostSerializer(many=True, required=False)
    likes_count = serializers.SerializerMethodField()
    views_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'title', 'body', 'author', 'views_count', 'likes_count',
                  'subposts', 'created_at', 'updated_at']
        read_only_fields = ['id', 'author', 'views_count', 'created_at', 'updated_at']

    def get_likes_count(self, obj):
        return obj.likes.count()

    def create(self, validated_data):
        subposts_data = validated_data.pop('subposts', [])
        post = Post.objects.create(**validated_data)

        for subpost_data in subposts_data:
            SubPost.objects.create(post=post, **subpost_data)

        return post

    def update(self, instance, validated_data):
        subposts_data = validated_data.pop('subposts', [])

        # Обновляем пост
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Простое управление под-постами: удаляем все старые, создаем новые
        if subposts_data:
            instance.subposts.all().delete()
            for subpost_data in subposts_data:
                SubPost.objects.create(post=instance, **subpost_data)

        return instance
