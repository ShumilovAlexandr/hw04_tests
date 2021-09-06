import shutil
import tempfile

from django.conf import settings
from django.test import Client, TestCase
from django.urls import reverse
from posts.forms import PostForm
from posts.models import Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


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
        cls.form = PostForm()
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_create_post(self):
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Текстовый текст',
            'group': self.group.id,
            'author': self.user
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('posts:profile',
                             args=[self.user.username]))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Текстовый текст',
                group=self.group,
                author=self.user
            ).exists()
        )

    def test_title_label(self):
        text_label = self.form.fields['text'].label
        self.assertTrue(text_label, 'Введите текст')

    def test_title_label(self):
        group_label = self.form.fields['group'].label
        self.assertTrue(group_label, 'Выберите группу')

    def test_title_help_text(self):
        title_help_text = self.form.fields['text'].help_text
        self.assertTrue(title_help_text, 'Напишите Ваш комментарий')
