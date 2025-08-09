from django.db import models, transaction
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from .models import Like, Post, SubPost
from .serializers import PostSerializer, SubPostSerializer


class PostView(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        if isinstance(request.data, list):
            posts = [Post(title=item['title'], body=item['body'], author=request.user)
                     for item in request.data]
            created_posts = Post.objects.bulk_create(posts)
            serializer = self.get_serializer(created_posts, many=True)
            return Response(serializer.data, status=201)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        post = serializer.save(author=request.user)
        return Response(self.get_serializer(post).data, status=201)

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def like(self, request, pk=None):
        post = self.get_object()
        like, created = Like.objects.get_or_create(post=post, user=request.user)

        if created:
            return Response({"liked": True, "likes_count": post.likes.count()})
        else:
            like.delete()
            return Response({"liked": False, "likes_count": post.likes.count()})

    @action(detail=True, methods=['get'])
    def view(self, request, pk=None):
        post = self.get_object()
        Post.objects.filter(pk=post.pk).update(views_count=models.F('views_count') + 1)
        post.refresh_from_db()
        return Response({"views_count": post.views_count})


class SubPostView(viewsets.ModelViewSet):
    queryset = SubPost.objects.all()
    serializer_class = SubPostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
