import requests

# URL de la API
API_URL = "https://script.google.com/macros/s/AKfycbz-_eiS8MZAtpu-g2qiQnIe5QefufcxpiJkXkSdmG3sdlij1OEIDPUHAzdF_IyMmgcoaw/exec"

# Número de proforma para buscar
proforma_a_buscar = "0738-25"

# Parámetros para obtener los datos completos de la proforma
params = {
    "action": "getFullProformaData",
    "numeroProforma": proforma_a_buscar
}

# Realizar la solicitud GET
response = requests.get(API_URL, params=params)

# Verificar la respuesta
if response.status_code == 200:
    try:
        data = response.json()
        print("✅ Respuesta de la API:")
        print(data)
    except requests.exceptions.JSONDecodeError:
        print("❌ Error: La respuesta no es un JSON válido.")
        print(response.text)
else:
    print(f"❌ Error en la API. Código de respuesta: {response.status_code}")
    print(response.text)
