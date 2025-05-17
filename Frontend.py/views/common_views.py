# views/common_views.py
import streamlit as st
import pandas as pd
from api_client import client 

def render_top_riesgo_section():
    st.header("Top Estudiantes con Mayor Riesgo de Deserción")
    if st.button("Mostrar Top Riesgo"):
        data, status_code = client.get_top_riesgo() 
        if status_code == 200:
            if data:
                df_top_riesgo = pd.DataFrame(data)
                df_top_riesgo.index = df_top_riesgo.index + 1 
                st.table(df_top_riesgo)
            else:
                st.info("No hay estudiantes con riesgo significativo calculado.")
        else:
            st.error(data.get("detail", "Error al obtener el top de riesgo."))