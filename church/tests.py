import tempfile
from datetime import timedelta
from io import BytesIO

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from PIL import Image

from .models import ChurchInformation, ContactMessage, Event, GalleryImage, Service

PAGE_NAMES = [
    'home', 'about', 'leadership', 'ministries', 'services',
    'events', 'sermons', 'gallery', 'give', 'contact',
]


class PageTests(TestCase):
    """Every public page loads, and the technical pages behave."""

    def test_every_page_loads(self):
        for name in PAGE_NAMES:
            with self.subTest(page=name):
                response = self.client.get(reverse(name))
                self.assertEqual(response.status_code, 200)

    def test_unknown_page_gives_404(self):
        response = self.client.get('/this-page-does-not-exist/')
        self.assertEqual(response.status_code, 404)

    def test_sitemap_lists_pages(self):
        response = self.client.get('/sitemap.xml')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '/about/')

    def test_robots_blocks_the_dashboard(self):
        response = self.client.get('/robots.txt')
        self.assertContains(response, 'Disallow: /dashboard/')

    def test_old_admin_address_is_gone(self):
        self.assertEqual(self.client.get('/admin/').status_code, 404)

    def test_dashboard_needs_login(self):
        response = self.client.get('/dashboard/')
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response['Location'])

    def test_logged_in_user_can_open_dashboard(self):
        get_user_model().objects.create_superuser(
            'boss', 'boss@example.com', 'a-long-test-password-123'
        )
        self.client.login(username='boss', password='a-long-test-password-123')
        self.assertEqual(self.client.get('/dashboard/').status_code, 200)


class ContentTests(TestCase):
    """Content from the database shows up correctly."""

    def test_church_name_comes_from_the_database(self):
        ChurchInformation.objects.create(name='Test Church Name')
        response = self.client.get(reverse('home'))
        self.assertContains(response, 'Test Church Name')

    def test_services_are_in_week_order_starting_sunday(self):
        Service.objects.create(name='Friday Service', day='friday', start_time='18:30')
        Service.objects.create(name='Sunday Service', day='sunday', start_time='09:00')
        Service.objects.create(name='Prayer Altar', day='tuesday', start_time='18:30')
        response = self.client.get(reverse('services'))
        names = [s.name for s in response.context['services']]
        self.assertEqual(names, ['Sunday Service', 'Prayer Altar', 'Friday Service'])

    def test_inactive_service_is_hidden(self):
        Service.objects.create(
            name='Hidden Service', day='monday', start_time='10:00', active=False
        )
        response = self.client.get(reverse('services'))
        self.assertNotContains(response, 'Hidden Service')

    def test_only_upcoming_events_are_shown(self):
        today = timezone.now().date()
        Event.objects.create(title='Old Event Title', date=today - timedelta(days=3))
        Event.objects.create(title='Future Event Title', date=today + timedelta(days=3))
        response = self.client.get(reverse('events'))
        self.assertContains(response, 'Future Event Title')
        self.assertNotContains(response, 'Old Event Title')


class ContactFormTests(TestCase):
    """The contact form saves good messages and rejects bad ones."""

    def good_data(self, **changes):
        data = {'name': 'Grace', 'email': 'grace@example.com', 'message': 'Please pray for us.'}
        data.update(changes)
        return data

    def test_valid_message_is_saved(self):
        response = self.client.post(reverse('contact'), self.good_data())
        self.assertEqual(ContactMessage.objects.count(), 1)
        self.assertContains(response, 'Thank you')

    def test_bad_email_is_rejected(self):
        self.client.post(reverse('contact'), self.good_data(email='not-an-email'))
        self.assertEqual(ContactMessage.objects.count(), 0)

    def test_missing_message_is_rejected(self):
        self.client.post(reverse('contact'), self.good_data(message=''))
        self.assertEqual(ContactMessage.objects.count(), 0)

    def test_spam_honeypot_is_rejected(self):
        self.client.post(reverse('contact'), self.good_data(website='http://spam.example'))
        self.assertEqual(ContactMessage.objects.count(), 0)

    def test_very_long_message_is_rejected(self):
        self.client.post(reverse('contact'), self.good_data(message='x' * 5001))
        self.assertEqual(ContactMessage.objects.count(), 0)


class ImageShrinkTests(TestCase):
    """Uploaded photos are shrunk automatically."""

    def setUp(self):
        # Save test photos in a temporary folder, not in your real media folder
        self.temp_media = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_media.cleanup)
        override = override_settings(MEDIA_ROOT=self.temp_media.name)
        override.enable()
        self.addCleanup(override.disable)

    def make_upload(self, name, size, image_format, mode='RGB', color='purple'):
        buffer = BytesIO()
        Image.new(mode, size, color).save(buffer, format=image_format)
        return SimpleUploadedFile(name, buffer.getvalue())

    def test_big_photo_is_shrunk(self):
        upload = self.make_upload('big.jpg', (3000, 2000), 'JPEG')
        photo = GalleryImage.objects.create(image=upload, title='Big')
        with Image.open(photo.image.path) as saved:
            self.assertLessEqual(max(saved.size), 1600)

    def test_small_photo_is_not_enlarged(self):
        upload = self.make_upload('small.jpg', (400, 300), 'JPEG')
        photo = GalleryImage.objects.create(image=upload, title='Small')
        with Image.open(photo.image.path) as saved:
            self.assertEqual(saved.size, (400, 300))

    def test_png_stays_png(self):
        upload = self.make_upload('logo.png', (100, 100), 'PNG', mode='RGBA', color=(255, 0, 0, 128))
        photo = GalleryImage.objects.create(image=upload, title='Png')
        self.assertTrue(photo.image.name.endswith('.png'))

# ---------------------------------------------------------------------------
# Email notification tests
# ---------------------------------------------------------------------------
from django.core import mail  # noqa: E402


@override_settings(CONTACT_NOTIFY_EMAIL='church@example.com')
class ContactEmailTests(TestCase):
    """A good contact message also emails the church."""

    def test_email_is_sent_with_reply_to(self):
        self.client.post(reverse('contact'), {
            'name': 'Grace', 'email': 'grace@example.com',
            'subject': 'Prayer', 'message': 'Please pray for us.',
        })
        self.assertEqual(len(mail.outbox), 1)
        sent = mail.outbox[0]
        self.assertEqual(sent.to, ['church@example.com'])
        self.assertEqual(sent.reply_to, ['grace@example.com'])
        self.assertIn('Please pray for us.', sent.body)

    def test_spam_sends_no_email(self):
        self.client.post(reverse('contact'), {
            'name': 'Bot', 'email': 'bot@example.com',
            'message': 'Buy now', 'website': 'http://spam.example',
        })
        self.assertEqual(len(mail.outbox), 0)

    @override_settings(CONTACT_NOTIFY_EMAIL='')
    def test_no_email_when_no_address_is_set(self):
        self.client.post(reverse('contact'), {
            'name': 'Grace', 'email': 'grace@example.com', 'message': 'Hello',
        })
        self.assertEqual(len(mail.outbox), 0)
        self.assertEqual(ContactMessage.objects.count(), 1)        