import os
from io import BytesIO

from django.core.files.base import ContentFile
from django.db import models
from PIL import Image, ImageOps


def shrink_image(image_field, max_size=1600, quality=82):
    """Shrink a newly uploaded photo so pages load fast.
    Phone photos can be 5 MB or more; this makes them a few hundred KB.
    It only runs when a NEW file is uploaded, never on normal edits."""
    if not image_field or image_field._committed:
        return

    img = Image.open(image_field)
    original_format = (img.format or '').upper()
    if original_format not in ('JPEG', 'PNG', 'WEBP'):
        return  # leave unusual formats alone

    img = ImageOps.exif_transpose(img)    # fix photos that come out sideways
    img.thumbnail((max_size, max_size))   # only shrinks, keeps proportions

    buffer = BytesIO()
    name = image_field.name
    if original_format == 'PNG':
        img.save(buffer, format='PNG', optimize=True)
    else:
        if img.mode != 'RGB':
            img = img.convert('RGB')
        img.save(buffer, format='JPEG', quality=quality, optimize=True)
        name = os.path.splitext(name)[0] + '.jpg'

    image_field.save(name, ContentFile(buffer.getvalue()), save=False)


class OptimizedImagesMixin:
    """Add this to a model and list its image fields in optimized_image_fields.
    Those images are shrunk automatically every time a new one is uploaded."""
    optimized_image_fields = []

    def save(self, *args, **kwargs):
        for field_name in self.optimized_image_fields:
            shrink_image(getattr(self, field_name))
        super().save(*args, **kwargs)


class ChurchInformation(models.Model):
    """
    Holds the church's core identity — name, description, contact details.
    This is a 'singleton' model: we only ever expect ONE row to exist,
    since there's only one church. The admin will show it as one editable record.
    """
    name = models.CharField(max_length=255, default="Asante Church International")
    short_description = models.TextField(blank=True)
    about = models.TextField(blank=True)
    mission = models.TextField(blank=True)
    vision = models.TextField(blank=True)
    motto = models.CharField(max_length=255, blank=True)
    bible_verse = models.CharField(max_length=100, blank=True)
    history = models.TextField(blank=True)
    core_values = models.TextField(blank=True, help_text="One value per line, format: Title — Description")
    statement_of_faith = models.TextField(blank=True, help_text="Full statement of faith text")
    giving_instructions = models.TextField(blank=True, help_text="e.g. mobile money code, bank details")
    address = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=50, blank=True)
    whatsapp = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    maps_url = models.URLField(blank=True)
    logo = models.ImageField(upload_to='church/', blank=True, null=True)
    favicon = models.ImageField(upload_to='church/', blank=True, null=True)

    def __str__(self):
        return self.name


class SocialLink(models.Model):
    """One row per social media account (Facebook, Instagram, etc.)."""
    PLATFORM_CHOICES = [
        ('facebook', 'Facebook'),
        ('instagram', 'Instagram'),
        ('youtube', 'YouTube'),
        ('tiktok', 'TikTok'),
        ('whatsapp', 'WhatsApp'),
        ('x', 'X'),
        ('other', 'Other'),
    ]
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    url = models.URLField()
    active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['display_order']

    def __str__(self):
        return self.get_platform_display()


class Leadership(OptimizedImagesMixin, models.Model):
    """One row per leader shown on the Leadership page."""
    optimized_image_fields = ['photo']
    name = models.CharField(max_length=255)
    position = models.CharField(max_length=255)
    biography = models.TextField(blank=True)
    photo = models.ImageField(upload_to='leadership/', blank=True, null=True)
    display_order = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ['display_order']
        verbose_name_plural = "Leadership"

    def __str__(self):
        return f"{self.name} — {self.position}"


class Ministry(OptimizedImagesMixin, models.Model):
    """One row per ministry (youth, women, choir, etc.)."""
    optimized_image_fields = ['image']
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='ministries/', blank=True, null=True)
    contact = models.CharField(max_length=255, blank=True)
    display_order = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ['display_order']
        verbose_name_plural = "Ministries"

    def __str__(self):
        return self.name


class Service(models.Model):
    """One row per recurring service (Sunday service, midweek prayer, etc.)."""
    DAY_CHOICES = [
        ('monday', 'Monday'), ('tuesday', 'Tuesday'), ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'), ('friday', 'Friday'), ('saturday', 'Saturday'),
        ('sunday', 'Sunday'),
    ]
    name = models.CharField(max_length=255)
    day = models.CharField(max_length=20, choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ['day', 'start_time']

    def __str__(self):
        return f"{self.name} ({self.get_day_display()})"


class Event(OptimizedImagesMixin, models.Model):
    """One row per upcoming or past event."""
    optimized_image_fields = ['image']
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    date = models.DateField()
    start_time = models.TimeField(blank=True, null=True)
    end_time = models.TimeField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True)
    image = models.ImageField(upload_to='events/', blank=True, null=True)
    registration_url = models.URLField(blank=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ['date']

    def __str__(self):
        return f"{self.title} — {self.date}"


class Sermon(OptimizedImagesMixin, models.Model):
    """One row per sermon/media item."""
    optimized_image_fields = ['thumbnail']
    title = models.CharField(max_length=255)
    speaker = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    date = models.DateField()
    thumbnail = models.ImageField(upload_to='sermons/', blank=True, null=True)
    youtube_url = models.URLField(blank=True)
    video_url = models.URLField(blank=True)
    audio_url = models.URLField(blank=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return self.title


class GalleryImage(OptimizedImagesMixin, models.Model):
    """One row per photo in the gallery."""
    optimized_image_fields = ['image']
    image = models.ImageField(upload_to='gallery/')
    title = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=100, blank=True)
    display_order = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ['display_order']

    def __str__(self):
        return self.title or f"Gallery Image #{self.pk}"


class ContactMessage(models.Model):
    """One row per message submitted through the contact form."""
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=50, blank=True)
    subject = models.CharField(max_length=255, blank=True)
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-submitted_at']

    def __str__(self):
        return f"{self.name} — {self.submitted_at:%Y-%m-%d}"