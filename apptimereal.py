import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime
import time

# Configuración
st.set_page_config(page_title="Sistema de Calificación", page_icon="🏆", layout="wide")

TEMAS = [
    "1. SOP - Síndrome de Ovario Poliquístico",
    "2. Interfaz IA El Castillo de Tequila", 
    "3. Pronóstico de Demanda Grupo Collins",
    "4. Conflicto Vial López Mateos"
]

CRITERIOS = {
    "FORMALIDAD DE LA PRESENTACIÓN": [
        "Se presentó el día y la hora establecidos",
        "Se respetó el tiempo de duración de la exposición",
        "La vestimenta es casual formal"
    ],
    "HABILIDADES COMUNICATIVAS": [
        "Habla de forma natural, sin titubeos, haciendo fluido el mensaje",
        "Utiliza una postura corporal con la que muestra seguridad de lo que está hablando",
        "La transmisión del mensaje es efectiva"
    ],
    "DOMINIO DEL TEMA": [
        "Muestra excelente dominio del tema",
        "Puede contestar con precisión todas las preguntas planteadas"
    ],
    "SOLUTION VALUE": [
        "Identificó con precisión las variables",
        "El método es claro y consiso",
        "El razonamiento matemático es claro y congruente",
        "La interpretación matemática es fiable",
        "La solution aporta valor agregado, creatividad e innovación"
    ]
}

# Cache de conexión
@st.cache_resource
def get_google_sheet():
    credentials = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=[
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
    )
    gc = gspread.authorize(credentials)
    return gc.open(st.secrets["sheet_name"])

@st.cache_resource
def init_sheets():
    spreadsheet = get_google_sheet()
    
    try:
        config_sheet = spreadsheet.worksheet("Config")
    except gspread.exceptions.WorksheetNotFound:
        config_sheet = spreadsheet.add_worksheet("Config", rows=100, cols=10)
        config_sheet.update('A1:C1', [['Timestamp', 'Jueces', 'EquiposPorTema']])
    
    try:
        calif_sheet = spreadsheet.worksheet("Calificaciones")
    except gspread.exceptions.WorksheetNotFound:
        calif_sheet = spreadsheet.add_worksheet("Calificaciones", rows=10000, cols=10)
        calif_sheet.update('A1:H1', [['Tema', 'Equipo', 'Juez', 'Categoria', 'Criterio', 'Cumple', 'Puntos', 'Timestamp']])
    
    return config_sheet, calif_sheet

# Inicializar hojas
def init_sheets():
    spreadsheet = get_google_sheet()
    
    # Obtener lista de hojas existentes
    existing_sheets = [sheet.title for sheet in spreadsheet.worksheets()]
    
    # Config
    if "Config" not in existing_sheets:
        config_sheet = spreadsheet.add_worksheet("Config", rows=100, cols=10)
        config_sheet.update('A1:C1', [['Timestamp', 'Jueces', 'EquiposPorTema']])
    else:
        config_sheet = spreadsheet.worksheet("Config")
    
    # Calificaciones
    if "Calificaciones" not in existing_sheets:
        calif_sheet = spreadsheet.add_worksheet("Calificaciones", rows=10000, cols=10)
        calif_sheet.update('A1:H1', [['Tema', 'Equipo', 'Juez', 'Categoria', 'Criterio', 'Cumple', 'Puntos', 'Timestamp']])
    else:
        calif_sheet = spreadsheet.worksheet("Calificaciones")
    
    return config_sheet, calif_sheet

# Guardar configuración
def guardar_config(jueces, equipos_por_tema):
    config_sheet, _ = init_sheets()
    config_sheet.append_row([
        str(datetime.now()),
        str(jueces),
        str(equipos_por_tema)
    ])

# Cargar configuración
def cargar_config():
    config_sheet, _ = init_sheets()
    values = config_sheet.get_all_values()
    if len(values) > 1:
        last_config = values[-1]
        return {
            'jueces': eval(last_config[1]),
            'equipos_por_tema': eval(last_config[2])
        }
    return None

