import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import datetime
from io import BytesIO
import json
import time
import altair as alt

st.set_page_config(page_title="Sistema de Calificación", page_icon="🏆", layout="wide")

st.markdown("""
<style>
    /* Mejor responsive para móviles */
    @media (max-width: 768px) {
        .stNumberInput > div > div > input {
            font-size: 18px !important;
        }
        .stCheckbox > label > span {
            font-size: 16px !important;
        }
        div[data-testid="column"] {
            padding: 0.2rem !important;
        }
    }
    /* Checkboxes más grandes */
    .stCheckbox > label > div[role="checkbox"] {
        width: 25px;
        height: 25px;
    }
    /* Botones más visibles */
    .stButton > button {
        min-height: 50px;
        font-size: 18px;
    }
</style>
""", unsafe_allow_html=True)

# MODO ADMIN
if 'mode' not in st.session_state:
    st.session_state.mode = 'juez'  # Por defecto modo juez

@st.cache_data(ttl=15)
def obtener_calificaciones():
    response = supabase.table('calificaciones').select("*").execute()
    return pd.DataFrame(response.data)

@st.cache_resource
def init_supabase_v2():
    return create_client(st.secrets["supabase_url"], st.secrets["supabase_key"])

supabase = init_supabase_v2()

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

def cargar_config():
    response = supabase.table('config').select("*").order('id', desc=True).limit(1).execute()
    if response.data:
        return {
            'jueces': json.loads(response.data[0]['jueces']),
            'equipos_por_tema': json.loads(response.data[0]['equipos_por_tema'])
        }
    return None

def guardar_config(jueces, equipos_por_tema):
    supabase.table('config').insert({
        'jueces': json.dumps(jueces),
        'equipos_por_tema': json.dumps(equipos_por_tema)
    }).execute()

def guardar_calificacion(tema, equipo, juez, categoria, criterio, cumple, puntos):
    supabase.table('calificaciones').upsert({
        'tema': tema,
        'equipo': equipo,
        'juez': juez,
        'categoria': categoria,
        'criterio': criterio,
        'cumple': cumple,
        'puntos': puntos
    }, on_conflict='tema,equipo,juez,categoria,criterio').execute()

def calcular_ranking(tema):
    df = obtener_calificaciones()
    if df.empty:
        return pd.DataFrame()
    
    df_tema = df[df['tema'] == tema].copy()
    if df_tema.empty:
        return pd.DataFrame()
    
    resumen = df_tema.groupby(['equipo', 'juez'])['puntos'].sum().reset_index()
    pivot = resumen.pivot(index='equipo', columns='juez', values='puntos').fillna(0)
    pivot['Promedio'] = pivot.mean(axis=1)
    pivot = pivot.sort_values('Promedio', ascending=False)
    pivot.insert(0, 'Posición', range(1, len(pivot) + 1))
    return pivot.reset_index()

def generar_excel():
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Resumen por tema
        for tema in TEMAS:
            df = calcular_ranking(tema)
            if not df.empty:
                sheet_name = tema.split('.')[1].strip()[:31]
                df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        # Detalle completo
        df_all = obtener_calificaciones()
        if not df_all.empty:
            df_all.to_excel(writer, sheet_name='Detalle Completo', index=False)
    
    output.seek(0)
    return output

# UI Principal
st.title("🏆 Sistema de Calificación - Solution Challenge 2025B")

# SELECTOR DE MODO EN SIDEBAR
st.sidebar.title("🎯 Sistema de Calificación")
st.sidebar.markdown("---")

# Cambiar entre modos
if st.session_state.mode == 'juez':
    if st.sidebar.button("🔐 Modo Administrador", use_container_width=True):
        st.session_state.mode = 'admin_login'
        st.rerun()
else:
    if st.sidebar.button("👥 Modo Juez", use_container_width=True, type="primary"):
        st.session_state.mode = 'juez'
        st.rerun()

# MODO ADMIN LOGIN
if st.session_state.mode == 'admin_login':
    st.header("🔐 Acceso Administrador")
    password = st.text_input("Contraseña:", type="password")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Entrar", type="primary"):
            try:
                # 1. LECTURA SEGURA: Lee la contraseña del admin desde secrets.toml
                password_correcta = st.secrets["admin"]["password"]
                
                # 2. COMPARACIÓN
                if password == password_correcta:
                    st.session_state.mode = 'admin'
                    st.rerun()
                else:
                    st.error("❌ Contraseña incorrecta")
            
            except KeyError:
                # 3. MANEJO DE ERRORES: Evita que la app falle si secrets.toml está incompleto
                st.error("❌ Error: La contraseña de administrador no está configurada en secrets.toml.")
    with col2:
        if st.button("Cancelar"):
            st.session_state.mode = 'juez'
            st.rerun()

