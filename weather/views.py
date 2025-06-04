from django.shortcuts import redirect, render
from requests_cache import datetime

from weather.forms import WeatherForm
from weather.utils import WeatherService


def weather_view(request):
    """Основная функция отображения погоды."""
    init_search_history(request)
    form, city_name = get_form_and_city(request)
    weather_data, error = process_weather_request(
        request, city_name
    ) if city_name else (None, None)
    return render(request, 'weather/weather.html', {
        'form': form or WeatherForm(),
        'weather_data': weather_data,
        'error': error,
        'history': request.session.get('search_history', [])
    })


def init_search_history(request):
    """Инициализирует историю поиска в сессии."""
    if 'search_history' not in request.session:
        request.session['search_history'] = []


def get_form_and_city(request):
    """Извлекает форму и название города из запроса."""
    if request.method == 'POST':
        form = WeatherForm(request.POST)
    elif 'city' in request.GET:
        form = WeatherForm(request.GET)
    else:
        return None, None
    return form, form.cleaned_data['city'] if form.is_valid() else None


def process_weather_request(request, city_name):
    """Обрабатывает запрос погоды и обновляет историю."""
    try:
        service = WeatherService()
        weather_data = service.get_weather_by_city(
            city_name
        ).to_dict('records')
        update_search_history(request, city_name)
        return weather_data, None
    except Exception as e:
        return None, str(e)


def update_search_history(request, city_name):
    """Обновляет историю поиска в сессии."""
    history = request.session['search_history']
    if not any(city_name.lower() == h['city'].lower() for h in history):
        history.insert(0, {
            'city': city_name,
            'date': datetime.now().strftime("%d.%m.%Y %H:%M")
        })
        request.session['search_history'] = history[:10]
        request.session.modified = True


def clear_history(request):
    """Очищаяет историю поиска в сессии."""
    if 'search_history' in request.session:
        del request.session['search_history']
    return redirect('weather')