# Guardar calificaciones por lote
def guardar_calificaciones_batch(calificaciones):
    _, calif_sheet = init_sheets()
    # Convertir a lista de listas
    rows = []
    timestamp = str(datetime.now())
    for calif in calificaciones:
        rows.append([
            calif['tema'],
            calif['equipo'],
            calif['juez'],
            calif['categoria'],
            calif['criterio'],
            calif['cumple'],
            calif['puntos'],
            timestamp
        ])
    
    # Guardar todas de una vez
    if rows:
        calif_sheet.append_rows(rows)

# Obtener calificaciones existentes
@st.cache_data(ttl=5)
def obtener_calificaciones():
    _, calif_sheet = init_sheets()
    values = calif_sheet.get_all_records()
    if not values:  # Si está vacía
        return pd.DataFrame(columns=['Tema', 'Equipo', 'Juez', 'Categoria', 'Criterio', 'Cumple', 'Puntos', 'Timestamp'])
    return pd.DataFrame(values)

# Obtener ranking
def calcular_ranking(tema):
    df = obtener_calificaciones()
    if df.empty:
        return pd.DataFrame()
    
    # Filtrar por tema
    df_tema = df[df['Tema'] == tema].copy()
    
    # Calcular puntos por juez
    resumen = df_tema.groupby(['Equipo', 'Juez'])['Puntos'].sum().reset_index()
    
    # Pivotar para tener jueces como columnas
    pivot = resumen.pivot(index='Equipo', columns='Juez', values='Puntos').fillna(0)
    
    # Calcular promedio
    pivot['Promedio'] = pivot.mean(axis=1)
    
    # Ordenar y agregar posición
    pivot = pivot.sort_values('Promedio', ascending=False)
    pivot.insert(0, 'Posición', range(1, len(pivot) + 1))
    
    return pivot.reset_index()

# UI Principal
st.title("🏆 Sistema de Calificación - Solution Challenge 2025B")

# Estado de sincronización
sync_status = st.sidebar.empty()

# Inicializar
config_sheet, calif_sheet = init_sheets()

# Cargar configuración
config = cargar_config()

if not config:
    # CONFIGURACIÓN INICIAL
    st.header("⚙️ Configuración Inicial")
    
    num_jueces = st.number_input("Número de jueces", 3, 5, 3)
    jueces = []
    cols = st.columns(num_jueces)
    for i in range(num_jueces):
        with cols[i]:
            jueces.append(st.text_input(f"Juez {i+1}", f"Juez {i+1}"))
    
    st.subheader("📚 Equipos por Tema")
    equipos_por_tema = {}
    
    for tema in TEMAS:
        with st.expander(f"🎯 {tema}"):
            num_equipos = st.number_input(f"Equipos", 1, 12, 2, key=f"n_{tema}")
            equipos = []
            cols = st.columns(min(3, num_equipos))
            for i in range(num_equipos):
                with cols[i % 3]:
                    equipos.append(st.text_input(f"Equipo {i+1}", f"Equipo {i+1}", key=f"e_{tema}_{i}"))
            equipos_por_tema[tema] = equipos
    
    if st.button("✅ Iniciar Competencia", type="primary", use_container_width=True):
        guardar_config(jueces, equipos_por_tema)
        st.rerun()

