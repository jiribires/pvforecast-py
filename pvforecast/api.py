import urllib.parse
import urllib.request
import json
from dataclasses import dataclass
from typing import List, Optional, Literal
from urllib.error import URLError, HTTPError


@dataclass
class HourlyForecast:
    timestamp: str
    irradiance: int
    """Irradiance in W/m^2."""


@dataclass
class DailyForecast:
    timestamp: str
    total_irradiance: Optional[int]
    """Total irradiance in Wh/m^2."""


@dataclass
class HourlyForecastData:
    forecasts: List[HourlyForecast]


@dataclass
class DailyForecastData:
    forecasts: List[HourlyForecast]


class PVForecast:
    """
    A simple API client for the PVForecast irradiance service.

    Service documentation is available at https://wp2.pvforecast.cz/podpora/.
    """

    BASE_URL = "http://www.pvforecast.cz/api/"

    def __init__(self, key: str):
        self.api_key = key

    def get_hourly_irradiance(
        self,
        lat: float,
        lon: float,
        length: Literal[24, 48, 72] = 24,
        dst=1,
        start="auto",
    ) -> HourlyForecastData:
        """
        Retrieves hourly irradiance forecast for a given location and set of parameters.
        Irradiance is given in W/m^2.

        Args:
            lat (float): Latitude of the location.
            lon (float): Longitude of the location.
            length (int): Length of the forecast (24, 48 or 72 hours for hourly, 1, 2 or 3 days for daily). Default is 24.
            dst (int): Daylight Saving Time option (1 for automatic, 0 for disabled). Default is 1.
            start (str): Forecast start time ('today', 'tomorrow', 'auto'). Default is 'auto'.

        Returns: Forecast data parsed into a ForecastData class.
        """

        # Ensure that the parameters are valid
        if length not in [24, 48, 72]:
            raise ValueError("Invalid length. Should be 24, 48 or 72.")
        if dst not in [0, 1]:
            raise ValueError("Invalid dst. Should be 0 or 1.")
        if start not in ["today", "tomorrow", "auto"]:
            raise ValueError("Invalid start. Should be 'today', 'tomorrow', or 'auto'.")

        params = {
            "key": self.api_key,
            "lat": lat,
            "lon": lon,
            "forecast": "pv",
            "format": "json",
            "type": "hour",
            "number": length,
            "dst": dst,
            "start": start,
        }

        url = self.BASE_URL + "?" + urllib.parse.urlencode(params)

        try:
            with urllib.request.urlopen(url) as response:
                if response.status == 200:
                    data = response.read().decode()
                    return self._parse_json(data, "hour")
                else:
                    raise Exception(f"Failed to fetch data: HTTP {response.status}")
        except HTTPError as e:
            msg = e.read().decode()
            raise Exception(f"Failed get data: {e.reason} - {msg}") from e
        except URLError as e:
            raise Exception(f"Failed to reach server: {e.reason}") from e

    def get_daily_irradiance(
        self,
        lat: float,
        lon: float,
        length: Literal[1, 2, 3] = 1,
        dst=1,
        start="auto",
    ) -> DailyForecastData:
        """
        Retrieves daily irradiance forecast for a given location and set of parameters.
        Irradiance is given in W/m^2.

        Args:
            lat (float): Latitude of the location.
            lon (float): Longitude of the location.
            length (int): Length of the forecast (24, 48 or 72 hours for hourly, 1, 2 or 3 days for daily). Default is 24.
            dst (int): Daylight Saving Time option (1 for automatic, 0 for disabled). Default is 1.
            start (str): Forecast start time ('today', 'tomorrow', 'auto'). Default is 'auto'.

        Returns: Forecast data parsed into a ForecastData class.
        """

        # Ensure that the parameters are valid
        if length not in [1, 2, 3]:
            raise ValueError("Invalid length. Should be 1, 2 or 3.")
        if dst not in [0, 1]:
            raise ValueError("Invalid dst. Should be 0 or 1.")
        if start not in ["today", "tomorrow", "auto"]:
            raise ValueError("Invalid start. Should be 'today', 'tomorrow', or 'auto'.")

        params = {
            "key": self.api_key,
            "lat": lat,
            "lon": lon,
            "forecast": "pv",
            "format": "json",
            "type": "day",
            "number": length,
            "dst": dst,
            "start": start,
        }

        url = self.BASE_URL + "?" + urllib.parse.urlencode(params)

        try:
            with urllib.request.urlopen(url) as response:
                if response.status == 200:
                    data = response.read().decode()
                    return self._parse_json(data, "day")
                else:
                    raise Exception(f"Failed to fetch data: HTTP {response.status}")
        except HTTPError as e:
            msg = e.read().decode()
            raise Exception(f"Failed get data: {e.reason} - {msg}") from e
        except URLError as e:
            raise Exception(f"Failed to reach server: {e.reason}") from e

    def _parse_json(self, data: str, forecast_type: str):
        """
        Parses the JSON response and converts it into the ForecastData structure.

        Args:
            data (str): JSON response data as a string.
            forecast_type (str): 'hour' for hourly forecasts, 'day' for daily forecasts.

        Returns:
            ForecastData or List[DailyForecast]: Parsed forecast data.
        """
        raw_data = json.loads(data)

        if forecast_type == "hour":
            forecasts = [
                HourlyForecast(timestamp=entry[0], irradiance=entry[1])
                for entry in raw_data
            ]
            return HourlyForecastData(forecasts=forecasts)
        elif forecast_type == "day":
            forecasts = [
                DailyForecast(timestamp=entry[0], total_irradiance=entry[1])
                for entry in raw_data
            ]
            return forecasts
        else:
            raise ValueError("Invalid time_type. Should be 'hour' or 'day'.")
