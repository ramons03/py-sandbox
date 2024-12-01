import os
import requests
import logging
import json
from urllib.parse import urlparse
from dotenv import load_dotenv

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("bitly_fetcher.log"),  # Guardar logs en archivo
        logging.StreamHandler()                   # Mostrar logs en consola
    ]
)

# Cargar las variables desde .env
load_dotenv()
token = os.getenv("BITLY_TOKEN")

if not token:
    raise ValueError("No se encontró el token en el archivo .env")

# Configuración inicial
headers = {
    "Authorization": f"Bearer {token}"
}
base_url = "https://api-ssl.bitly.com/v4/groups/Ba2518tdV09/bitlinks"
params = {
    "size": 100  # Tamaño por página
}

# Lista para guardar todos los resultados
all_links = []

logging.info("Iniciando la obtención de links desde Bitly...")

# Paginación
while True:
    logging.info(f"Realizando solicitud a {base_url} con params {params}...")
    response = requests.get(base_url, headers=headers, params=params)
    response.raise_for_status()  # Lanzar excepción en caso de error
    data = response.json()

    # Agregar los links de la respuesta actual
    links_obtenidos = len(data["links"])
    logging.info(f"Se obtuvieron {links_obtenidos} links en esta página.")
    all_links.extend(data["links"])

    # Verificar si hay una página siguiente
    next_url = data["pagination"].get("next")
    if next_url:
        # Validar si next_url es relativa o absoluta
        if not urlparse(next_url).scheme:
            next_url = f"https://api-ssl.bitly.com{next_url}"  # Asegurar esquema
        base_url = next_url
        params = {}  # Limpiar parámetros porque 'next' ya los incluye
        logging.info(f"URL de la siguiente página: {next_url}")
    else:
        logging.info("No hay más páginas disponibles. Finalizando...")
        break

# Guardar los resultados en un archivo JSON
output_file = "bitly_links.json"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(all_links, f, ensure_ascii=False, indent=4)

logging.info(f"Se guardaron {len(all_links)} links en el archivo {output_file}.")

# Mostrar un resumen en consola
logging.info("Resumen de los links obtenidos:")
for link in all_links:
    logging.info(f"Short Link: {link['link']}, Long URL: {link['long_url']}")