else:
    # SISTEMA PRINCIPAL
    jueces = config['jueces']
    equipos_por_tema = config['equipos_por_tema']
    
    # Sidebar
    st.sidebar.title("🎯 Navegación")
    tema_actual = st.sidebar.selectbox("Tema:", TEMAS)
    modo = st.sidebar.radio("Modo:", ["📝 Calificar", "📊 Ranking"])
    
    # Auto-refresh para ranking
    if modo == "📊 Ranking":
        auto_refresh = st.sidebar.checkbox("🔄 Auto-actualizar")
        if auto_refresh:
            st.empty()
            time.sleep(3)
            st.rerun()
    
    # Botón para abrir Google Sheet
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"[📊 Abrir Google Sheet](https://docs.google.com/spreadsheets/d/{st.secrets['sheet_id']})")
    
    # MODO CALIFICAR
    if modo == "📝 Calificar":
        st.header(f"📝 Calificar - {tema_actual}")
        
        col1, col2 = st.columns(2)
        with col1:
            juez = st.selectbox("👤 Juez:", jueces)
        with col2:
            equipo = st.selectbox("🎪 Equipo:", equipos_por_tema[tema_actual])
        
        st.markdown("---")
        
        # Contenedor para calificaciones temporales
        if 'temp_calif' not in st.session_state:
            st.session_state.temp_calif = []
        
        total_puntos = 0
        calificaciones_actuales = []
        
        # Obtener calificaciones previas
        df_previas = obtener_calificaciones()
        
        for categoria, criterios in CRITERIOS.items():
            st.markdown(f"### {categoria}")
            
            for criterio in criterios:
                col1, col2, col3 = st.columns([4, 1, 1.5])
                
                # Buscar calificación previa
                prev = df_previas[
                    (df_previas['Tema'] == tema_actual) &
                    (df_previas['Equipo'] == equipo) &
                    (df_previas['Juez'] == juez) &
                    (df_previas['Categoria'] == categoria) &
                    (df_previas['Criterio'] == criterio)
                ]
                
                if not prev.empty:
                    cumple_prev = prev.iloc[0]['Cumple']
                    puntos_prev = float(prev.iloc[0]['Puntos'])
                    # Fix para datos malos
                    if cumple_prev and puntos_prev == 0.0:
                        puntos_prev = 10.0
                else:
                    cumple_prev = False
                    puntos_prev = 10.0
                
                with col1:
                    st.write(f"• {criterio}")
                
                with col2:
                    cumple = st.checkbox("✓", value=cumple_prev, 
                                       key=f"{tema_actual}_{equipo}_{juez}_{categoria}_{criterio}")
                
                with col3:
                    if cumple:
                        puntos = st.number_input("Pts", 0.0, 10.0, puntos_prev, 0.5,
                                               key=f"{tema_actual}_{equipo}_{juez}_{categoria}_{criterio}_pts")
                        total_puntos += puntos
                    else:
                        puntos = 0
                        st.write("—")
                
                # Agregar a lista temporal
                calificaciones_actuales.append({
                    'tema': tema_actual,
                    'equipo': equipo,
                    'juez': juez,
                    'categoria': categoria,
                    'criterio': criterio,
                    'cumple': cumple,
                    'puntos': puntos
                })
        
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.metric("🎯 TOTAL", f"{total_puntos:.1f} pts")
        
        # Guardar
        if st.button("💾 Guardar Calificación", type="primary", use_container_width=True):
            with st.spinner("Guardando..."):
                # Limpiar calificaciones previas del mismo juez/equipo/tema
                guardar_calificaciones_batch(calificaciones_actuales)
                st.success(f"✅ Guardado: {equipo} por {juez}")
                time.sleep(1)
                # Limpiar cache
                obtener_calificaciones.clear()
                st.rerun()
        
        # Mostrar estado
        sync_status.info(f"✅ Conectado a Google Sheets")
    
    # MODO RANKING
    else:
        st.header(f"📊 Ranking - {tema_actual}")
        
        df_ranking = calcular_ranking(tema_actual)
        
        if not df_ranking.empty:
            # Podio
            if len(df_ranking) >= 3:
                col1, col2, col3 = st.columns(3)
                with col2:
                    st.markdown("# 🥇")
                    st.subheader(df_ranking.iloc[0]['Equipo'])
                    st.metric("", f"{df_ranking.iloc[0]['Promedio']:.2f}")
                with col1:
                    st.markdown("# 🥈")
                    st.subheader(df_ranking.iloc[1]['Equipo'])
                    st.metric("", f"{df_ranking.iloc[1]['Promedio']:.2f}")
                with col3:
                    st.markdown("# 🥉")
                    st.subheader(df_ranking.iloc[2]['Equipo'])
                    st.metric("", f"{df_ranking.iloc[2]['Promedio']:.2f}")
            
            st.markdown("---")
            st.dataframe(df_ranking, use_container_width=True, hide_index=True)
            
            # Última actualización
            st.caption(f"Última actualización: {datetime.now().strftime('%H:%M:%S')}")
        else:
            st.warning("No hay calificaciones registradas aún")