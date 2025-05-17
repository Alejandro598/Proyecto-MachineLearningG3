import streamlit as st
from views import login, admin_view, educador_view, auxiliar_view, common_views

def main():
    if "token" not in st.session_state or not st.session_state["token"]:
        login.login_page()
    else:
        st.sidebar.title("Menú Principal")
        st.sidebar.write(f"Bienvenido, {st.session_state.get('username', 'Usuario')} ({st.session_state['role']})")

        if st.sidebar.button("Cerrar Sesión"):
            st.session_state.clear()
            st.rerun()

        role = st.session_state["role"]

        pages = {}
        if role == "Administrador":
            pages = {
                "Gestión de Estudiantes": admin_view.render_admin_management,
                "Top Riesgo": common_views.render_top_riesgo_section,
                "Gestión de Asistencia (Admin)": admin_view.render_asistencia_management,
                "Gestión de Estados Psicológicos (Admin)": admin_view.render_estado_psicologico_management,
                "Gestión de Incidencias (Admin)": admin_view.render_incidencias_management,
            }
        elif role == "Auxiliar":
            pages = {
                "Reportar Incidencia": auxiliar_view.render_incidencia_form,
                "Ver Incidencias Registradas": auxiliar_view.render_incidencias_list,
                "Listar Estados Psicológicos": auxiliar_view.render_estado_psicologico_list,
                "Top Riesgo (Mayor)": common_views.render_top_riesgo_section,
                "Top Riesgo (Menor)": auxiliar_view.render_lowest_risk_students_list,
            }
        elif role == "Educador":
            pages = {
                "Predecir Riesgo": educador_view.render_predict_risk,
                "Registrar Asistencia": educador_view.render_asistencia_form,
                "Top Riesgo": common_views.render_top_riesgo_section,
            }
        else:
            st.error("Rol no reconocido. Por favor, contacta al administrador.")
            st.session_state.clear()
            st.rerun()
            return

        selected_page = st.sidebar.radio("Navegar", list(pages.keys()))

        if selected_page:
            pages[selected_page]()

if __name__ == "__main__":
    main()
