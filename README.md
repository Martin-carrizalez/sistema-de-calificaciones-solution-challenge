# 🏆 Sistema de Calificación | Solution Challenge 2025-B (CUGDL)

## 🌟 Resumen del Evento
El **Solution Challenge 2025-B** fue un vibrante evento de innovación del Centro Universitario de Guadalajara (**#CUGDL**), celebrado el **11 de septiembre de 2025**.

Nuestras y nuestros estudiantes demostraron cómo las matemáticas, la estadística y la innovación se convierten en **soluciones reales** para los retos del futuro.

🚀💡 ¡La creatividad de nuestra manada no tiene límites!

Agradecemos profundamente a las empresas e instituciones patrocinadoras por confiar en el talento universitario:
* **El Castillo de Tequila**
* **Grupo Collins**
* **CFE**
* **Clúster de Ingeniería Biomédica**
* **Coordinación General Estratégica de Seguridad del Estado de Jalisco**

---

## 💻 Sobre la Aplicación (Streamlit App)

Esta aplicación web fue desarrollada para simplificar y centralizar el proceso de **calificación y ranking** de los equipos participantes en el Solution Challenge 2025-B.

Construida con **Streamlit** y **Python**, permite a múltiples jueces evaluar simultáneamente a los equipos y ver el ranking en tiempo real.

### ✨ Características Principales

* **Configuración Rápida:** Permite configurar fácilmente el número de jueces y los equipos por tema al inicio de la competencia.
* **Doble Modo:** Interfaz separada para **Calificación** (enfocada en el juez) y **Ranking** (enfocada en la visualización de resultados).
* **Criterios Detallados:** Utiliza una matriz de criterios de evaluación (Formalidad, Habilidades Comunicativas, Dominio, Solution Value) para garantizar una evaluación justa y estructurada.
* **Podio Dinámico:** Muestra el top 3 de equipos con un atractivo formato de podio.
* **Exportación de Datos:** Genera un archivo **Excel (xlsx)** completo con el resumen general, rankings por tema y un detalle completo por criterio y juez.
* **Almacenamiento en Sesión:** Utiliza `st.session_state` para mantener los datos de calificación en memoria durante la sesión activa.

---

## 🛠️ Temas y Criterios de Evaluación

### 📚 Retos a Solucionar

Los equipos se enfrentaron a problemas reales propuestos por los patrocinadores:

| ID | Tema |
| :--- | :--- |
| **1** | SOP - Síndrome de Ovario Poliquístico |
| **2** | Interfaz IA El Castillo de Tequila |
| **3** | Pronóstico de Demanda Grupo Collins |
| **4** | Conflicto Vial López Mateos |

### 📝 Matriz de Calificación (Categorías Principales)

1.  **FORMALIDAD DE LA PRESENTACIÓN**
2.  **HABILIDADES COMUNICATIVAS**
3.  **DOMINIO DEL TEMA**
4.  **SOLUTION VALUE** (Énfasis en el razonamiento matemático, la interpretación y la innovación)

---

## 🚀 Cómo Ejecutar la Aplicación

Esta aplicación requiere Python y la librería **Streamlit** para correr.

### 1. Requisitos

Asegúrate de tener Python (3.8+) instalado.

### 2. Instalación de Dependencias

Ejecuta el siguiente comando para instalar las librerías necesarias:

```bash
pip install streamlit pandas openpyxl plotly

---
### 👨‍💻 Créditos

Sistema creado por el **QFB y LIACD Martín Ángel Carrizalez Piña**.
