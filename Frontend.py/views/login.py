import streamlit as st
from api_client import client
from PIL import Image
import requests
from io import BytesIO

def load_image_from_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return Image.open(BytesIO(response.content))
    except requests.exceptions.RequestException as e:
        st.error(f"Error al cargar la imagen desde {url}: {e}")
        return None

def login_page():
    st.set_page_config(layout="wide", initial_sidebar_state="collapsed", page_title="EDUAnalytics Login")

    st.markdown(
        """
        <style>
        .main-header {
            text-align: center;
            font-size: 3.5em;
            color: #E0E0E0;
            margin-bottom: 0.3em;
            font-weight: bold;
            letter-spacing: 1px;
        }
        .subheader {
            text-align: center;
            font-size: 1.5em;
            color: #B0B0B0;
            margin-bottom: 2em;
            font-weight: normal;
        }
        .login-container {
            background-color: #2C2F33;
            padding: 40px;
            border-radius: 15px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
            border: 1px solid #4A4A4A;
            width: 100%;
        }
        h2 {
            text-align: center;
            color: #E0E0E0;
            margin-bottom: 1.5em;
            font-size: 2em;
        }
        .stButton button {
            background-color: #28A745;
            color: white;
            padding: 12px 25px;
            border-radius: 8px;
            border: none;
            font-size: 1.1em;
            font-weight: bold;
            width: 100%;
            margin-top: 20px;
            transition: background-color 0.3s ease;
        }
        .stButton button:hover {
            background-color: #218838;
            cursor: pointer;
        }
        .stTextInput label, .stTextInput input {
            color: #E0E0E0;
            font-size: 1.05em;
        }
        .stTextInput div:has(input) {
            background-color: #3A3F44;
            border-radius: 8px;
            border: 1px solid #5A5A5A;
            padding: 8px 12px;
            color: #E0E0E0;
        }
        .stTextInput div:has(input)::placeholder {
            color: #A0A0A0;
        }
        .stTextInput div:has(input):focus-within {
            border-color: #2F80ED;
            box-shadow: 0 0 0 0.1rem rgba(47, 128, 237, 0.25);
        }
        .stAlert {
            border-radius: 8px;
            margin-top: 15px;
        }
        p {
            color: #B0B0B0;
            text-align: center;
            font-size: 0.9em;
        }
        a {
            color: #2F80ED;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.title("EDUAnalytics🔍")
    st.markdown("<h3>sistema web de alerta para prevención de riesgo de deserción escolar</h3>", unsafe_allow_html=True)

    col_image, col_form_wrapper = st.columns([2.5, 1.5])

    with col_image:
        image_url = "https://www.webyempresas.com/wp-content/uploads/2021/01/an%C3%A1lisis-del-entorno-696x379.jpg"
        image = load_image_from_url(image_url)
        if image:
            st.image(image, use_container_width=True)

    with col_form_wrapper:
        inner_col_left, inner_col_form, inner_col_right = st.columns([0.7, 2, 0.7])

        with inner_col_form:
            st.markdown("<div class='login-container'>", unsafe_allow_html=True)
            st.markdown("<h2>INICIAR SESION</h2>", unsafe_allow_html=True)

            username = st.text_input("Usuario", placeholder="Ingresa tu nombre de usuario", help="Tu nombre de usuario para EDUAnalytics", key="username_input")
            password = st.text_input("Contraseña", type="password", placeholder="Ingresa tu contraseña", help="Tu contraseña secreta", key="password_input")

            if st.button("Entrar"):
                user_trimmed = username.strip()
                pass_trimmed = password.strip()

                if not user_trimmed or not pass_trimmed:
                    st.error("Por favor, ingresa tu usuario y contraseña.")
                else:
                    data, status_code = client.login(user_trimmed, pass_trimmed)
                    if status_code == 200:
                        st.session_state["token"] = data["token"]
                        st.session_state["role"] = data["role"]
                        st.session_state["username"] = user_trimmed
                        st.success(f"¡Bienvenido, {user_trimmed} ({data['role']})! Redirigiendo...")
                        st.rerun()
                    else:
                        st.error(data.get("detail", "Error de inicio de sesión. Verifica tus credenciales."))

            st.markdown("<p>¿Problemas para iniciar sesión? Contacta a soporte.</p>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
