import requests

meteo_url = "https://archive-api.open-meteo.com/v1/archive?latitude=52.52&longitude=13.41&start_date=2025-01-01&end_date=2025-01-02&daily=temperature_2m_mean,precipitation_sum&hourly=temperature_2m,precipitation&timezone=auto"
res = requests.get(meteo_url).json()
print(res.keys())
