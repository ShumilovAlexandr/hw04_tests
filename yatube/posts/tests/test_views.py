import datetime as dt

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
                                             args=['test-slug']),
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

    def test_home_page_show_correct_context(self):
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        task_text_0 = first_object.text
        task_pub_date_0 = first_object.pub_date.date()
        task_group_0 = first_object.group
        task_author_0 = first_object.author
        self.assertEqual(task_text_0, 'Текстовый текст')
        self.assertEqual(task_pub_date_0, dt.date.today())
        self.assertEqual(task_group_0, self.group)
        self.assertEqual(task_author_0, self.user)

    def test_group_list_page_show_correct_context(self):
        response = self.authorized_client.get(reverse('posts:group_list',
                                              args=['test-slug']))
        post_object = response.context['page_obj'][0]
        group_object = response.context['group']
        post_text = post_object.text
        post_author = post_object.author
        post_date = post_object.pub_date.date()
        group_desc = group_object.description
        group_title = group_object.title
        self.assertEqual(post_text, self.post.text)
        self.assertEqual(post_date, dt.date.today())
        self.assertEqual(group_desc, self.group.description)
        self.assertEqual(post_author, self.user)
        self.assertEqual(group_title, self.group.title)

    def test_profile_show_correct_context(self):
        response = self.authorized_client.get(reverse('posts:profile',
                                              args=[self.user.username]))
        post_object = response.context['page_obj'][0]
        user_object = response.context['author']
        post_text = post_object.text
        post_group = post_object.group
        user_username = user_object.username
        self.assertEqual(post_text, self.post.text)
        self.assertEqual(post_group, self.group)
        self.assertEqual(user_username, self.user.username)

    def test_post_detail_show_correct_context(self):
        response = self.authorized_client.get(reverse('posts:post_detail',
                                              args=[self.post.id]))
        post_object = response.context['post']
        post_text = post_object.text
        post_group = post_object.group
        self.assertEqual(post_text, self.post.text)
        self.assertEqual(post_group, self.group)

    def test_post_edit_show_correcе_context(self):
        response = self.authorized_client_creat.get(reverse('posts:post_edit',
                                                    args=[self.post.id]))
        print(response)
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

    def test_paginator_index_page(self):
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), self.post.id, 10)

    def test_paginator_group_list_page(self):
        response = self.authorized_client.get(reverse('posts:group_list',
                                              args=['test-slug']))
        self.assertEqual(len(response.context['page_obj']), self.post.id, 10)

    def test_profile_page(self):
        response = self.authorized_client.get(reverse('posts:profile',
                                              args=[self.user.username]))
        self.assertEqual(len(response.context['page_obj']), self.post.id, 10)
