import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO
import plotly.graph_objects as go
import plotly.express as px

# Configuración de la página
st.set_page_config(page_title="Sistema de Calificación -Solution Challenge",page_icon="🏆", layout="wide")

# Temas del challenge
TEMAS = [
    "1. SOP - Síndrome de Ovario Poliquístico",
    "2. Interfaz IA El Castillo de Tequila",
    "3. Pronóstico de Demanda Grupo Collins",
    "4. Conflicto Vial López Mateos"
]

# Criterios de evaluación
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

# Función para generar Excel
def generar_excel():
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Hoja de resumen general
        resumen_general = []
        for tema in TEMAS:
            equipos_tema = st.session_state.equipos_por_tema[tema]
            for equipo in equipos_tema:
                key_calif = f"{tema}|{equipo}"
                puntos_jueces = []
                for juez in st.session_state.jueces:
                    total = 0
                    for categoria in CRITERIOS.keys():
                        for criterio in CRITERIOS[categoria]:
                            if criterio in st.session_state.calificaciones[key_calif]['jueces'][juez][categoria]:
                                total += st.session_state.calificaciones[key_calif]['jueces'][juez][categoria][criterio].get('puntos', 0)
                    puntos_jueces.append(total)
                promedio = sum(puntos_jueces) / len(puntos_jueces) if puntos_jueces else 0
                
                fila = {'Tema': tema, 'Equipo': equipo}
                for i, juez in enumerate(st.session_state.jueces):
                    fila[juez] = puntos_jueces[i]
                fila['Promedio'] = promedio
                resumen_general.append(fila)
        
        df_resumen = pd.DataFrame(resumen_general)
        df_resumen.to_excel(writer, sheet_name='Resumen General', index=False)
        
        # Hoja por cada tema con ranking
        for tema in TEMAS:
            equipos_tema = st.session_state.equipos_por_tema[tema]
            resultados_tema = []
            
            for equipo in equipos_tema:
                key_calif = f"{tema}|{equipo}"
                puntos_jueces = []
                for juez in st.session_state.jueces:
                    total = 0
                    for categoria in CRITERIOS.keys():
                        for criterio in CRITERIOS[categoria]:
                            if criterio in st.session_state.calificaciones[key_calif]['jueces'][juez][categoria]:
                                total += st.session_state.calificaciones[key_calif]['jueces'][juez][categoria][criterio].get('puntos', 0)
                    puntos_jueces.append(total)
                promedio = sum(puntos_jueces) / len(puntos_jueces) if puntos_jueces else 0
                
                resultado = {'Equipo': equipo}
                for i, juez in enumerate(st.session_state.jueces):
                    resultado[juez] = puntos_jueces[i]
                resultado['Promedio'] = promedio
                resultados_tema.append(resultado)
            
            resultados_tema = sorted(resultados_tema, key=lambda x: x['Promedio'], reverse=True)
            for i, res in enumerate(resultados_tema):
                res['Posición'] = i + 1
            
            df_tema = pd.DataFrame(resultados_tema)
            if not df_tema.empty:
                columnas = ['Posición', 'Equipo'] + st.session_state.jueces + ['Promedio']
                df_tema = df_tema[columnas]
                
                # Limpiar nombre para sheet
                sheet_name = tema.split('.')[1].strip()[:31]
                df_tema.to_excel(writer, sheet_name=sheet_name, index=False)
        
        # Hoja detallada con criterios
        detalles_completos = []
        for tema in TEMAS:
            equipos_tema = st.session_state.equipos_por_tema[tema]
            for equipo in equipos_tema:
                key_calif = f"{tema}|{equipo}"
                for juez in st.session_state.jueces:
                    for categoria in CRITERIOS.keys():
                        for criterio in CRITERIOS[categoria]:
                            if criterio in st.session_state.calificaciones[key_calif]['jueces'][juez][categoria]:
                                datos = st.session_state.calificaciones[key_calif]['jueces'][juez][categoria][criterio]
                                detalles_completos.append({
                                    'Tema': tema,
                                    'Equipo': equipo,
                                    'Juez': juez,
                                    'Categoría': categoria,
                                    'Criterio': criterio,
                                    'Cumple': 'Sí' if datos.get('cumple', False) else 'No',
                                    'Puntos': datos.get('puntos', 0)
                                })
        
        if detalles_completos:
            df_detalle = pd.DataFrame(detalles_completos)
            df_detalle.to_excel(writer, sheet_name='Detalle Completo', index=False)
    
    output.seek(0)
    return output

