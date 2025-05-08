import yfinance as yf
import numpy as np
actions = []
def listeActions(symbols):
    if len(actions) == 0:
        for symbol in symbols:
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                symbole = info['symbol'].strip("[]' \n\r\t")
                nom = info['shortName']
                prix = info['regularMarketPrice']

                # Données historiques
                historique = ticker.history(period="6mo")
                prix_cloture = historique["Close"]

                # Calcul du risque : volatilité annualisée
                rendements_log = np.log(prix_cloture / prix_cloture.shift(1)).dropna()
                risque = rendements_log.std() * np.sqrt(252)
                tendance = rendements_log.mean() * 252
                data = ticker.history(period="6mo")
                if data.empty:
                    print(f"{symbol}: pas de données disponibles.")
                    continue
                actions.append({"symbole": symbole, "nom": nom, "prix": round(prix,2), "risque": round(risque,4),
                                                                                                       "tendance": round(tendance,4)})

            except Exception as e:
                print(f"Erreur pour {symbol}: {e}")

    return actions

def graphProduit(action):
    donnees = []
    try:
        print(action['symbole'])
        ticker = yf.Ticker(action['symbole'])

        # Récupère les données sur 30 jours
        historique = ticker.history(period="6mo", interval="1mo")

        # Parcours des lignes
        for index, row in historique.iterrows():
            date = index.strftime('%Y-%m-%d')  # Format date lisible
            prix = row["Close"]  # Prix de clôture
            donnees.append({"date": date, "prix": prix})
            print(f"{date}: {prix}")
    except Exception as e:
        print(f"Erreur pour {action['symbole']}: {e}")


    return donnees

#Simulation de Monte Carlo
def lancerSimulations(symbole, nbannes):
    # Récupérer les données depuis yfinance
    ticker = yf.Ticker(symbole)  # Choisis ton symbole boursier
    historique = ticker.history(period="1y")
    prix_cloture = historique["Close"]

    # Calcul des paramètres
    rendements_log = np.log(prix_cloture / prix_cloture.shift(1)).dropna()

    S0 = prix_cloture.iloc[-1]             # Prix actuel
    mu = rendements_log.mean() * 252       # Drift (rendement annuel)
    sigma = rendements_log.std() * np.sqrt(252)  # Volatilité annualisée

    # Simulation de Monte Carlo
    N = 252 * nbannes       # Nombre de jours (1 an de bourse)
    M = 100        # Nombre de simulations

    dt = 1 / N
    simulations = np.zeros((M, N))
    for i in range(M):
        prices = [S0]
        for _ in range(1, N):
            rand = np.random.normal()
            St = prices[-1] * np.exp((mu - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * rand)
            prices.append(St)
        simulations[i] = prices

    simulations_list = [sim.tolist() if isinstance(sim, np.ndarray) else sim for sim in simulations]
    return simulations_list


