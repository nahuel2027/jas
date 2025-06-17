import requests

def obtener_precio_actual(activo):
    # Usa CoinGecko si es cripto, o mock para acciones
    activo = activo.upper()
    try:
        if activo in ["BTC", "ETH", "ADA"]:
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={activo.lower()}&vs_currencies=usd"
            r = requests.get(url).json()
            return r[activo.lower()]["usd"]
        else:
            # Simulación de precio para activos no cripto
            return 100 + hash(activo) % 100  # Precio aleatorio entre 100-200
    except:
        return 0.0

def calcular_rendimiento(cantidad, precio_compra, precio_actual):
    if precio_actual == 0:
        return 0
    valor_actual = cantidad * precio_actual
    valor_inicial = cantidad * precio_compra
    return round(((valor_actual - valor_inicial) / valor_inicial) * 100, 2)
