import streamlit as st
import json
import requests
import folium
from streamlit_folium import st_folium
import pandas as pd

# From https://stackpath.boostrapcdn.com/bootstrap/4.1.1/css/bootstrap.min.css
# css_file = "bootstrap.min.css"
# 
# try:
#     css_file_content = open(css_file).read()
# except FileNotFoundError:
#     css_file_content = requests.get(css_file).text
# 
# st.markdown(f"<style>{css_file_content}</style>", unsafe_allow_html=True)

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
st.image('https://www.electoral.gob.ar/nuevo/img/Logo_cne_350x60px.png', width=400)
st.title('Normalizar domicilio')

with st.expander("Ayuda", expanded=False, icon=":material/help:"):
    st.write("Ingrese una de las siguientes opciones:")
    st.markdown("- Calle y número (por ejemplo `Urquiza 3046`)")
    st.markdown("- Intersección de calles (por ejemplo, `Las Heras y Padilla`)")
    st.markdown("- Tramo _entre_ dos calles (por ejemplo, `Urquiza entre Crespo y Suipacha`)")

# Selección de la provincia
provincias = get_provincias()
provincia_nombres = [prov['nombre'] for prov in provincias]
provincia_nombres = sorted(provincia_nombres)
provincia_index = provincia_nombres.index("Santa Fe")
provincia = st.selectbox("Seleccione la provincia", provincia_nombres, index=provincia_index)

# Selección del departamento (después de seleccionar provincia)
if provincia and provincia != "Ciudad Autónoma de Buenos Aires":
    departamentos = get_departamentos(provincia)
    departamento_nombres = [dep['nombre'] for dep in departamentos]
    departamento = st.selectbox("Seleccione el departamento", sorted(departamento_nombres))
elif provincia == "Ciudad Autónoma de Buenos Aires":
    departamento = None
    localidad = None

# Selección de la localidad (después de seleccionar departamento)
if departamento:
    localidades = get_localidades(provincia)
    localidad_nombres = [loc['nombre'] for loc in localidades]
    localidad = st.selectbox("Seleccione la localidad", sorted(localidad_nombres))

# Ingreso de domicilio
if localidad or provincia == "Ciudad Autónoma de Buenos Aires":
    direccion = st.text_input("Ingrese domicilio", value=None)
    # altura = st.text_input("Ingrese la altura")

# Función para obtener coordenadas de una dirección
def get_direccion(provincia, direccion, departamento=None, localidad=None):

    if provincia == "Ciudad Autónoma de Buenos Aires":        
        url = f"https://apis.datos.gob.ar/georef/api/direcciones?provincia=CABA&direccion={direccion}"
    elif departamento is not None:
        url = f"https://apis.datos.gob.ar/georef/api/direcciones?provincia={provincia}&departamento={departamento}&localidad={localidad}&direccion={direccion}"        
    response = requests.get(url)
    data = response.json()
    if 'direcciones' in data and data['direcciones']:
        return data['direcciones'][0], url
    return None, url

def details_as_table(data):
    
    df = pd.DataFrame([
        [
            f"{data['altura']['valor']} {data['altura']['unidad'] if data['altura']['unidad'] else ''}" if data['altura']['valor'] else "N/A",
            data['calle']['nombre'],
            data['calle_cruce_1']['nombre'] if data['calle_cruce_1']['nombre'] else "N/A",
            data['calle_cruce_2']['nombre'] if data['calle_cruce_2']['nombre'] else "N/A",
            f"{data_direccion['ubicacion']['lat']:.3f}, {data_direccion['ubicacion']['lon']:.3f}"
        ]], columns=['Altura', 'Calle', 'Calle Cruce 1', 'Calle Cruce 2', 'Coordenadas']
    ).T
    df.columns = [""]
    return df

# Mostrar un mapa interactivo con coordenadas de la API
if direccion:
    
    data_direccion, url = get_direccion(provincia, direccion, departamento, localidad)
    
    if data_direccion:
        nombre_normalizado = data_direccion['nomenclatura']  # Nombre normalizado que devuelve el endpoint
        lat = data_direccion['ubicacion']['lat']
        lon = data_direccion['ubicacion']['lon']
        
        # Mostrar el nombre normalizado en estilo h1
        st.markdown(f'<p style="font-size:1.5em;color:darkgreen;" align="center">{nombre_normalizado}</p>', unsafe_allow_html=True)
            
        with st.expander("Ver detalles:"):
            st.markdown(f"Coordenadas: {lat:.2f}, {lon:.2f}")
            # st.markdown(f"Dirección completa: {data_direccion['direccion']['calle']['nombre']} {data_direccion['direccion']['altura']['valor']}")
            #st.markdown(f"Localidad: {data_direccion['localidad']['nombre']}")
            #st.markdown(f"Departamento: {data_direccion['departamento']['nombre']}")
            # st.markdown(f"Provincia: {data_direccion['provincia']['nombre']}")
            # st.markdown(f"Código Postal: {data_direccion['cod_postal']}")
            # Print the API endpoint
            # st.code(json.dumps(data_direccion, indent=4))
         
            st.table(details_as_table(data_direccion))

            # Mostrar el DataFrame centrado
            # st.dataframe(details_as_table(data_direccion))
            # st.markdown(, unsafe_allow_html=True)

            st.write("Los datos se obtuvieron de este endpoint:")

            st.code(url, wrap_lines=True)
            st.markdown(f'<a href="{url}" target="_blank">Abrir endpoint en nueva pestaña</a>', unsafe_allow_html=True)



        
        # Crear un mapa con las coordenadas obtenidas
        m = folium.Map(location=[lat, lon], zoom_start=16)
        
        # Añadir marcador para la ubicación
        folium.Marker([lat, lon], popup=direccion).add_to(m)
        
        # Mostrar el mapa en Streamlit
        st_folium(m, width=700, height=500)

    elif direccion != "": 
        texto = "No se pudo encontrar esa dirección."
        icono = ''
        st.markdown(f'<p style="font-size:1.5em;color:darkred;" align="center">{icono}{texto}</p>', unsafe_allow_html=True)        
        with st.expander("Ver posibles causas"):
            st.write("Este es el endpoint que fue consultado:")
            st.code(url)

