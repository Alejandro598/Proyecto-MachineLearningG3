import streamlit as st
import pandas as pd
from api_client import client

def render_admin_management():
    st.title("Módulo de Administrador")
    st.header("Gestión de usuarios")

    st.subheader("Registrar Nuevo Usuario")
    with st.form("new_estudiante_form"):
        nombre_new = st.text_input("Nombre")
        apellido_new = st.text_input("Apellido")
        telefono_new = st.text_input("Teléfono")
        submitted = st.form_submit_button("Crear usuario")
        if submitted:
            result, status_code = client.create_estudiante(nombre_new, apellido_new, telefono_new)
            if status_code == 201:
                st.success(f"usuario {result['nombre']} {result['apellido']} (Código: {result['codigo']}) creado exitosamente.")
                st.rerun()
            else:
                st.error(result.get("detail", "Error al crear estudiante."))

    st.subheader("Lista de Usuarios Registrados")
    estudiantes_data, status_code = client.get_estudiantes()
    if status_code == 200:
        if estudiantes_data:
            df_estudiantes = pd.DataFrame(estudiantes_data)
            st.dataframe(df_estudiantes)

            st.subheader("Editar o un usuario")
            estudiantes_map = {f"{e['nombre']} {e['apellido']} (Código: {e['codigo']})": e['codigo'] for e in estudiantes_data}
            selected_estudiante_edit_delete = st.selectbox("Selecciona un usuario para editar/eliminar", list(estudiantes_map.keys()))

            if selected_estudiante_edit_delete:
                codigo_selected = estudiantes_map[selected_estudiante_edit_delete]
                current_estudiante_data, get_status = client.get_estudiante_by_codigo(codigo_selected)
                if get_status == 200:
                    current_nombre = current_estudiante_data['nombre']
                    current_apellido = current_estudiante_data['apellido']
                    current_telefono = current_estudiante_data['telefono']
                else:
                    st.warning(f"No se pudieron cargar los datos actuales del estudiante. {current_estudiante_data.get('detail', '')}")
                    current_nombre = ""
                    current_apellido = ""
                    current_telefono = ""

                col1, col2 = st.columns(2)
                with col1:
                    with st.form("edit_estudiante_form"):
                        st.write(f"Editar usuario con Código: {codigo_selected}")
                        nombre_edit = st.text_input("Nuevo Nombre", value=current_nombre, key=f"edit_nombre_{codigo_selected}")
                        apellido_edit = st.text_input("Nuevo Apellido", value=current_apellido, key=f"edit_apellido_{codigo_selected}")
                        telefono_edit = st.text_input("Nuevo Teléfono", value=current_telefono, key=f"edit_telefono_{codigo_selected}")
                        submitted_edit = st.form_submit_button("Actualizar Estudiante")
                        if submitted_edit:
                            result, status_code = client.update_estudiante(codigo_selected, nombre_edit, apellido_edit, telefono_edit)
                            if status_code == 200:
                                st.success(f"Estudiante con Código {codigo_selected} actualizado.")
                                st.rerun()
                            else:
                                st.error(result.get("detail", "Error al actualizar estudiante."))
                with col2:
                    st.write(f"Eliminar usuario con Código: {codigo_selected}")
                    if st.button("Eliminar Estudiante", key=f"delete_btn_{codigo_selected}"):
                        confirm = st.checkbox(f"Confirmar eliminación de {selected_estudiante_edit_delete}", key=f"confirm_del_{codigo_selected}")
                        if confirm:
                            status_code = client.delete_estudiante(codigo_selected)
                            if status_code == 204:
                                st.success(f"Estudiante con Código {codigo_selected} eliminado.")
                                st.rerun()
                            else:
                                st.error(f"Error al eliminar estudiante (Código HTTP: {status_code}). Puede haber registros relacionados.")
        else:
            st.info("No hay estudiantes registrados. ¡Agrega uno primero!")
    else:
        st.error("Error al cargar la lista de estudiantes.")

def render_asistencia_management():
    st.title("Gestión de Asistencia (Admin)")
    st.info("Aquí puedes implementar la vista para que el administrador gestione la asistencia.")

def render_estado_psicologico_management():
    st.title("Gestión de Estados Psicológicos (Admin)")
    st.info("Aquí puedes implementar la vista para que el administrador gestione los estados psicológicos.")

def render_incidencias_management():
    st.title("Gestión de Incidencias (Admin)")
    st.info("Aquí puedes implementar la vista para que el administrador gestione las incidencias.")
