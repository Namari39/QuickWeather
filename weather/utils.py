import requests
from dataclasses import dataclass
from typing import Optional

import openmeteo_requests
import pandas as pd
import requests_cache
import weather.constants
from retry_requests import retry


@dataclass
class CityInfo:
    name: str
    latitude: float
    longitude: float
    country: str


class WeatherService:
    """Класс определения погоды в городе по названию."""

    def __init__(self):
        """Инициализация параметров."""
        self.base_geocoding_url = (
            "https://geocoding-api.open-meteo.com/v1/search"
        )
        self.base_weather_url = "https://api.open-meteo.com/v1/forecast"
        cache_session = requests_cache.CachedSession(
            '.cache',
            expire_after=weather.constants.CACHE_TIMEOUT
        )
        retry_session = retry(
            cache_session,
            retries=weather.constants.RETRY_SESSION,
            backoff_factor=weather.constants.DELAY_TIME
        )
        self.client = openmeteo_requests.Client(session=retry_session)

    def get_city_coordinates(self, city_name: str) -> Optional[CityInfo]:
        """Запрашивает координаты города через Open-Meteo Geocoding API."""
        params = {
            "name": city_name,
            "count": weather.constants.COUTNT_RESULT,
            "language": "ru",
            "format": "json"
        }
        try:
            response = requests.get(self.base_geocoding_url, params=params)
            response.raise_for_status()
            data = response.json()
            if not data.get("results"):
                return None
            city_data = data["results"][weather.constants.SLICE_RESULT]
            return CityInfo(
                name=city_data["name"],
                latitude=city_data["latitude"],
                longitude=city_data["longitude"],
                country=city_data["country"]
            )
        except Exception as e:
            print(f"Ошибка при геокодинге: {e}")
            return None

    def get_weather(self, latitude, longitude):
        """Запрашивает погоду по параметрам через Open-Meteo Geocoding API"""
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "hourly": "temperature_2m",
            "forecast_days": 1
        }
        response = requests.get(self.base_weather_url, params=params)
        data = response.json()
        df = pd.DataFrame({
            'time': pd.to_datetime(data['hourly']['time']),
            'temperature_2m': data['hourly']['temperature_2m']
        })
        df['formatted_time'] = df['time'].dt.strftime('%H:%M')
        return df[['formatted_time', 'temperature_2m']].head(
            weather.constants.TIME_LIMIT
        )

    def get_weather_by_city(self, city_name: str):
        """Возвращает погоду для города по его названию."""
        city = self.get_city_coordinates(city_name)
        if not city:
            raise ValueError(f"Город '{city_name}' не найден")
        print(f"Найден город: {city.name}, {city.country}")
        return self.get_weather(city.latitude, city.longitude)
