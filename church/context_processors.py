from .models import ChurchInformation, SocialLink


def church_globals(request):
    """
    Makes church_info and social_links available to every template,
    automatically, without each view needing to fetch them manually.
    """
    return {
        'church_info': ChurchInformation.objects.first(),
        'social_links': SocialLink.objects.filter(active=True),
    }