# Inicializar session_state
if 'equipos_por_tema' not in st.session_state:
    st.session_state.equipos_por_tema = {tema: [] for tema in TEMAS}
    
if 'jueces' not in st.session_state:
    st.session_state.jueces = []
    
if 'calificaciones' not in st.session_state:
    st.session_state.calificaciones = {}
    
if 'config_done' not in st.session_state:
    st.session_state.config_done = False

if 'tema_actual' not in st.session_state:
    st.session_state.tema_actual = TEMAS[0]

# Título principal
st.title("🏆 Sistema de Calificación - Solution Challenge 2025B")
st.markdown("---")

# CONFIGURACIÓN INICIAL
if not st.session_state.config_done:
    st.header("⚙️ Configuración Inicial")
    
    # Configurar jueces
    st.subheader("👥 Jueces")
    num_jueces = st.number_input("Número de jueces", min_value=3, max_value=5, value=3)
    jueces_nombres = []
    cols_jueces = st.columns(num_jueces)
    for i in range(num_jueces):
        with cols_jueces[i]:
            nombre = st.text_input(f"Juez {i+1}", value=f"Juez {i+1}", key=f"juez_{i}")
            jueces_nombres.append(nombre)
    
    st.markdown("---")
    
    # Configurar equipos por tema
    st.subheader("📚 Equipos por Tema")
    
    equipos_data = {}
    
    for tema in TEMAS:
        with st.expander(f"🎯 {tema}", expanded=True):
            num_equipos = st.number_input(
                f"Número de equipos para este tema", 
                min_value=1, 
                max_value=12, 
                value=2,
                key=f"num_{tema}"
            )
            
            equipos_tema = []
            cols = st.columns(min(3, num_equipos))
            
            for i in range(num_equipos):
                with cols[i % 3]:
                    nombre_equipo = st.text_input(
                        f"Equipo {i+1}",
                        value=f"Equipo {i+1}",
                        key=f"equipo_{tema}_{i}"
                    )
                    equipos_tema.append(nombre_equipo)
            
            equipos_data[tema] = equipos_tema
    
    st.markdown("---")
    
    if st.button("✅ Iniciar Competencia", type="primary", use_container_width=True):
        st.session_state.equipos_por_tema = equipos_data
        st.session_state.jueces = jueces_nombres
        st.session_state.config_done = True
        
        # Inicializar estructura de calificaciones
        for tema, equipos in equipos_data.items():
            for equipo in equipos:
                st.session_state.calificaciones[f"{tema}|{equipo}"] = {
                    'tema': tema,
                    'equipo': equipo,
                    'jueces': {
                        juez: {categoria: {} for categoria in CRITERIOS.keys()}
                        for juez in jueces_nombres
                    }
                }
        st.rerun()

