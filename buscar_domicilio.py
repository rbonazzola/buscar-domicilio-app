import streamlit as st
import requests
import folium
from streamlit_folium import st_folium

# Funciones para obtener datos de la API
def get_provincias():
    url = "https://apis.datos.gob.ar/georef/api/provincias"
    response = requests.get(url)
    return response.json()['provincias']

def get_departamentos(provincia):
    url = f"https://apis.datos.gob.ar/georef/api/departamentos?provincia={provincia}&max=99"
    response = requests.get(url)
    return response.json()['departamentos']

def get_localidades(provincia):
    url = f"https://apis.datos.gob.ar/georef/api/localidades?provincia={provincia}&departamento={departamento}&campos=nombre&max=999"
    response = requests.get(url)
    return response.json()['localidades']

# Interfaz de selección en Streamlit
st.title('Seleccionar Domicilio en Argentina')

# Selección de la provincia
provincias = get_provincias()
provincia_nombres = [prov['nombre'] for prov in provincias]
provincia_nombres = sorted(provincia_nombres)
provincia_index = provincia_nombres.index("Santa Fe")
provincia = st.selectbox("Seleccione la provincia", provincia_nombres, index=provincia_index)

# Selección del departamento (después de seleccionar provincia)
if provincia:
    departamentos = get_departamentos(provincia)
    departamento_nombres = [dep['nombre'] for dep in departamentos]
    departamento = st.selectbox("Seleccione el departamento", sorted(departamento_nombres))

# Selección de la localidad (después de seleccionar departamento)
if departamento:
    localidades = get_localidades(provincia)
    localidad_nombres = [loc['nombre'] for loc in localidades]
    localidad = st.selectbox("Seleccione la localidad", sorted(localidad_nombres))

# Ingreso de domicilio
if localidad:
    calle = st.text_input("Ingrese el nombre de la calle")
    altura = st.text_input("Ingrese la altura")

# Función para obtener coordenadas de una dirección
def get_direccion(provincia, departamento, direccion):
    url = f"https://apis.datos.gob.ar/georef/api/direcciones?provincia={provincia}&departamento={departamento}&direccion={direccion}"
    response = requests.get(url)
    data = response.json()
    if 'direcciones' in data and data['direcciones']:
        return data['direcciones'][0]
    return None

# Mostrar un mapa interactivo con coordenadas de la API
if calle and altura:
    direccion = f"{calle} al {altura}"
    data_direccion = get_direccion(provincia, departamento, direccion)
    
    if data_direccion:
        nombre_normalizado = data_direccion['nomenclatura']  # Nombre normalizado que devuelve el endpoint
        lat = data_direccion['ubicacion']['lat']
        lon = data_direccion['ubicacion']['lon']
        
        # Mostrar el nombre normalizado en estilo h1
        st.markdown(f"## {nombre_normalizado}")
        
        # Crear un mapa con las coordenadas obtenidas
        m = folium.Map(location=[lat, lon], zoom_start=16)
        
        # Añadir marcador para la ubicación
        folium.Marker([lat, lon], popup=direccion).add_to(m)
        
        # Mostrar el mapa en Streamlit
        st_folium(m, width=700, height=500)
    else:
        st.write("No se encontraron coordenadas para esa dirección.")

