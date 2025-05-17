import requests
from datetime import datetime

API_URL = "http://localhost:8000"

def get_top_n_lowest_risk_students(n: int = 5):
    try:
        response = requests.get(f"{API_URL}/top_n_lowest_risk_students", params={"n": n})
        response.raise_for_status()
        return response.json(), response.status_code
    except requests.exceptions.RequestException as e:
        return {"detail": f"Error de conexión con la API: {e}"}, 500
    except Exception as e:
        return {"detail": f"Error inesperado al obtener estudiantes de menor riesgo: {e}"}, 500

def login(username, password):
    resp = requests.post(f"{API_URL}/login", json={"username": username, "password": password})
    return resp.json(), resp.status_code

def get_estudiantes():
    resp = requests.get(f"{API_URL}/estudiantes")
    return resp.json(), resp.status_code

def get_estudiante_by_codigo(codigo: int):
    resp = requests.get(f"{API_URL}/estudiantes/{codigo}")
    return resp.json(), resp.status_code

def create_estudiante(nombre, apellido, telefono):
    payload = {"nombre": nombre, "apellido": apellido, "telefono": telefono}
    resp = requests.post(f"{API_URL}/estudiantes", json=payload)
    return resp.json(), resp.status_code

def update_estudiante(codigo, nombre, apellido, telefono):
    payload = {"nombre": nombre, "apellido": apellido, "telefono": telefono}
    resp = requests.put(f"{API_URL}/estudiantes/{codigo}", json=payload)
    return resp.json(), resp.status_code

def delete_estudiante(codigo):
    resp = requests.delete(f"{API_URL}/estudiantes/{codigo}")
    return resp.status_code

def predecir_riesgo(codigo_estudiante):
    resp = requests.post(f"{API_URL}/predecir_riesgo/{codigo_estudiante}")
    return resp.json(), resp.status_code

def get_top_riesgo():
    resp = requests.get(f"{API_URL}/top_riesgo")
    return resp.json(), resp.status_code

def record_asistencia(id_alumno, id_estado):
    payload = {"id_alumno": id_alumno, "id_estado": id_estado}
    resp = requests.post(f"{API_URL}/asistencia", json=payload)
    return resp.json(), resp.status_code

def get_asistencia_by_alumno(id_alumno):
    resp = requests.get(f"{API_URL}/asistencia/{id_alumno}")
    return resp.json(), resp.status_code

def record_estado_psicologico(id_estudiante, nombre_estado, id_intensidad, id_valencia):
    payload = {
        "id_estudiante": id_estudiante,
        "nombre_estado_psicologico": nombre_estado,
        "id_intensidad": id_intensidad,
        "id_valencia": id_valencia
    }
    resp = requests.post(f"{API_URL}/estado_psicologico", json=payload)
    return resp.json(), resp.status_code

def get_estado_psicologico_by_estudiante(id_estudiante):
    resp = requests.get(f"{API_URL}/estado_psicologico/{id_estudiante}")
    return resp.json(), resp.status_code

def get_all_estados_psicologicos():
    resp = requests.get(f"{API_URL}/estado_psicologico/")
    return resp.json(), resp.status_code

def create_incidencia(nombre, descripcion, id_afectado, id_reportado):
    payload = {
        "nombre": nombre,
        "descripcion": descripcion,
        "id_afectado": id_afectado,
        "id_reportado": id_reportado
    }
    resp = requests.post(f"{API_URL}/incidencias", json=payload)
    return resp.json(), resp.status_code

def get_incidencias():
    resp = requests.get(f"{API_URL}/incidencias")
    return resp.json(), resp.status_code