# SISTEMA DE CALIFICACIÓN
else:
    # Sidebar para navegación
    st.sidebar.title("🎯 Navegación")
    
    # Selector de tema actual
    st.sidebar.markdown("### 📚 Tema Actual")
    tema_seleccionado = st.sidebar.selectbox(
        "Selecciona el tema que se está exponiendo:",
        TEMAS,
        index=TEMAS.index(st.session_state.tema_actual)
    )
    st.session_state.tema_actual = tema_seleccionado
    
    # Mostrar equipos del tema actual
    equipos_tema_actual = st.session_state.equipos_por_tema[tema_seleccionado]
    st.sidebar.info(f"📊 {len(equipos_tema_actual)} equipos en este tema")
    
    st.sidebar.markdown("---")
    
    # Selección de modo
    modo = st.sidebar.radio(
        "Modo de operación:",
        ["📝 Calificar", "📊 Ver Ranking"],
        key="modo_radio"
    )
    
    st.sidebar.markdown("---")

    # Botón de descarga en el sidebar
    st.sidebar.markdown("### 📥 Exportar Datos")
    if st.sidebar.button("📊 Descargar Excel", type="primary", use_container_width=True):
        excel_data = generar_excel()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        st.sidebar.download_button(
            label="⬇️ Descargar Archivo",
            data=excel_data,
            file_name=f"calificaciones_challenge_{timestamp}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
        st.sidebar.success("✅ Excel generado!")
    
    st.sidebar.markdown("---")
    
    # Botón para reiniciar
    if st.sidebar.button("🔄 Reiniciar Sistema", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
    
    # Información de todos los temas
    with st.sidebar.expander("📋 Resumen de Equipos"):
        for tema in TEMAS:
            st.markdown(f"**{tema}**")
            equipos = st.session_state.equipos_por_tema[tema]
            for eq in equipos:
                st.markdown(f"- {eq}")
    
    # ========== MODO CALIFICAR ==========
    if modo == "📝 Calificar":
        st.header("📝 Panel de Calificación")
        
        # Mostrar tema actual destacado
        st.info(f"🎯 **Tema Actual:** {tema_seleccionado}")
        
        # Selección de juez y equipo
        col1, col2 = st.columns(2)
        
        with col1:
            juez_actual = st.selectbox("👤 Selecciona tu nombre (Juez):", st.session_state.jueces)
        
        with col2:
            equipo_actual = st.selectbox(
                "🎪 Equipo a calificar:", 
                equipos_tema_actual
            )
        
        st.markdown("---")
        
        # Formulario de calificación
        st.subheader(f"Evaluando: **{equipo_actual}** | Juez: **{juez_actual}**")
        
        key_calif = f"{tema_seleccionado}|{equipo_actual}"
        total_puntos = 0
        
        for categoria, criterios in CRITERIOS.items():
            st.markdown(f"### 📋 {categoria}")
            
            for criterio in criterios:
                col1, col2, col3 = st.columns([4, 1, 1.5])
                
                with col1:
                    st.write(f"• {criterio}")
                
                with col2:
                    cumple = st.checkbox(
                        "✓ C",
                        key=f"{juez_actual}_{key_calif}_{categoria}_{criterio}_cumple",
                        value=st.session_state.calificaciones[key_calif]['jueces'][juez_actual][categoria].get(criterio, {}).get('cumple', False)
                    )
                
                with col3:
                    if cumple:
                        puntos = st.number_input(
                            "Puntos (0-10)",
                            min_value=0.0,
                            max_value=10.0,
                            step=0.5,
                            key=f"{juez_actual}_{key_calif}_{categoria}_{criterio}_puntos",
                            value=st.session_state.calificaciones[key_calif]['jueces'][juez_actual][categoria].get(criterio, {}).get('puntos', 0.0)
                        )
                        total_puntos += puntos
                    else:
                        puntos = 10.0
                        st.write("—")
                
                # Guardar en session_state
                st.session_state.calificaciones[key_calif]['jueces'][juez_actual][categoria][criterio] = {
                    'cumple': cumple,
                    'puntos': puntos
                }
            
            st.markdown("---")
        
        # Mostrar total
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.metric("🎯 TOTAL DE PUNTOS", f"{total_puntos:.1f}", delta=None)
        
        # Observaciones
        st.markdown("---")
        st.subheader("📝 Observaciones (Opcional)")
        observaciones = st.text_area(
            "Comentarios adicionales:",
            key=f"obs_{juez_actual}_{key_calif}",
            height=100,
            placeholder="Escribe aquí cualquier observación relevante sobre la presentación..."
        )
        
        if st.button("💾 Guardar Calificación", type="primary", use_container_width=True):
            st.success(f"✅ Calificación guardada para **{equipo_actual}** por **{juez_actual}**")
            st.balloons()
    
    # ========== MODO RANKING ==========
    else:
        st.header(f"📊 Ranking - {tema_seleccionado}")
        
        # Calcular ranking solo para el tema actual
        equipos_tema_actual = st.session_state.equipos_por_tema[tema_seleccionado]
        resultados = []
        
        for equipo in equipos_tema_actual:
            key_calif = f"{tema_seleccionado}|{equipo}"
            puntos_por_juez = {}
            
            for juez in st.session_state.jueces:
                total = 0
                for categoria in CRITERIOS.keys():
                    for criterio in CRITERIOS[categoria]:
                        calif = st.session_state.calificaciones[key_calif]['jueces'][juez][categoria]
                        if criterio in calif and calif[criterio].get('cumple', False):
                            total += calif[criterio].get('puntos', 0)
                puntos_por_juez[juez] = total
            
            promedio = sum(puntos_por_juez.values()) / len(puntos_por_juez) if puntos_por_juez else 0
            
            resultado = {
                'Posición': 0,
                'Equipo': equipo,
                'Promedio': promedio,
                **puntos_por_juez
            }
            
            resultados.append(resultado)
        
        # Ordenar por promedio
        resultados = sorted(resultados, key=lambda x: x['Promedio'], reverse=True)
        
        # Asignar posiciones
        for i, resultado in enumerate(resultados):
            resultado['Posición'] = i + 1
        
        # Mostrar podio si hay al menos 3 equipos
        if len(resultados) >= 3:
            st.markdown("### 🏆 Podio")
            col1, col2, col3 = st.columns(3)
            
            with col2:
                st.markdown("<h1 style='text-align: center;'>🥇</h1>", unsafe_allow_html=True)
                st.markdown(f"<h3 style='text-align: center;'>{resultados[0]['Equipo']}</h3>", unsafe_allow_html=True)
                st.markdown(f"<h2 style='text-align: center; color: gold;'>{resultados[0]['Promedio']:.2f} pts</h2>", unsafe_allow_html=True)
            
            with col1:
                st.markdown("<h1 style='text-align: center;'>🥈</h1>", unsafe_allow_html=True)
                st.markdown(f"<h4 style='text-align: center;'>{resultados[1]['Equipo']}</h4>", unsafe_allow_html=True)
                st.markdown(f"<h3 style='text-align: center; color: silver;'>{resultados[1]['Promedio']:.2f} pts</h3>", unsafe_allow_html=True)
            
            with col3:
                st.markdown("<h1 style='text-align: center;'>🥉</h1>", unsafe_allow_html=True)
                st.markdown(f"<h4 style='text-align: center;'>{resultados[2]['Equipo']}</h4>", unsafe_allow_html=True)
                st.markdown(f"<h3 style='text-align: center; color: #CD7F32;'>{resultados[2]['Promedio']:.2f} pts</h3>", unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Tabla completa
        st.markdown("### 📋 Tabla Completa de Posiciones")
        df = pd.DataFrame(resultados)
        
        # Reordenar columnas
        columnas_ordenadas = ['Posición', 'Equipo'] + st.session_state.jueces + ['Promedio']
        df = df[columnas_ordenadas]
        
        # Formatear y mostrar
        st.dataframe(
            df.style.format({
                'Promedio': '{:.2f}',
                **{juez: '{:.2f}' for juez in st.session_state.jueces}
            }),
            use_container_width=True,
            height=min(400, len(resultados) * 50 + 100)
        )
        
        st.markdown("---")
        
        # Gráficos modernos con Plotly
        col_graph1, col_graph2 = st.columns(2)
        
        with col_graph1:
            st.markdown("### 📊 Promedio por Equipo")
            # Gráfico de barras horizontal con colores degradados
            fig_bar = go.Figure()
            
            colors = px.colors.sequential.Viridis
            color_scale = [colors[int(i * (len(colors)-1) / (len(df)-1))] for i in range(len(df))]
            
            fig_bar.add_trace(go.Bar(
                y=df['Equipo'],
                x=df['Promedio'],
                orientation='h',
                marker=dict(
                    color=df['Promedio'],
                    colorscale='Viridis',
                    showscale=False,
                    line=dict(color='white', width=2)
                ),
                text=df['Promedio'].round(2),
                textposition='outside',
                textfont=dict(size=14, color='white'),
                hovertemplate='<b>%{y}</b><br>Promedio: %{x:.2f}<extra></extra>'
            ))
            
            fig_bar.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white', size=12),
                xaxis=dict(
                    showgrid=True,
                    gridcolor='rgba(255,255,255,0.1)',
                    title='Puntos',
                    range=[0, max(df['Promedio']) * 1.15]
                ),
                yaxis=dict(
                    showgrid=False,
                    categoryorder='total ascending',
                    title=''
                ),
                height=max(300, len(df) * 50),
                margin=dict(l=10, r=10, t=10, b=10)
            )
            
            st.plotly_chart(fig_bar, use_container_width=True)
        
        # Ver ranking de otros temas
        st.markdown("---")
        st.markdown("### 🔍 Ver Ranking de Otros Temas")
        
        otros_temas = [t for t in TEMAS if t != tema_seleccionado]
        tema_consulta = st.selectbox("Selecciona otro tema para ver su ranking:", otros_temas)
        
        if st.button("Ver Ranking", type="secondary"):
            st.session_state.tema_actual = tema_consulta
            st.rerun()

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray; padding: 20px;'>
        <strong>Sistema de Calificación Solution Challenge 2025B</strong><br>
        ⚠️ Mantén la app abierta durante toda la competencia para no perder los datos
    </div>
    """,
    unsafe_allow_html=True
)