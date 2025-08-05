import requests

def obtener_ultima_proforma():
    url = "https://script.google.com/macros/s/AKfycbyFgBEg_qbJ-U4jDXC8UOZnvkRJb4h2L6PpLSzWa_WSj1e078WD7wVBBs3LMpyTUb8moQ/exec"

    try:
        response = requests.get(url)
        response.raise_for_status()  # Verifica que la solicitud fue exitosa
        last_proforma = response.text.strip()  # Elimina espacios en blanco adicionales
        print(f"Última proforma obtenida: '{last_proforma}'")
        return last_proforma
    except requests.exceptions.RequestException as e:
        print(f"Error al realizar la solicitud: {e}")
        return None

# Llamada a la función
ultima_proforma = obtener_ultima_proforma()
