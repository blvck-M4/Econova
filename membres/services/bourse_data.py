# Classe python de la page entièrement par Samy

from datetime import timedelta

from django.conf import settings
import requests
from datetime import datetime, timedelta

ALPHA_VANTAGE_API_KEY = settings.ALPHA_VANTAGE_API_KEY


def stock_data(request):
    stock_data = None  # Par défaut, pas de données
    if 'symbol' in request.GET:
        symbol = request.GET['symbol'].upper()
        period = request.GET.get('period', '5j')

        # Configuration des périodes
        if period == '24h':
            function = "TIME_SERIES_INTRADAY"
            interval = "60min"  # Données horaires
            outputsize = "compact"
            days = 1
        elif period == '5j':
            function = "TIME_SERIES_DAILY"
            outputsize = "compact"
            days = 5
        elif period == '30j':
            function = "TIME_SERIES_DAILY"
            outputsize = "compact"
            days = 30
        elif period == '90j':
            function = "TIME_SERIES_DAILY"
            outputsize = "compact"
            days = 90
        elif period == '1an':
            function = "TIME_SERIES_DAILY"
            outputsize = "compact"
            days = 365
        else:  # 'tout'
            function = "TIME_SERIES_DAILY"
            outputsize = "full"
            days = None

        # Récupération des données depuis Alpha Vantage
        url = "https://www.alphavantage.co/query"
        params = {
            "function": "TIME_SERIES_DAILY",
            "symbol": symbol,
            "apikey": ALPHA_VANTAGE_API_KEY,
            "outputsize": outputsize
        }


        if period == '24h':
            params["interval"] = interval

        response = requests.get(url, params=params)
        data = response.json()

        # Traitement des données
        if period == '24h' and "Time Series (60min)" in data:
            time_series = data["Time Series (60min)"]
            # Récupérer les 24 dernières heures
            all_timestamps = sorted(time_series.keys(), reverse=True)
            timestamps = all_timestamps[:24]  # 24 dernières heures
            prices = [float(time_series[ts]["4. close"]) for ts in timestamps]
            # Formater les heures (ex: "14:00")
            labels = [datetime.strptime(ts, '%Y-%m-%d %H:%M:%S').strftime('%H:%M') for ts in timestamps]
        else:
            # Traitement normal pour les autres périodes
            time_series = data.get("Time Series (Daily)", {})
            all_dates = sorted(time_series.keys(), reverse=True)
            if days:
                dates = all_dates[:days]
            else:
                dates = all_dates
            prices = [float(time_series[date]["4. close"]) for date in dates]
            labels = [datetime.strptime(date, '%Y-%m-%d').strftime('%d/%m') for date in dates]

            # Récupération des données fondamentales
            fundamental_params = {
                "function": "OVERVIEW",
                "symbol": symbol,
                "apikey": ALPHA_VANTAGE_API_KEY
            }
            fundamental_response = requests.get(url, params=fundamental_params)
            fundamental_data = fundamental_response.json()

            # Calcul des indicateurs techniques
            sma_20 = sum(prices[:20]) / 20 if len(prices) >= 20 else None
            daily_volume = [float(time_series[date]["5. volume"]) for date in dates[:5]]
            avg_volume = sum(daily_volume) / len(daily_volume) if daily_volume else 0


            stock_data = {
                "symbol": symbol,
                "name": fundamental_data.get("Name", symbol),
                "last_price": prices[0],
                "change": round(prices[0] - prices[1], 2) if len(prices) > 1 else 0,
                "percent_change": round(((prices[0] - prices[1]) / prices[1]) * 100, 2) if len(prices) > 1 else 0,
                "dates": dates,
                "prices": prices,
                # Données fondamentales
                "sector": fundamental_data.get("Sector", "N/A"),
                "industry": fundamental_data.get("Industry", "N/A"),
                "market_cap": "${:,.2f}B".format(
                    float(fundamental_data.get("MarketCapitalization", 0)) / 1e9) if fundamental_data.get(
                    "MarketCapitalization") else "N/A",
                "pe_ratio": fundamental_data.get("PERatio", "N/A"),
                "dividend_yield": fundamental_data.get("DividendYield", "N/A"),
                "52_week_high": fundamental_data.get("52WeekHigh", "N/A"),
                "52_week_low": fundamental_data.get("52WeekLow", "N/A"),
                # Données techniques
                "sma_20": round(sma_20, 2) if sma_20 else "N/A",
                "volume": "{:,.0f}".format(avg_volume),
                # Données supplémentaires
                "open_price": time_series[dates[0]]["1. open"] if dates else "N/A",
                "daily_high": time_series[dates[0]]["2. high"] if dates else "N/A",
                "daily_low": time_series[dates[0]]["3. low"] if dates else "N/A",
            }

        return stock_data