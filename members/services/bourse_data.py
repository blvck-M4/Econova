from django.conf import settings
import requests
ALPHA_VANTAGE_API_KEY = settings.ALPHA_VANTAGE_API_KEY
def stock_data(request):
    stock_data = None  # Par défaut, pas de données
    if 'symbol' in request.GET:
        symbol = request.GET['symbol'].upper()

        # Récupération des données depuis Alpha Vantage
        url = f"https://www.alphavantage.co/query"
        params = {
            "function": "TIME_SERIES_DAILY",
            "symbol": symbol,
            "apikey": ALPHA_VANTAGE_API_KEY,
            "outputsize": "compact"
        }

        response = requests.get(url, params=params)
        data = response.json()

        if "Time Series (Daily)" in data:
            time_series = data["Time Series (Daily)"]
            dates = list(time_series.keys())[:30]  # Récupère les 30 derniers jours
            prices = [float(time_series[date]["4. close"]) for date in dates]

            stock_data = {
                "symbol": symbol,
                "name": symbol,  # Alpha Vantage n'a pas de champ 'nom', mais tu peux le compléter
                "last_price": prices[0],  # Dernier prix
                "change": round(prices[0] - prices[1], 2),
                "percent_change": round(((prices[0] - prices[1]) / prices[1]) * 100, 2),
                "dates": dates[::-1],  # Inverser pour afficher dans le bon ordre
                "prices": prices[::-1]
            }

        return stock_data