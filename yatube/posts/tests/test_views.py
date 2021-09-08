from django.conf import settings
from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User

User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создадим запись в БД
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.authorized_client_creat = Client()
        cls.authorized_client_creat.force_login(cls.user)
        cls.group = Group.objects.create(
            title='Test title',
            slug='test-slug',
            description='Test description'
        )
        cls.post = Post.objects.create(
            text='Текстовый текст',
            author=cls.user,
            group=cls.group,
        )
        cls.guest_client = Client()
        cls.second_user = User.objects.create_user(username='HasNoName')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.second_user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            'posts/create_post.html': reverse('posts:post_create'),
            'posts/post_detail.html': reverse('posts:post_detail',
                                              args=[self.post.id]),
            'posts/group_list.html': reverse('posts:group_list',
                                             args=[self.group.slug]),
            'posts/index.html': reverse('posts:index'),
            'posts/profile.html': reverse('posts:profile',
                                          args=[self.user.username]),
            'posts/update_post.html': reverse('posts:post_edit',
                                              args=[self.post.id]),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client_creat.get(reverse_name
                                                            )
                self.assertTemplateUsed(response, template)

    def test_page_show_correct_context(self):
        urls = {
            reverse('posts:index'),
            reverse('posts:group_list', args=[self.group.slug]),
            reverse('posts:profile', args=[self.user.username])
        }
        for url in urls:
            with self.subTest():
                response = self.authorized_client.get(url)
                post_object = response.context['page_obj'][0]
                post_text = post_object.text
                self.assertEqual(post_text, self.post.text)

    def test_page_show_correct_context_2(self):
        urls = {
            reverse('posts:group_list', args=[self.group.slug])
        }
        for url in urls:
            with self.subTest():
                response = self.authorized_client.get(url)
                group_object = response.context['group']
                group_desc = group_object.description
                self.assertEqual(group_desc, self.group.description)

    def test_page_show_correct_context_3(self):
        urls = {
            reverse('posts:profile', args=[self.user.username])
        }
        for url in urls:
            with self.subTest():
                response = self.authorized_client.get(url)
                user_object = response.context['author']
                user_username = user_object.username
                self.assertEqual(user_username, self.user.username)

    def test_page_show_correct_context_4(self):
        urls = {
            reverse('posts:post_detail', args=[self.post.id]),
            reverse('posts:post_edit', args=[self.post.id])
        }
        for url in urls:
            with self.subTest():
                response = self.authorized_client_creat.get(url)
                post_object = response.context['post']
                post_text = post_object.text
                post_group = post_object.group
                self.assertEqual(post_text, self.post.text)
                self.assertEqual(post_group, self.group)

    def test_create_post_show_correcе_context(self):
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_paginator_correct_context(self):
        responses = [
            reverse('posts:index'),
            reverse('posts:group_list', args=[self.group.slug]),
            reverse('posts:profile', args=[self.user.username])
        ]
        for url in responses:
            with self.subTest():
                response = self.authorized_client.get(url)
                self.assertEqual(len(response.context['page_obj']),
                                 self.post.id, settings.POSTS_PER_PAGE)
