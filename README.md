🏆 Sistema de Calificación | Solution Challenge 2025-B (CUGDL)

🌟 Resumen del Evento

El Solution Challenge 2025-B fue un vibrante evento de innovación del Centro Universitario de Guadalajara (#CUGDL), celebrado el 11 de septiembre de 2025.

Nuestras y nuestros estudiantes demostraron cómo las matemáticas, la estadística y la innovación se convierten en soluciones reales para los retos del futuro.

🚀💡 ¡La creatividad de nuestra manada no tiene límites!

Agradecemos profundamente a las empresas e instituciones patrocinadoras por confiar en el talento universitario:

El Castillo de Tequila

Grupo Collins

CFE

Clúster de Ingeniería Biomédica

Coordinación General Estratégica de Seguridad del Estado de Jalisco

💻 Sobre la Aplicación

Esta aplicación web fue desarrollada para simplificar y centralizar el proceso de calificación y ranking de los equipos participantes en el Solution Challenge 2025-B.

Construida con Streamlit, Python y una base de datos Supabase, permite a múltiples jueces evaluar simultáneamente a los equipos y visualizar el ranking en tiempo real.

✨ Características Principales

Autenticación Segura: Manejo de credenciales de juez y administrador a través del sistema de st.secrets para garantizar la seguridad de acceso.

Almacenamiento Persistente: Utiliza Supabase como backend para guardar todas las calificaciones de forma segura y persistente.

Doble Modo: Interfaz separada para Calificación (enfocada en el juez) y Ranking (enfocada en la visualización de resultados).

Gráficos Profesionales: Visualización dinámica del ranking con gráficos de barra degradados usando Altair.

Podio Dinámico: Muestra el top 3 de equipos con un atractivo formato de podio.

Exportación de Datos: Genera un archivo Excel (xlsx) completo con el resumen general, rankings por tema y un detalle completo por criterio y juez.

Criterios Detallados: Utiliza una matriz de criterios de evaluación (Formalidad, Habilidades Comunicativas, Dominio, Solution Value) para garantizar una evaluación justa y estructurada.

🛠️ Temas y Criterios de Evaluación

📚 Retos a Solucionar

ID

Tema

1

SOP - Síndrome de Ovario Poliquístico

2

Interfaz IA El Castillo de Tequila

3

Pronóstico de Demanda Grupo Collins

4

Conflicto Vial López Mateos

📝 Matriz de Calificación (Categorías Principales)

FORMALIDAD DE LA PRESENTACIÓN

HABILIDADES COMUNICATIVAS

DOMINIO DEL TEMA

SOLUTION VALUE (Énfasis en el razonamiento matemático, la interpretación y la innovación)

🚀 Cómo Ejecutar la Aplicación

Esta aplicación requiere Python y las librerías necesarias para correr.

1. Requisitos

Asegúrate de tener Python (3.8+) instalado.

2. Instalación de Dependencias

Ejecuta el siguiente comando para instalar las librerías necesarias (incluyendo Supabase y Altair):

pip install streamlit pandas openpyxl supabase altair


3. Configuración de Credenciales

Para que la aplicación funcione y se conecte a Supabase, debes crear un archivo llamado .streamlit/secrets.toml en el directorio raíz de tu proyecto. Este archivo NUNCA debe subirse al repositorio.

El contenido debe seguir la siguiente estructura, reemplazando los valores por tus credenciales de Supabase y las contraseñas que definiste:

supabase_url = "TU_URL_DE_SUPABASE" 
supabase_key = "TU_CLAVE_PUBLISHABLE_DE_SUPABASE" 

[admin]
password = "TU_CONTRASEÑA_SECRETA_DE_ADMIN" 

[passwords]
"Juez 1" = "clave1"
"Juez 2" = "clave2"
# ... y el resto de los jueces ...


4. Ejecución

Una vez que tengas el archivo secrets.toml, puedes ejecutar la aplicación con:

streamlit run appsupabase.py


📜 Licencia

Este proyecto está bajo la Licencia MIT (Massachusetts Institute of Technology). Puedes usar, copiar, modificar, fusionar, publicar, distribuir, sublicenciar y/o vender copias del software con la única condición de incluir el copyright original y la nota de permiso.

Copyright (c) 2025 Martín Ángel Carrizalez Piña

👨‍💻 Créditos

Sistema creado por el QFB y LIACD Martín Ángel Carrizalez Piña.
