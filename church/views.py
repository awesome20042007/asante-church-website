import logging

from django.conf import settings
from django.contrib import messages
from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone

from .forms import ContactForm
from .models import Event, GalleryImage, Leadership, Ministry, Sermon, Service

logger = logging.getLogger(__name__)

# The order days appear in on the website. Sunday first.
# To start the week on Monday instead, move 'sunday' to the end of this list.
WEEK_ORDER = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']


def active_services():
    """Active services in week order, then by start time."""
    services = Service.objects.filter(active=True)
    return sorted(services, key=lambda s: (WEEK_ORDER.index(s.day), s.start_time))


def send_contact_notification(contact_message):
    """Email the church a copy of a new contact-form message.
    A problem here must never stop the visitor's message from being saved."""
    recipient = settings.CONTACT_NOTIFY_EMAIL
    if not recipient:
        return

    subject = f"Website message from {contact_message.name}"
    if contact_message.subject:
        subject += f": {contact_message.subject}"
    subject = " ".join(subject.split())  # one line only; blocks header tricks

    body = (
        f"Name: {contact_message.name}\n"
        f"Email: {contact_message.email}\n"
        f"Phone: {contact_message.phone or '-'}\n"
        f"Subject: {contact_message.subject or '-'}\n\n"
        f"{contact_message.message}\n"
    )

    try:
        EmailMessage(
            subject, body, settings.DEFAULT_FROM_EMAIL, [recipient],
            reply_to=[contact_message.email],
        ).send()
    except Exception:
        logger.exception("Could not send the contact-form email notification.")


def home(request):
    context = {
        'services': active_services(),
        'ministries': Ministry.objects.filter(active=True)[:3],
        'upcoming_events': Event.objects.filter(active=True, date__gte=timezone.now().date())[:3],
        'latest_sermon': Sermon.objects.first(),
        'gallery_images': GalleryImage.objects.filter(active=True)[:6],
    }
    return render(request, 'home.html', context)


def about(request):
    return render(request, 'about.html')


def leadership(request):
    context = {'leaders': Leadership.objects.filter(active=True)}
    return render(request, 'leadership.html', context)


def ministries(request):
    context = {'ministries': Ministry.objects.filter(active=True)}
    return render(request, 'ministries.html', context)


def services(request):
    context = {'services': active_services()}
    return render(request, 'services.html', context)


def events(request):
    today = timezone.now().date()
    context = {
        'upcoming_events': Event.objects.filter(active=True, date__gte=today),
        'past_events': Event.objects.filter(active=True, date__lt=today),
    }
    return render(request, 'events.html', context)


def sermons(request):
    context = {'sermons': Sermon.objects.all()}
    return render(request, 'sermons.html', context)


def gallery(request):
    context = {'images': GalleryImage.objects.filter(active=True)}
    return render(request, 'gallery.html', context)


def give(request):
    return render(request, 'give.html')


def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact_message = form.save()
            send_contact_notification(contact_message)
            messages.success(request, "Thank you — your message has been sent. We'll get back to you soon.")
            form = ContactForm()  # reset the form after success
        else:
            messages.error(request, "Please check the form — something's missing or invalid.")
    else:
        form = ContactForm()

    return render(request, 'contact.html', {'form': form})


def robots_txt(request):
    content = (
        "User-agent: *\n"
        "Disallow: /dashboard/\n"
        f"Sitemap: {request.scheme}://{request.get_host()}/sitemap.xml\n"
    )
    return HttpResponse(content, content_type="text/plain")