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
            pk='1',
            text='Текстовый текст',
            author=cls.user,
            group=cls.group,
        )
        cls.guest_client = Client()
        cls.user = User.objects.create_user(username='HasNoName')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

    def test_homepage(self):
        # Отправляем запрос через client,
        # созданный в setUp()
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_author(self):
        response = self.guest_client.get('/about/author/')
        self.assertEqual(response.status_code, 200)

    def test_tech(self):
        response = self.guest_client.get('/about/tech/')
        self.assertEqual(response.status_code, 200)

    def test_group_page(self):
        response = self.guest_client.get('/group/test-slug/')
        self.assertEqual(response.status_code, 200)

    def test_profile_page(self):
        response = self.guest_client.get('/profile/HasNoName/')
        self.assertEqual(response.status_code, 200)

    def test_post_detail(self):
        response = self.guest_client.get('/posts/1/')
        self.assertEqual(response.status_code, 200)

    def test_usexisting_page(self):
        response = self.guest_client.get('/usexisting_page/')
        self.assertEqual(response.status_code, 404)

    def test_create_page(self):
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, 200)

    def test_edit_post_page(self):
        response = self.authorized_client.get(reverse('posts:post_edit',
                                                      args=[self.post.id]))
        self.assertEqual(response.status_code, 302)

    def test_edit_post_page_redirect_anonymous_on_login(self):
        response = self.guest_client.get('/posts/1/edit/', follow=True)
        self.assertRedirects(
            response, ('/auth/login/?next=/posts/1/edit/'))

    def test_urls_correct_temlate(self):
        templates_url_names = {
            '/create/': 'posts/create_post.html',
            f'/posts/{self.post.id}/': 'posts/update_post.html',
            '/group/test-slug/': 'posts/group_list.html',
            '/': 'posts/index.html',
            '/posts/1/': 'posts/post_detail.html',
            '/profile/HasNoName/': 'posts/profile.html',
        }
        for adress, template in templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                self.assertTemplateUsed(response, template)
