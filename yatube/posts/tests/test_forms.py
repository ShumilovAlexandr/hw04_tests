import shutil
import tempfile

from django import forms
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
TEXT = 'Текст для нового поста'
IMAGE = 'new_image/jpg'


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
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        self.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': TEXT,
            'group': self.group.id,
            'image': forms.fields.ImageField,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('posts:profile',
                             args=[self.user.username]))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertFalse(
            Post.objects.filter(
                text=form_data['text'],
                group=self.group,
                author=self.user,
                image=form_data['image']
            ).exists()
        )

    def test_edit_post(self):
        form_data = {
            'text': 'Тестовый текст измененный',
            'group': self.group.pk,
            'image': forms.fields.ImageField,
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', args=[self.post.id]),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(response, reverse('posts:post_detail',
                             args=[self.post.id]))
        count = Post.objects.all().count()
        self.assertEqual(count, 1)
        post = response.context['post']
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.group.pk, form_data['group'])

    def test_title_label(self):
        text_label = self.form.fields['text'].label
        self.assertTrue(text_label, 'Введите текст')

    def test_title_label(self):
        group_label = self.form.fields['group'].label
        self.assertTrue(group_label, 'Выберите группу')

    def test_title_help_text(self):
        title_help_text = self.form.fields['text'].help_text
        self.assertTrue(title_help_text, 'Напишите Ваш комментарий')
