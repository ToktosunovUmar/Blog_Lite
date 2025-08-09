from rest_framework import serializers

from .models import Post, SubPost


class SubPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubPost
        fields = ['id', 'title', 'body', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class PostSerializer(serializers.ModelSerializer):
    subposts = SubPostSerializer(many=True, required=False)
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())
    likes_count = serializers.SerializerMethodField()
    class Meta:
        model = Post
        fields = ['id', 'title', 'body', 'author', 'views_count',
                  'likes_count', 'subposts', 'created_at', 'updated_at']
        read_only_fields = ['views_count', 'likes_count', 'created_at', 'updated_at']

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

        instance.title = validated_data.get('title', instance.title)
        instance.body = validated_data.get('body', instance.body)
        instance.save()

        existing_subposts = list(instance.subposts.all())
        updated_subposts_map = {item.get('id'):
                                    item for item in subposts_data if 'id' in item}

        for subpost in existing_subposts:
            if subpost.id not in updated_subposts_map:
                subpost.delete()

        for subpost_data in subposts_data:
            subpost_id = subpost_data.get('id')
            if subpost_id:
                SubPost.objects.filter(id=subpost_id,
                                       post=instance).update(**subpost_data)
            else:
                SubPost.objects.create(post=instance, **subpost_data)

        return instance