# MODO ADMIN
elif st.session_state.mode == 'admin':
    st.header("⚙️ Panel de Administración")
    
    config = cargar_config()
    
    tab1, tab2, tab3, tab4 = st.tabs(["📝 Configuración", "🗑️ Reiniciar Sistema", "📊 Exportar Datos","🏆 Visualizar Rankings"])
    
    with tab1:
        st.subheader("Configuración del Sistema")
        
        # Si ya hay config, mostrar la actual
        if config:
            st.info("⚠️ Ya existe una configuración. Los cambios sobrescribirán la anterior.")
            with st.expander("Ver configuración actual"):
                st.write("**Jueces:**", config['jueces'])
                st.write("**Equipos por tema:**", config['equipos_por_tema'])
        
        num_jueces = st.number_input("Número de jueces", 3, 5, 3 if not config else len(config['jueces']))
        jueces = []
        cols = st.columns(num_jueces)
        for i in range(num_jueces):
            with cols[i]:
                default = f"Juez {i+1}" if not config else (config['jueces'][i] if i < len(config['jueces']) else f"Juez {i+1}")
                jueces.append(st.text_input(f"Juez {i+1}", default))
        
        st.subheader("📚 Equipos por Tema")
        equipos_por_tema = {}
        
        for tema in TEMAS:
            with st.expander(f"🎯 {tema}"):
                default_num = 2 if not config else len(config['equipos_por_tema'].get(tema, ['', '']))
                num_equipos = st.number_input(f"Equipos", 1, 12, default_num, key=f"n_{tema}")
                equipos = []
                cols = st.columns(min(3, num_equipos))
                for i in range(num_equipos):
                    with cols[i % 3]:
                        default_equipo = f"Equipo {i+1}"
                        if config and tema in config['equipos_por_tema'] and i < len(config['equipos_por_tema'][tema]):
                            default_equipo = config['equipos_por_tema'][tema][i]
                        equipos.append(st.text_input(f"Equipo {i+1}", default_equipo, key=f"e_{tema}_{i}"))
                equipos_por_tema[tema] = equipos
        
        if st.button("✅ Guardar Configuración", type="primary", use_container_width=True):
            guardar_config(jueces, equipos_por_tema)
            st.success("✅ Configuración guardada exitosamente")
            st.balloons()
    
    with tab2:
        st.warning("⚠️ Esta acción borrará TODAS las calificaciones y configuraciones")
        if st.checkbox("Confirmo que quiero borrar todo"):
            if st.button("🗑️ BORRAR TODO", type="secondary"):
                supabase.table('config').delete().neq('id', 0).execute()
                supabase.table('calificaciones').delete().neq('id', 0).execute()
                obtener_calificaciones.clear()
                st.success("✅ Sistema reiniciado")
                st.rerun()
    # En el tab3 del admin:
    with tab3:
        st.subheader("📥 Exportar Resultados")
        if st.button("📊 Generar Excel"):
            excel = generar_excel()
            st.download_button(
                "⬇️ Descargar Excel",
                excel,
                f"resultados_challenge_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                "application/vnd.ms-excel"
            )

    with tab4:
        st.subheader("🏆 Rankings en Vivo")
        
        # Selector de tema
        tema_mostrar = st.selectbox("Selecciona el tema:", TEMAS, index=0, key="admin_tema_ranking")
        
        # Auto-refresh para proyección
        auto_refresh = st.checkbox("🔄 Auto-actualizar cada 5 segundos", key="admin_refresh")
        if auto_refresh:
            time.sleep(5)
            st.rerun()
        
        # Mostrar ranking grande para proyectar
        df_ranking = calcular_ranking(tema_mostrar)
        
        if not df_ranking.empty:
            # Podio visual más grande
            st.markdown("---")
            if len(df_ranking) >= 3:
                col1, col2, col3 = st.columns(3)
                with col2:
                    st.markdown("<h1 style='text-align:center;font-size:60px;'>🥇</h1>", unsafe_allow_html=True)
                    st.markdown(f"<h2 style='text-align:center;'>{df_ranking.iloc[0]['equipo']}</h2>", unsafe_allow_html=True)
                    st.markdown(f"<h1 style='text-align:center;color:gold;'>{df_ranking.iloc[0]['Promedio']:.2f}</h1>", unsafe_allow_html=True)
                with col1:
                    st.markdown("<h1 style='text-align:center;font-size:50px;'>🥈</h1>", unsafe_allow_html=True)
                    st.markdown(f"<h3 style='text-align:center;'>{df_ranking.iloc[1]['equipo']}</h3>", unsafe_allow_html=True)
                    st.markdown(f"<h2 style='text-align:center;color:silver;'>{df_ranking.iloc[1]['Promedio']:.2f}</h2>", unsafe_allow_html=True)
                with col3:
                    st.markdown("<h1 style='text-align:center;font-size:50px;'>🥉</h1>", unsafe_allow_html=True)
                    st.markdown(f"<h3 style='text-align:center;'>{df_ranking.iloc[2]['equipo']}</h3>", unsafe_allow_html=True)
                    st.markdown(f"<h2 style='text-align:center;color:#CD7F32;'>{df_ranking.iloc[2]['Promedio']:.2f}</h2>", unsafe_allow_html=True)
            
            st.subheader("Gráfico de Promedios")

            if not df_ranking.empty:
                # Ordenar por promedio para que el degradado tenga sentido
                df_ranking_sorted = df_ranking.sort_values('Promedio', ascending=False).reset_index(drop=True)
                
                # Crear un campo para el color basado en la posición o el promedio
                # Esto asignará un color desde el verde (más alto) hasta el rojo (más bajo)
                chart = alt.Chart(df_ranking_sorted).mark_bar().encode(
                    # Convertimos 'equipo' a nominal para que cada equipo sea una barra separada
                    y=alt.Y('equipo:N', sort='-x', title='Equipo'), # Sort='-x' ordena por 'Promedio' descendente
                    x=alt.X('Promedio:Q', title='Puntuación Promedio'),
                    color=alt.Color(
                        'Promedio:Q', # Colorea basado en el promedio
                        scale=alt.Scale(range=['red', 'orange', 'green']), # Degradado de rojo a verde
                        legend=alt.Legend(title="Promedio") # Leyenda para la escala de color
                    ),
                    # Añadir texto con el promedio en cada barra para mayor claridad
                    text=alt.Text('Promedio:Q', format='.2f') 
                ).properties(
                    title=f"Promedio de Calificaciones por Equipo ({tema_mostrar})"
                ).interactive() # Permite zoom y pan, puedes quitar .interactive() si quieres que sea completamente estático

                # Mostrar la gráfica en Streamlit
                st.altair_chart(chart, use_container_width=True)

            else:
                st.warning("No hay calificaciones para mostrar en el gráfico.")
    

            st.markdown("")
            
            # Tabla completa con estilo para proyección
            st.markdown("<h2>📊 Tabla de Posiciones</h2>", unsafe_allow_html=True)
            
            # Hacer la tabla más grande para proyección
            st.markdown("""
            <style>
                .dataframe td, .dataframe th {
                    font-size: 20px !important;
                    padding: 15px !important;
                }
            </style>
            """, unsafe_allow_html=True)
            
            st.dataframe(
                df_ranking, 
                use_container_width=True, 
                hide_index=True,
                height=600
            )
            
            # Última actualización
            st.info(f"🕐 Última actualización: {datetime.now().strftime('%H:%M:%S')}")
        else:
            st.warning("No hay calificaciones registradas para este tema")

