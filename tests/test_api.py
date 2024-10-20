import json
import unittest
from unittest.mock import patch, MagicMock
from urllib.error import HTTPError, URLError

from pvforecast.api import PVForecast, HourlyForecastData, HourlyForecast, DailyForecast


class TestPVForecast(unittest.TestCase):
    def setUp(self):
        self.api_key = "test_key"
        self.pv_forecast = PVForecast(self.api_key)

    def test_initialization(self):
        self.assertEqual(self.pv_forecast.api_key, self.api_key)

    def test_invalid_length_for_dayly(self):
        with self.assertRaises(ValueError):
            self.pv_forecast.get_daily_irradiance(50.0, 14.0, length=5)

    def test_invalid_length_for_hourly(self):
        with self.assertRaises(ValueError):
            self.pv_forecast.get_hourly_irradiance(50.0, 14.0, length=12)

    def test_invalid_dst_for_hourly(self):
        with self.assertRaises(ValueError):
            self.pv_forecast.get_hourly_irradiance(50.0, 14.0, dst=2)

    def test_invalid_dst_for_daily(self):
        with self.assertRaises(ValueError):
            self.pv_forecast.get_daily_irradiance(50.0, 14.0, dst=2)

    def test_invalid_start_for_hourly(self):
        with self.assertRaises(ValueError):
            self.pv_forecast.get_hourly_irradiance(50.0, 14.0, start="invalid")

    def test_invalid_start_for_daily(self):
        with self.assertRaises(ValueError):
            self.pv_forecast.get_daily_irradiance(50.0, 14.0, start="invalid")

    @patch("pvforecast.api.urllib.request.urlopen")
    def test_get_irradiance_success(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.read.return_value = json.dumps(
            [["2023-10-01T00:00:00Z", 1000]]
        ).encode()
        mock_urlopen.return_value.__enter__.return_value = mock_response

        result = self.pv_forecast.get_hourly_irradiance(50.0, 14.0)
        self.assertIsInstance(result, HourlyForecastData)
        self.assertEqual(len(result.forecasts), 1)
        self.assertEqual(result.forecasts[0].timestamp, "2023-10-01T00:00:00Z")
        self.assertEqual(result.forecasts[0].irradiance, 1000)

    @patch("pvforecast.api.urllib.request.urlopen")
    def test_get_daily_irradiance_success(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.read.return_value = json.dumps(
            [["2023-10-01T00:00:00Z", 1000]]
        ).encode()
        mock_urlopen.return_value.__enter__.return_value = mock_response

        result = self.pv_forecast.get_daily_irradiance(50.0, 14.0)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].timestamp, "2023-10-01T00:00:00Z")
        self.assertEqual(result[0].total_irradiance, 1000)

    @patch("pvforecast.api.urllib.request.urlopen")
    def test_get_irradiance_http_error(self, mock_urlopen):
        mock_urlopen.side_effect = HTTPError(
            url="http://www.pvforecast.cz/api/",
            code=500,
            msg="Internal Server Error",
            hdrs=None,
            fp=None,
        )

        with self.assertRaises(Exception) as context:
            self.pv_forecast.get_hourly_irradiance(50.0, 14.0)
        self.assertIn("Failed get data", str(context.exception))

    @patch("pvforecast.api.urllib.request.urlopen")
    def test_get_daily_irradiance_http_error(self, mock_urlopen):
        mock_urlopen.side_effect = HTTPError(
            url="http://www.pvforecast.cz/api/",
            code=500,
            msg="Internal Server Error",
            hdrs=None,
            fp=None,
        )

        with self.assertRaises(Exception) as context:
            self.pv_forecast.get_daily_irradiance(50.0, 14.0)
        self.assertIn("Failed get data", str(context.exception))

    @patch("pvforecast.api.urllib.request.urlopen")
    def test_get_irradiance_url_error(self, mock_urlopen):
        mock_urlopen.side_effect = URLError("Server not reachable")

        with self.assertRaises(Exception) as context:
            self.pv_forecast.get_hourly_irradiance(50.0, 14.0)
        self.assertIn("Failed to reach server", str(context.exception))

    @patch("pvforecast.api.urllib.request.urlopen")
    def test_get_daily_irradiance_url_error(self, mock_urlopen):
        mock_urlopen.side_effect = URLError("Server not reachable")

        with self.assertRaises(Exception) as context:
            self.pv_forecast.get_daily_irradiance(50.0, 14.0)
        self.assertIn("Failed to reach server", str(context.exception))
