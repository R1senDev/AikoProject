from requests import get
from time     import time


def signify(number: int | float) -> str:
    return f'+{number}' if number > 0 else str(number)


class WeatherProvider:

    def __init__(self, latitude: float, longitude: float) -> None:

        self.api_url = f'https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,rain,showers,snowfall,wind_speed_10m&hourly=temperature_2m&wind_speed_unit=ms'
        self.last_request_ts = 0
        self.min_request_rate = 30
        self._last_return = None

    def current(self) -> dict[str, bool | float]:

        if time() < self.last_request_ts + self.min_request_rate and self._last_return is not None:
            return self._last_return

        weather = get(self.api_url).json()['current']

        self.last_request_ts = time()

        self._last_return = {
            'temperature': weather['temperature_2m'],
            'rain': weather['rain'] > 0,
            'showers': weather['showers'] > 0,
            'snowfall': weather['snowfall'] > 0,
            'wind_speed': weather['wind_speed_10m']
        }

        return self._last_return


if __name__ == '__main__':
    wp = WeatherProvider(52.52, 13.42)
    wp.current()