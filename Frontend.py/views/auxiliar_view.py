import streamlit as st
import pandas as pd
from api_client import client
from utils.helpers import format_datetime_for_display

def render_lowest_risk_students_list():
    st.title("Módulo de Auxiliares")
    st.header("Estudiantes con Menor Riesgo de Deserción")

    num_students = st.slider("Número de estudiantes a mostrar", min_value=1, max_value=20, value=5, key="num_lowest_risk")

    if st.button(f"Mostrar Top {num_students} Estudiantes de Menor Riesgo", key="btn_show_lowest_risk"):
        estudiantes_riesgo_data, status_code = client.get_top_n_lowest_risk_students(n=num_students)

        if status_code == 200:
            if estudiantes_riesgo_data:
                df_lowest_risk = pd.DataFrame(estudiantes_riesgo_data)
                if 'puntaje' in df_lowest_risk.columns:
                    df_lowest_risk_sorted = df_lowest_risk.sort_values(by='puntaje', ascending=True)
                    st.subheader(f"Top {num_students} Estudiantes con Menor Riesgo")
                    display_cols = ['nombre']
                    if 'apellido' in df_lowest_risk_sorted.columns:
                        display_cols.append('apellido')
                    if 'codigo' in df_lowest_risk_sorted.columns:
                        display_cols.append('codigo')
                    display_cols.append('puntaje')
                    st.dataframe(df_lowest_risk_sorted[display_cols])
                else:
                    st.warning("La respuesta de la API no contiene la columna 'puntaje'.")
            else:
                st.info("No hay datos disponibles.")
        else:
            st.error(f"Error al cargar estudiantes: {estudiantes_riesgo_data.get('detail', 'Desconocido')}")

    st.sidebar.subheader("Puntaje de Riesgo: Interpretación")
    st.sidebar.markdown(
        """
        El **Puntaje de Riesgo de Deserción** estima la probabilidad de que un estudiante abandone sus estudios.

        * **0 - 30:** Riesgo **Bajo**
        * **31 - 60:** Riesgo **Moderado**
        * **61 - 100:** Riesgo **Alto**
        """
    )

def render_estado_psicologico_list():
    st.title("Módulo de Auxiliares")
    st.header("Ver Estados Psicológicos Registrados")

    if st.button("Actualizar Estados Psicológicos", key="btn_actualizar_ep"):
        estados_psicologicos, status_code = client.get_all_estados_psicologicos()
        if status_code == 200:
            if estados_psicologicos:
                df_estados = pd.DataFrame(estados_psicologicos)
                if 'fecha_y_hora_registro' in df_estados.columns:
                    df_estados['fecha_y_hora_registro'] = df_estados['fecha_y_hora_registro'].apply(format_datetime_for_display)
                st.dataframe(df_estados)
            else:
                st.info("No hay estados registrados.")
        else:
            st.error(f"Error al obtener estados: {estados_psicologicos.get('detail', 'Desconocido')}")

def render_record_estado_psicologico_form():
    st.title("Módulo de Auxiliares")

def render_incidencia_form():
    st.title("Módulo de Auxiliares")
    st.header("Reportar Incidencia")

    estudiantes_data, status_code = client.get_estudiantes()
    if status_code == 200:
        if estudiantes_data:
            estudiantes_map = {f"{e['nombre']} {e['apellido']} (Código: {e['codigo']})": e['codigo'] for e in estudiantes_data}
            estudiantes_map_with_none = {"Ninguno": None}
            estudiantes_map_with_none.update(estudiantes_map)

            incidencia_nombre = st.text_input("Nombre de la Incidencia")
            incidencia_descripcion = st.text_area("Descripción")
            
            selected_afectado_display = st.selectbox("Estudiante Afectado", list(estudiantes_map.keys()), key="inc_afectado")
            selected_reportado_display = st.selectbox("Estudiante que Reporta (Opcional)", list(estudiantes_map_with_none.keys()), key="inc_reportado")

            if selected_afectado_display:
                id_afectado = estudiantes_map[selected_afectado_display]
                id_reportado = estudiantes_map_with_none[selected_reportado_display]

                if st.button("Registrar Incidencia"):
                    if incidencia_nombre and incidencia_descripcion:
                        result, status_code = client.create_incidencia(incidencia_nombre, incidencia_descripcion, id_afectado, id_reportado)
                        if status_code == 201:
                            st.success(f"Incidencia '{incidencia_nombre}' registrada.")
                        else:
                            st.error(result.get("detail", "Error al registrar incidencia."))
                    else:
                        st.warning("El nombre y la descripción no pueden estar vacíos.")
            else:
                st.info("Selecciona un estudiante afectado.")
        else:
            st.info("No hay estudiantes registrados.")
    else:
        st.error("No se pudieron cargar los estudiantes.")

def render_incidencias_list():
    st.title("Módulo de Auxiliares")
    st.header("Ver Incidencias Registradas")
    
    if st.button("Actualizar Incidencias", key="btn_actualizar_incidencias"):
        incidencias, status_code = client.get_incidencias()
        if status_code == 200:
            if incidencias:
                df_incidencias = pd.DataFrame(incidencias)
                if 'fecha_y_hora_reporte' in df_incidencias.columns:
                    df_incidencias['fecha_y_hora_reporte'] = df_incidencias['fecha_y_hora_reporte'].apply(format_datetime_for_display)
                st.dataframe(df_incidencias)
            else:
                st.info("No hay incidencias registradas.")
        else:
            st.error(f"Error al obtener incidencias: {incidencias.get('detail', 'Desconocido')}")

def render_desercion_riesgo_list():
    st.title("Módulo de Auxiliares")
    st.header("Estudiantes con Mayor Riesgo de Deserción")

    if st.button("Mostrar Top Riesgo", key="btn_riesgo_desercion"):
        estudiantes_riesgo_data, status_code = client.get_top_riesgo()

        if status_code == 200:
            if estudiantes_riesgo_data:
                df_riesgo = pd.DataFrame(estudiantes_riesgo_data)
                score_col = None
                if 'riesgo_desercion_score' in df_riesgo.columns:
                    score_col = 'riesgo_desercion_score'
                elif 'puntaje' in df_riesgo.columns:
                    score_col = 'puntaje'
                
                if score_col:
                    df_riesgo_sorted = df_riesgo.sort_values(by=score_col, ascending=False).head(10)
                    st.subheader("Top 10 Estudiantes con Mayor Riesgo")
                    display_cols = ['nombre']
                    if 'apellido' in df_riesgo_sorted.columns:
                        display_cols.append('apellido')
                    if 'codigo' in df_riesgo_sorted.columns:
                        display_cols.append('codigo')
                    display_cols.append(score_col)
                    st.dataframe(df_riesgo_sorted[display_cols])
                else:
                    st.warning("No se encontró la columna del puntaje.")
            else:
                st.info("No hay datos disponibles.")
        else:
            st.error(f"Error al cargar estudiantes: {estudiantes_riesgo_data.get('detail', 'Desconocido')}")

    st.sidebar.subheader("Explicación del Puntaje de Riesgo")
    st.sidebar.markdown(
        """
        El **Puntaje de Riesgo de Deserción** estima la probabilidad de que un estudiante abandone sus estudios.

        * **0 - 30:** Riesgo **Bajo**
        * **31 - 60:** Riesgo **Moderado**
        * **61 - 100:** Riesgo **Alto**

        Un puntaje más alto indica mayor riesgo.
        """
    )
