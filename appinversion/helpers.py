import requests

def obtener_precio_actual(activo):
    activo = activo.upper()

    # Mapeo de símbolos a CoinGecko IDs
    mapeo_coingecko = {
        "BTC": "bitcoin",
        "ETH": "ethereum",
        "ADA": "cardano",
        "BNB": "binancecoin",
        "SOL": "solana",
        "USDT": "tether",
        "DOGE": "dogecoin",
        "XRP": "ripple"
        # Agregá más si querés
    }

    try:
        if activo in mapeo_coingecko:
            id_cg = mapeo_coingecko[activo]
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={id_cg}&vs_currencies=usd"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            return float(data[id_cg]["usd"])
        else:
            # Activos no cripto: simulación
            return round(100 + hash(activo) % 100, 2)

    except Exception as e:
        print(f"Error al obtener precio de {activo}: {e}")
        return 0.0
