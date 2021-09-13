from http import HTTPStatus
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.core.cache import cache

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

    def setUp(self) -> None:
        cache.clear()

    def test_urls_correct_temlate(self):
        templates_url_names = {
            '/create/': 'posts/create_post.html',
            f'/posts/{self.post.id}/': '/update_post.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            '/': 'posts/index.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
            f'/profile/{self.user.username}/': 'posts/profile.html',
        }
        for adress, template in templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                self.assertTemplateUsed(response, template)

    def test_pages_status_codes_for_clients(self):
        status_codes = {
            self.guest_client:
            {
                '/': HTTPStatus.OK,
                '/about/author/': HTTPStatus.OK,
                '/about/tech/': HTTPStatus.OK,
                f'/group/{self.group.slug}/': HTTPStatus.OK,
                f'/profile/{self.user.username}/': HTTPStatus.OK,
                f'/posts/{self.post.id}/': HTTPStatus.OK,
                '/unexisting_page/': HTTPStatus.NOT_FOUND,
            },
                self.authorized_client:
            {
                '/create/': HTTPStatus.OK,
                f'/posts/{self.post.id}/edit/': HTTPStatus.FOUND,
            },
        }
        for client, data in status_codes.items():
            for url, ststus_code in data.items():
                with self.subTest():
                    response = client.get(url)
                    self.assertEqual(response.status_code, ststus_code)

    def test_redirects(self):
        redirects = {
            self.guest_client:
            {
                f'/posts/{self.post.id}/edit/':
                '/auth/login/?next=/posts/1/edit/',
                '/create/': '/auth/login/?next=/create/',
            },
        }
        for client, redirect in redirects.items():
            for url, redirect_url in redirect.items():
                with self.subTest():
                    response = client.get(url)
                    self.assertRedirects(response, redirect_url)
