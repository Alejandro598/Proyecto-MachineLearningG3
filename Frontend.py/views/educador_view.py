import streamlit as st
import pandas as pd
from api_client import client

def render_predict_risk():
    st.header("Predecir Riesgo de un Estudiante")
    estudiantes_data, status_code = client.get_estudiantes()
    if status_code == 200:
        estudiantes_map = {f"{e['nombre']} {e['apellido']} (Código: {e['codigo']})": e['codigo'] for e in estudiantes_data}
        selected_estudiante_display = st.selectbox("Selecciona un estudiante", list(estudiantes_map.keys()))

        if selected_estudiante_display:
            codigo_estudiante = estudiantes_map[selected_estudiante_display]
            if st.button("Predecir Riesgo"):
                st.info(f"Calculando riesgo para {selected_estudiante_display}...")
                result, pred_status = client.predecir_riesgo(codigo_estudiante)
                if pred_status == 200:
                    st.success("Predicción de Riesgo:")
                    st.write(f"**Nombre:** {result['nombre_estudiante']}")
                    st.write(f"**Código:** {result['codigo_estudiante']}")
                    st.write(f"**Asistencias Totales:** {result['asistencias_totales']}")
                    st.write(f"**Faltas Totales:** {result['faltas_totales']}")
                    st.markdown(f"**Riesgo ML (0-1):** <span style='font-size:20px; font-weight:bold; color:red;'>{result['riesgo_ml']:.2f}</span>", unsafe_allow_html=True)
                    st.write(f"**Riesgo por Reglas:** {result['riesgo_reglas'].capitalize()}")
                    st.write(f"**Estados Psicológicos Negativos:** {result['estados_negativos_psicologicos']}")
                    st.write(f"**Incidencias Registradas:** {result['incidencias_registradas']}")
                else:
                    st.error(result.get("detail", "Error al predecir el riesgo."))
    else:
        st.error("No se pudieron cargar los estudiantes para la predicción.")

def render_asistencia_form():
    st.header("Registrar Asistencia")
    estudiantes_data, status_code = client.get_estudiantes()
    if status_code == 200:
        estudiantes_map = {f"{e['nombre']} {e['apellido']} (Código: {e['codigo']})": e['codigo'] for e in estudiantes_data}
        selected_asistencia_estudiante_display = st.selectbox("Selecciona estudiante para asistencia", list(estudiantes_map.keys()), key="asist_sel")
        if selected_asistencia_estudiante_display:
            id_alumno = estudiantes_map[selected_asistencia_estudiante_display]
            estado_asistencia_options = {1: "Presente", 2: "Ausente", 3: "Tarde"}
            selected_estado_display = st.selectbox("Estado de Asistencia", list(estado_asistencia_options.values()))
            id_estado = [k for k, v in estado_asistencia_options.items() if v == selected_estado_display][0]

            if st.button("Registrar Asistencia"):
                result, status_code = client.record_asistencia(id_alumno, id_estado)
                if status_code == 201:
                    st.success(f"Asistencia registrada para {selected_asistencia_estudiante_display}.")
                else:
                    st.error(result.get("detail", "Error al registrar asistencia."))
        else:
            st.info("Por favor, agrega estudiantes primero.")
    else:
        st.error("No se pudieron cargar los estudiantes para registrar asistencia.")
