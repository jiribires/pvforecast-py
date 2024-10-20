# PVForecast

PVForecast je jednoduchý API klient pro službu [PVForecast](http://www.pvforecast.cz/),
která poskytuje předpovědi slunečního záření.

## Instalace

Pro instalaci závislostí použijte následující příkaz:

```sh
pip3 install -r pvforecast-py
```

## Použití

### Inicializace

Pro inicializaci třídy `PVForecast` použijte váš API klíč:

```python
from pvforecast.api import PVForecast

api_key = "váš_api_klíč"
pv_forecast = PVForecast(api_key)
```

### Získání hodinové předpovědi

Pro získání hodinové předpovědi slunečního záření pro následujících 48 hodin
použijte metodu `get_hourly_irradiance`:

```python
hourly_data = pv_forecast.get_hourly_irradiance(lat=50.0, lon=14.0, length=48)
print(hourly_data)
```

### Získání denní předpovědi

Pro získání denní předpovědi slunečního záření pro následující dva dny
použijte metodu `get_daily_irradiance`:

```python
daily_data = pv_forecast.get_daily_irradiance(lat=50.0, lon=14.0, length=2)
print(daily_data)
```

## Testování

Pro spuštění testů použijte následující příkaz:

```sh
python -m unittest discover -s tests
```

## Licence

Tento projekt je licencován pod MIT licencí. Podrobnosti naleznete v souboru `LICENSE`.
