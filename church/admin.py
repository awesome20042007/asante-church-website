from django.contrib import admin
from django.utils.html import format_html
from .models import (
    ChurchInformation, SocialLink, Leadership, Ministry,
    Service, Event, Sermon, GalleryImage, ContactMessage
)

# Register your models here.


@admin.register(ChurchInformation)
class ChurchInformationAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'email')
    # Only one row should ever exist — block adding a second.
    def has_add_permission(self, request):
        return not ChurchInformation.objects.exists()


@admin.register(SocialLink)
class SocialLinkAdmin(admin.ModelAdmin):
    list_display = ('platform', 'url', 'active', 'display_order')
    list_filter = ('platform', 'active')
    ordering = ('display_order',)


@admin.register(Leadership)
class LeadershipAdmin(admin.ModelAdmin):
    list_display = ('name', 'position', 'active', 'display_order', 'photo_preview')
    list_filter = ('active',)
    search_fields = ('name', 'position')
    ordering = ('display_order',)

    def photo_preview(self, obj):
        if obj.photo:
            return format_html('<img src="{}" style="height:40px;border-radius:50%;" />', obj.photo.url)
        return "—"
    photo_preview.short_description = "Photo"


@admin.register(Ministry)
class MinistryAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact', 'active', 'display_order')
    list_filter = ('active',)
    search_fields = ('name',)
    ordering = ('display_order',)


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'day', 'start_time', 'end_time', 'location', 'active')
    list_filter = ('day', 'active')
    ordering = ('day', 'start_time')


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'location', 'active')
    list_filter = ('active', 'date')
    search_fields = ('title', 'description')
    ordering = ('date',)
    date_hierarchy = 'date'


@admin.register(Sermon)
class SermonAdmin(admin.ModelAdmin):
    list_display = ('title', 'speaker', 'date', 'thumbnail_preview')
    search_fields = ('title', 'speaker')
    ordering = ('-date',)
    date_hierarchy = 'date'

    def thumbnail_preview(self, obj):
        if obj.thumbnail:
            return format_html('<img src="{}" style="height:40px;" />', obj.thumbnail.url)
        return "—"
    thumbnail_preview.short_description = "Thumbnail"


@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'active', 'display_order', 'image_preview')
    list_filter = ('category', 'active')
    ordering = ('display_order',)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height:40px;" />', obj.image.url)
        return "—"
    image_preview.short_description = "Preview"

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'submitted_at', 'read')
    list_filter = ('read', 'submitted_at')
    search_fields = ('name', 'email', 'message')
    readonly_fields = ('submitted_at',)    