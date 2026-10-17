from django import forms

from .models import ContactMessage


class ContactForm(forms.ModelForm):
    message = forms.CharField(max_length=5000, widget=forms.Textarea(attrs={'rows': 5}))

    # Anti-spam "honeypot": real visitors never see or fill this box,
    # but spam bots usually fill in every box they find.
    website = forms.CharField(
        required=False,
        label='Leave this field empty',
        widget=forms.TextInput(attrs={'tabindex': '-1', 'autocomplete': 'off'}),
    )

    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'phone', 'subject', 'message']

    def clean_website(self):
        if self.cleaned_data.get('website'):
            raise forms.ValidationError('Spam detected.')
        return ''