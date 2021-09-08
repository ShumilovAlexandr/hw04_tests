from http import HTTPStatus
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User

User = get_user_model()


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
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
        cls.user = User.objects.create_user(username='HasNoName')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

    def test_usexisting_page(self):
        response = self.guest_client.get('/usexisting_page/')
        self.assertEqual(response.status_code, 404)

    def test_edit_post_page_redirect_anonymous_on_login(self):
        response = self.guest_client.get('/posts/1/edit/', follow=True)
        self.assertRedirects(
            response, ('/auth/login/?next=/posts/1/edit/'))

    def test_urls_correct_temlate(self):
        templates_url_names = {
            '/create/': 'posts/create_post.html',
            f'/posts/{self.post.id}/': '/update_post.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            '/': 'posts/index.html',
            '/posts/1/': 'posts/post_detail.html',
            '/profile/HasNoName/': 'posts/profile.html',
        }
        for adress, template in templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                self.assertTemplateUsed(response, template)

    def test_pages_status_codes_for_clients(self):
        status_codes = {
            self.guest_client:
            {
                reverse('posts:index'): HTTPStatus.OK,
                reverse('about:author'): HTTPStatus.OK,
                reverse('about:tech'): HTTPStatus.OK,
                reverse('posts:group_list', args=[self.group.slug]):
                HTTPStatus.OK,
                reverse('posts:profile', args=[self.user.username]):
                HTTPStatus.OK,
                reverse('posts:post_detail', args=[self.post.id]):
                HTTPStatus.OK
            },
                self.authorized_client:
            {
                reverse('posts:post_create'): HTTPStatus.OK,
                reverse('posts:post_edit',
                        args=[self.post.id]): HTTPStatus.FOUND,
            },
        }
        for client, data in status_codes.items():
            for url, ststus_code in data.items():
                with self.subTest():
                    response = client.get(url)
                    self.assertEqual(response.status_code, ststus_code)