# MODO JUEZ
# MODO JUEZ
elif st.session_state.mode == 'juez':
    config = cargar_config()
    
    if not config:
        st.error("❌ No hay configuración inicial. Solicita al administrador que configure el sistema.")
        st.stop()
    
    jueces = config['jueces']
    equipos_por_tema = config['equipos_por_tema']
    
    # --- INICIO DE LA LÓGICA DE AUTENTICACIÓN ---
    
    # Si el juez NO está autenticado, mostrar formulario de login
    if not st.session_state.get('juez_autenticado', False):
        
        st.header("👤 Login de Juez")
        st.sidebar.markdown("---")
        
        juez_seleccionado = st.sidebar.selectbox("Selecciona tu nombre:", jueces)
        password_ingresada = st.sidebar.text_input("Contraseña:", type="password", key="juez_pass_input")

        if st.sidebar.button("Entrar", type="primary", use_container_width=True):
            
            # --- INICIALIZACIÓN CRÍTICA ---
            password_correcta = None # Inicializamos a None para que siempre esté definida
            error_ocurrido = False 

            try:
                # 1. Intenta LEER la contraseña del secret.
                password_correcta = st.secrets["passwords"][juez_seleccionado]
                
            except KeyError:
                # Error Específico: El nombre del juez no está en el archivo secrets.
                st.sidebar.error(f"Error de Configuración: No se encontró una contraseña para '{juez_seleccionado}' en los secrets.")
                error_ocurrido = True
                
            except Exception:
                # Error Genérico (SOLUCIÓN AL DOBLE CLICK): st.secrets no responde a la primera.
                st.sidebar.warning(f"Error temporal al leer los secrets. Por favor, haz clic en 'Entrar' OTRA VEZ.")
                st.stop() # Detenemos el script aquí para forzar el segundo clic
                
            # --- LÓGICA DE COMPARACIÓN FINAL (Fuera del try/except) ---
            # Solo comparamos si no hubo errores bloqueantes
            if not error_ocurrido and password_correcta is not None: 
                if password_ingresada == password_correcta:
                    st.session_state.juez_autenticado = True
                    st.session_state.juez_actual = juez_seleccionado # Guardamos el juez
                    st.rerun()
                else:
                    st.sidebar.error("Contraseña incorrecta")

    # Si el juez SÍ ESTÁ AUTENTICADO, mostrar la app normal
    else:
        # Cargar el juez autenticado desde el estado
        juez_actual = st.session_state.juez_actual
        
        # Panel de juez en sidebar
        st.sidebar.markdown("---")
        st.sidebar.subheader(f"👤 Juez: {juez_actual}")
        
        if st.sidebar.button("🔐 Cerrar Sesión", use_container_width=True):
            del st.session_state.juez_autenticado
            if 'juez_actual' in st.session_state:
                del st.session_state.juez_actual
            st.rerun()
        
        st.sidebar.markdown("---")
        tema_actual = st.sidebar.selectbox("📚 Tema actual:", TEMAS, index=0)
        modo = st.sidebar.radio("Modo:", ["📝 Calificar", "📊 Ver Ranking"])
        
        if modo == "📊 Ver Ranking":
            auto_refresh = st.sidebar.checkbox("🔄 Auto-actualizar cada 3s")
            if auto_refresh:
                import time
                time.sleep(3)
                st.rerun()
        
        # --- (AQUÍ EMPIEZA TU CÓDIGO ORIGINAL) ---
        
        # CALIFICAR
        if modo == "📝 Calificar":
            st.header(f"📝 Calificar - {tema_actual}")
            st.info(f"**Juez:** {juez_actual}")
            
            equipo = st.selectbox("🎪 Equipo a calificar:", equipos_por_tema[tema_actual])
            
            st.markdown("---")
            total_puntos = 0
            df_prev = obtener_calificaciones()
            calificaciones_a_guardar = []
             # NUEVA VERIFICACIÓN DE SEGURIDAD (Si df_prev NO está vacío):
            if not df_prev.empty:
                # Si el DF NO está vacío, entonces filtramos:
                df_team = df_prev[
                    (df_prev['tema'] == tema_actual) & 
                    (df_prev['equipo'] == equipo)
                ]
            else:
                # Si el DF está vacío, inicializamos df_team como vacío para evitar el KeyError
                df_team = pd.DataFrame()

            jueces_calificaron = df_team['juez'].unique() if not df_team.empty else []

            col1, col2 = st.columns([3, 1])
            with col1:
                st.info(f"**Equipo:** {equipo}")
            with col2:
                st.metric("Calificado por", f"{len(jueces_calificaron)}/{len(jueces)} jueces")

            # Mostrar quién falta
            if len(jueces_calificaron) < len(jueces):
                faltan = [j for j in jueces if j not in jueces_calificaron]
                st.warning(f"⏳ Faltan: {', '.join(faltan)}")
            
            for categoria, criterios in CRITERIOS.items():
                st.markdown(f"### {categoria}")
                
                for criterio in criterios:
                    col1, col2, col3 = st.columns([4, 1, 1.5])
                    
                    prev = df_prev[
                        (df_prev['tema'] == tema_actual) &
                        (df_prev['equipo'] == equipo) &
                        (df_prev['juez'] == juez_actual) &
                        (df_prev['categoria'] == categoria) &
                        (df_prev['criterio'] == criterio)
                    ] if not df_prev.empty else pd.DataFrame()
                    
                    if not prev.empty:
                        cumple_str = str(prev.iloc[0]['cumple']).strip().upper()
                        cumple_prev = (cumple_str == "TRUE")
                        puntos_prev = float(prev.iloc[0]['puntos'])
                        if cumple_prev and puntos_prev == 0:
                            puntos_prev = 10.0
                    else:
                        cumple_prev = False
                        puntos_prev = 10.0
                    
                    with col1:
                        st.write(f"• {criterio}")
                    
                    with col2:
                        cumple = st.checkbox("✓", value=cumple_prev, 
                                           key=f"{tema_actual}_{equipo}_{juez_actual}_{categoria}_{criterio}")
                    
                    with col3:
                        if cumple:
                            puntos = st.number_input("Pts", 0.0, 10.0, puntos_prev, 0.5,
                                                   key=f"{tema_actual}_{equipo}_{juez_actual}_{categoria}_{criterio}_pts")
                            total_puntos += puntos
                        else:
                            puntos = 0
                            st.write("—")
                    
                    calificaciones_a_guardar.append({
                        'tema': tema_actual,
                        'equipo': equipo,
                        'juez': juez_actual,
                        'categoria': categoria,
                        'criterio': criterio,
                        'cumple': cumple,
                        'puntos': puntos
                    })
            
            st.markdown("---")
            col1, col2, col3 = st.columns([1,2,1])
            with col2:
                st.metric("🎯 TOTAL DE PUNTOS", f"{total_puntos:.1f}")
            
            if st.button("💾 Guardar Calificación", type="primary", use_container_width=True):
                progress_bar = st.progress(0)
                status = st.empty()
                
                with st.spinner("Guardando..."):
                    total_items = len(calificaciones_a_guardar)
                    for i, calif in enumerate(calificaciones_a_guardar):
                        guardar_calificacion(
                            calif['tema'], calif['equipo'], calif['juez'],
                            calif['categoria'], calif['criterio'],
                            calif['cumple'], calif['puntos']
                        )
                        progress_bar.progress((i + 1) / total_items)
                    
                    obtener_calificaciones.clear()
                    progress_bar.empty()
                    
                # Mostrar resumen
                st.success(f"""
                ✅ **Calificación Guardada**
                - Equipo: {equipo}
                - Total: {total_puntos:.1f} pts
                - Juez: {juez_actual}
                """)
                st.balloons()
                time.sleep(2)
                st.rerun()
        
        # RANKING
        else:
            st.header(f"📊 Ranking - {tema_actual}")
            
            df_ranking = calcular_ranking(tema_actual)
            
            if not df_ranking.empty:
                if len(df_ranking) >= 3:
                    col1, col2, col3 = st.columns(3)
                    with col2:
                        st.markdown("# 🥇")
                        st.subheader(df_ranking.iloc[0]['equipo'])
                        st.metric("", f"{df_ranking.iloc[0]['Promedio']:.2f}")
                    with col1:
                        st.markdown("# 🥈")
                        st.subheader(df_ranking.iloc[1]['equipo'])
                        st.metric("", f"{df_ranking.iloc[1]['Promedio']:.2f}")
                    with col3:
                        st.markdown("# 🥉")
                        st.subheader(df_ranking.iloc[2]['equipo'])
                        st.metric("", f"{df_ranking.iloc[2]['Promedio']:.2f}")
                st.subheader("Gráfico de Promedios")

                if not df_ranking.empty:
                    # Ordenar por promedio para que el degradado tenga sentido
                    df_ranking_sorted = df_ranking.sort_values('Promedio', ascending=False).reset_index(drop=True)
                    
                    # Crear un campo para el color basado en la posición o el promedio
                    # Esto asignará un color desde el verde (más alto) hasta el rojo (más bajo)
                    chart = alt.Chart(df_ranking_sorted).mark_bar().encode(
                        # Convertimos 'equipo' a nominal para que cada equipo sea una barra separada
                        y=alt.Y('equipo:N', sort='-x', title='Equipo'), # Sort='-x' ordena por 'Promedio' descendente
                        x=alt.X('Promedio:Q', title='Puntuación Promedio'),
                        color=alt.Color(
                            'Promedio:Q', # Colorea basado en el promedio
                            scale=alt.Scale(range=['red', 'orange', 'green']), # Degradado de rojo a verde
                            legend=alt.Legend(title="Promedio") # Leyenda para la escala de color
                        ),
                        # Añadir texto con el promedio en cada barra para mayor claridad
                        text=alt.Text('Promedio:Q', format='.2f') 
                    ).properties(
                        title=f"Promedio de Calificaciones por Equipo ({tema_actual})"
                    ).interactive() # Permite zoom y pan, puedes quitar .interactive() si quieres que sea completamente estático

                    # Mostrar la gráfica en Streamlit
                    st.altair_chart(chart, use_container_width=True)

                else:
                    st.warning("No hay calificaciones para mostrar en el gráfico.")        
                
                st.markdown("---")
                st.dataframe(df_ranking, use_container_width=True, hide_index=True)
            else:
                st.warning("No hay calificaciones aún")