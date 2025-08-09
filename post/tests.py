# tests.py
from django.contrib.auth.models import User
from rest_framework.test import APITestCase

from .models import Like, Post, SubPost


class BlogTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test', password='test')
        self.client.force_authenticate(user=self.user)

    def test_bulk_create(self):
        """Массовое создание постов"""
        data = [
            {'title': 'Post 1', 'body': 'Content 1'},
            {'title': 'Post 2', 'body': 'Content 2'}
        ]

        response = self.client.post('/api/posts/', data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Post.objects.count(), 2)

    def test_create_with_subposts(self):
        """Создание поста с под-постами"""
        data = {
            'title': 'Main Post',
            'body': 'Content',
            'subposts': [
                {'title': 'Sub 1', 'body': 'Sub content 1'},
                {'title': 'Sub 2', 'body': 'Sub content 2'}
            ]
        }

        response = self.client.post('/api/posts/', data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(SubPost.objects.count(), 2)

    def test_update_subposts(self):
        """Обновление под-постов"""
        post = Post.objects.create(title='Test', body='Content', author=self.user)
        SubPost.objects.create(title='Old Sub', body='Old content', post=post)

        data = {
            'title': 'Updated Post',
            'body': 'Updated content',
            'subposts': [{'title': 'New Sub', 'body': 'New content'}]
        }

        response = self.client.put(f'/api/posts/{post.id}/', data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(SubPost.objects.count(), 1)
        self.assertEqual(SubPost.objects.first().title, 'New Sub')

    def test_like_toggle(self):
        """Лайки"""
        post = Post.objects.create(title='Test', body='Content', author=self.user)

        # Ставим лайк
        response = self.client.post(f'/api/posts/{post.id}/like/')
        self.assertTrue(response.data['liked'])
        self.assertEqual(Like.objects.count(), 1)

        # Убираем лайк
        response = self.client.post(f'/api/posts/{post.id}/like/')
        self.assertFalse(response.data['liked'])
        self.assertEqual(Like.objects.count(), 0)

    def test_views_count(self):
        """Просмотры"""
        post = Post.objects.create(title='Test', body='Content', author=self.user)

        response = self.client.get(f'/api/posts/{post.id}/view/')
        self.assertEqual(response.data['views_count'], 1)

        response = self.client.get(f'/api/posts/{post.id}/view/')
        self.assertEqual(response.data['views_count'], 2)
