# 🏆 Sistema de Calificación | Solution Challenge 2025-B (CUGDL)

![Streamlit](https://img.shields.io/badge/Framework-Streamlit-red)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![License: MIT](https://img.shields.io/badge/License-MIT-green)
![Supabase](https://img.shields.io/badge/Backend-Supabase-3FCF8E)

---

## 🌟 Resumen del Evento

El **Solution Challenge 2025-B** fue un vibrante evento de innovación del **Centro Universitario de Guadalajara (#CUGDL)**, celebrado el **11 de septiembre de 2025**.

Nuestras y nuestros estudiantes demostraron cómo las **matemáticas**, la **estadística** y la **innovación** se convierten en soluciones reales para los retos del futuro.

> 🚀💡 ¡La creatividad de nuestra manada no tiene límites!

Agradecemos profundamente a las empresas e instituciones patrocinadoras por confiar en el talento universitario:

- 🏰 El Castillo de Tequila  
- 🧱 Grupo Collins  
- ⚡ CFE  
- 🧬 Clúster de Ingeniería Biomédica  
- 🛡️ Coordinación General Estratégica de Seguridad del Estado de Jalisco  

---

## 💻 Sobre la Aplicación

Esta aplicación web fue desarrollada para **simplificar y centralizar el proceso de calificación y ranking** de los equipos participantes en el Solution Challenge 2025-B.

Construida con **Streamlit**, **Python** y **Supabase**, permite que múltiples jueces evalúen simultáneamente a los equipos y visualicen el **ranking en tiempo real**.

---

## ✨ Características Principales

- 🔐 **Autenticación Segura:**  
  Manejo de credenciales de juez y administrador mediante `st.secrets` para garantizar la seguridad de acceso.

- 🧩 **Almacenamiento Persistente:**  
  Uso de **Supabase** como backend para guardar todas las calificaciones de forma segura y persistente.

- 🧭 **Doble Modo:**  
  Interfaz separada para **Calificación (jueces)** y **Ranking (visualización de resultados)**.

- 📊 **Gráficos Profesionales:**  
  Visualización dinámica del ranking con **gráficos de barra degradados** usando **Altair**.

- 🥇 **Podio Dinámico:**  
  Muestra el **Top 3 de equipos** con un atractivo formato de podio.

- 📤 **Exportación de Datos:**  
  Genera un archivo **Excel (.xlsx)** con:
  - Resumen general  
  - Rankings por tema  
  - Detalle completo por criterio y juez  

- 🧮 **Criterios Detallados:**  
  Matriz estructurada de evaluación:
  - **Formalidad**
  - **Habilidades Comunicativas**
  - **Dominio del Tema**
  - **Solution Value** (énfasis en razonamiento matemático, interpretación e innovación)

---

## 🛠️ Temas y Criterios de Evaluación

### 📚 Retos a Solucionar

| ID | Tema |
|----|------|
| 1 | SOP - Síndrome de Ovario Poliquístico |
| 2 | Interfaz IA El Castillo de Tequila |
| 3 | Pronóstico de Demanda Grupo Collins |
| 4 | Conflicto Vial López Mateos |

### 📝 Matriz de Calificación

- **FORMALIDAD DE LA PRESENTACIÓN**  
- **HABILIDADES COMUNICATIVAS**  
- **DOMINIO DEL TEMA**  
- **SOLUTION VALUE**  
  _(Énfasis en el razonamiento matemático, la interpretación y la innovación)_

---

## 🚀 Cómo Ejecutar la Aplicación

### 1️⃣ Requisitos

Asegúrate de tener instalado:

- **Python 3.8+**

### 2️⃣ Instalación de Dependencias

Ejecuta el siguiente comando:

```bash
pip install streamlit pandas openpyxl supabase altair
3️⃣ Configuración de Credenciales
Crea un archivo llamado:

bash
Copiar código
.streamlit/secrets.toml
Este archivo no debe subirse al repositorio.
Debe contener tus credenciales de Supabase y contraseñas personalizadas.

Ejemplo de estructura:
toml
Copiar código
supabase_url = "TU_URL_DE_SUPABASE"
supabase_key = "TU_CLAVE_PUBLISHABLE_DE_SUPABASE"

[admin]
password = "TU_CONTRASEÑA_SECRETA_DE_ADMIN"

[passwords]
"Juez 1" = "clave1"
"Juez 2" = "clave2"
# ... agrega más jueces si es necesario ...
4️⃣ Ejecución
Una vez configurado, ejecuta:

bash
Copiar código
streamlit run appsupabase.py
La aplicación se abrirá automáticamente en tu navegador local.

📜 Licencia
Este proyecto está bajo la Licencia MIT.
Puedes usar, copiar, modificar, fusionar, publicar, distribuir, sublicenciar y/o vender copias del software con la condición de incluir el copyright.

css
Copiar código
Copyright (c) 2025
Martín Ángel Carrizalez Piña
👨‍💻 Créditos
Sistema desarrollado por:
QFB y LIACD Martín Ángel Carrizalez Piña

"La ciencia, la creatividad y la colaboración universitaria son la fórmula de la innovación."
— Solution Challenge 2025-B, CUGDL
