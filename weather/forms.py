from django import forms


class WeatherForm(forms.Form):
    """Форма ввода города."""

    city = forms.CharField(
        label='Город',
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Например: Москва'
        })
    )
