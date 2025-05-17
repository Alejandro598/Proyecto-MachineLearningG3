import traceback
from fastapi import FastAPI, HTTPException, Depends, status
from typing import List, Optional
from datetime import datetime
import heapq
from utils.helpers import reg_model, format_db_record, EstudianteRiesgoCalculado


from db.connection import get_db
from schemas.models import (
    EstudianteRiesgoMinimoOutput, LoginData, AuthResponse,
    EstudianteBase, EstudianteCreate, EstudianteInDB,
    AsistenciaInput, AsistenciaInDB,
    EstadoPsicologicoInput, EstadoPsicologicoInDB,
    IncidenciaInput, IncidenciaInDB,
    RiesgoEstudiantePrediction, TopRiesgoOutput
)
from utils.helpers import reg_model, format_db_record, EstudianteRiesgoCalculado
from auth.dependencies import get_current_user_role, check_role

import numpy as np
import heapq
import mysql.connector

app = FastAPI(
    title="Centro Academico API",
    description="API para gestionar asistencia, estados psicológicos e incidencias de estudiantes.",
    version="1.0.0",
)



#Algoritmo de búsqueda informada: Best-First Search
@app.get("/top_n_lowest_risk_students", response_model=List[EstudianteRiesgoMinimoOutput])
def get_top_n_lowest_risk_students(
    n: int = 5,
    db_tuple: tuple = Depends(get_db)
):
    conn, cursor = db_tuple
    estudiantes_con_riesgo_calculado = []

    try:
        min_heap = []
        for estudiante in estudiantes_con_riesgo_calculado:
            heapq.heappush(min_heap, (estudiante['puntaje'], estudiante))

        lowest_risk_students = []
        for _ in range(min(n, len(min_heap))):
            puntaje, estudiante_data = heapq.heappop(min_heap)
            lowest_risk_students.append(EstudianteRiesgoMinimoOutput(**estudiante_data))

        return lowest_risk_students

    except Exception as e:
        print(f"\n--- ERROR DETALLADO DEL SERVIDOR ---")
        traceback.print_exc() 
        print(f"-------------------------------------\n")
        raise HTTPException(status_code=500, detail=f"Error al obtener estudiantes de menor riesgo con Best-First Search: {e}")
    















@app.post("/login", response_model=AuthResponse)
def login(data: LoginData, db_tuple: tuple = Depends(get_db)):
    conn, cursor = db_tuple
    try:
        cursor.execute("SELECT u.NOMBRE, u.CONTRASEÑA, r.NOMBREROL FROM USUARIOS u JOIN ROLES r ON u.IDROL = r.IDROL WHERE u.NOMBRE = %s", (data.username,))
        user = cursor.fetchone()
        if user and user["CONTRASEÑA"] == data.password:
            return {"role": user["NOMBREROL"], "token": "fake-token"}
        else:
            raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al intentar login: {e}")

@app.get("/estudiantes", response_model=List[EstudianteInDB])
def get_all_estudiantes(db_tuple: tuple = Depends(get_db)):
    conn, cursor = db_tuple
    try:
        cursor.execute("SELECT CODIGO, NOMBRE, APELLIDO, TELEFONO FROM ESTUDIANTES")
        estudiantes_raw = cursor.fetchall()
        estudiantes_formateados = [format_db_record(est_dict) for est_dict in estudiantes_raw]
        return [EstudianteInDB(**est_data) for est_data in estudiantes_formateados]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener estudiantes: {e}")

@app.get("/estudiantes/{codigo}", response_model=EstudianteInDB)
def get_estudiante_by_codigo(codigo: int, db_tuple: tuple = Depends(get_db)):
    conn, cursor = db_tuple
    try:
        cursor.execute("SELECT CODIGO, NOMBRE, APELLIDO, TELEFONO FROM ESTUDIANTES WHERE CODIGO = %s", (codigo,))
        estudiante_raw = cursor.fetchone()
        if not estudiante_raw:
            raise HTTPException(status_code=404, detail="Estudiante no encontrado")
        formatted_est = format_db_record(estudiante_raw)
        return EstudianteInDB(**formatted_est)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener estudiante: {e}")

@app.post("/estudiantes", response_model=EstudianteInDB, status_code=status.HTTP_201_CREATED)
def create_estudiante(estudiante: EstudianteCreate, db_tuple: tuple = Depends(get_db)):
    conn, cursor = db_tuple
    try:
        cursor.execute("SELECT MAX(CODIGO) as max_codigo FROM ESTUDIANTES")
        max_codigo_result = cursor.fetchone()
        new_codigo = (max_codigo_result['max_codigo'] or 1000) + 1

        query = "INSERT INTO ESTUDIANTES (CODIGO, NOMBRE, APELLIDO, TELEFONO) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (new_codigo, estudiante.nombre, estudiante.apellido, estudiante.telefono))
        conn.commit()
        return EstudianteInDB(codigo=new_codigo, **estudiante.model_dump())
    except mysql.connector.IntegrityError as e:
        raise HTTPException(status_code=409, detail=f"Error de integridad: El código de estudiante podría ya existir. Detalle: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear estudiante: {e}")

@app.put("/estudiantes/{codigo}", response_model=EstudianteInDB)
def update_estudiante(codigo: int, estudiante: EstudianteCreate, db_tuple: tuple = Depends(get_db)):
    conn, cursor = db_tuple
    try:
        query = "UPDATE ESTUDIANTES SET NOMBRE = %s, APELLIDO = %s, TELEFONO = %s WHERE CODIGO = %s"
        cursor.execute(query, (estudiante.nombre, estudiante.apellido, estudiante.telefono, codigo))
        conn.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Estudiante no encontrado")
        return EstudianteInDB(codigo=codigo, **estudiante.model_dump())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al actualizar estudiante: {e}")

@app.delete("/estudiantes/{codigo}", status_code=status.HTTP_204_NO_CONTENT)
def delete_estudiante(codigo: int, db_tuple: tuple = Depends(get_db)):
    conn, cursor = db_tuple
    try:
        cursor.execute("DELETE FROM ESTUDIANTES WHERE CODIGO = %s", (codigo,))
        conn.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Estudiante no encontrado")
        return
    except mysql.connector.IntegrityError as e:
        raise HTTPException(status_code=409, detail=f"No se puede eliminar el estudiante debido a registros relacionados: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al eliminar estudiante: {e}")

@app.post("/asistencia", response_model=AsistenciaInDB, status_code=status.HTTP_201_CREATED)
def record_asistencia(asistencia: AsistenciaInput, db_tuple: tuple = Depends(get_db)):
    conn, cursor = db_tuple
    try:
        fecha_registro = datetime.now()
        query = "INSERT INTO ASISTENCIA (IDALUMNO, FECHAYHORADEREGISTRO, IDESTADO) VALUES (%s, %s, %s)"
        cursor.execute(query, (asistencia.id_alumno, fecha_registro, asistencia.id_estado))
        conn.commit()
        id_asistencia = cursor.lastrowid
        return AsistenciaInDB(id_asistencia=id_asistencia, fecha_y_hora_de_registro=fecha_registro, **asistencia.model_dump())
    except mysql.connector.IntegrityError as e:
        raise HTTPException(status_code=400, detail=f"Datos inválidos (ej. IDALUMNO o IDESTADO no existen): {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al registrar asistencia: {e}")

@app.get("/asistencia/{id_alumno}", response_model=List[AsistenciaInDB])
def get_asistencia_by_alumno(id_alumno: int, db_tuple: tuple = Depends(get_db)):
    conn, cursor = db_tuple
    try:
        query = "SELECT IDASISTENCIA, IDALUMNO, FECHAYHORADEREGISTRO, IDESTADO FROM ASISTENCIA WHERE IDALUMNO = %s ORDER BY FECHAYHORADEREGISTRO DESC"
        cursor.execute(query, (id_alumno,))
        asistencias_raw = cursor.fetchall()
        asistencias_formateadas = [format_db_record(as_dict) for as_dict in asistencias_raw]
        return [AsistenciaInDB(**a) for a in asistencias_formateadas]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener asistencia: {e}")

@app.post("/estado_psicologico", response_model=EstadoPsicologicoInDB, status_code=status.HTTP_201_CREATED)
def record_estado_psicologico(estado_psicologico: EstadoPsicologicoInput, db_tuple: tuple = Depends(get_db)):
    conn, cursor = db_tuple
    try:
        fecha_registro = datetime.now()
        query = "INSERT INTO ESTADOPSICOLOGICO (IDESTUDIANTE, NOMBREESTADOPSICOLOGICO, FECHAYHORADEREGISTRO, IDINTENSIDAD, IDVALENCIA) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(query, (
            estado_psicologico.id_estudiante,
            estado_psicologico.nombre_estado_psicologico,
            fecha_registro,
            estado_psicologico.id_intensidad,
            estado_psicologico.id_valencia
        ))
        conn.commit()
        id_estado = cursor.lastrowid
        return EstadoPsicologicoInDB(id=id_estado, fecha_y_hora_de_registro=fecha_registro, **estado_psicologico.model_dump())
    except mysql.connector.IntegrityError as e:
        raise HTTPException(status_code=400, detail=f"Datos inválidos (ej. IDESTUDIANTE, IDINTENSIDAD o IDVALENCIA no existen): {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al registrar estado psicológico: {e}")
    
@app.get("/estado_psicologico/{id_estudiante}", response_model=List[EstadoPsicologicoInDB])
def get_estado_psicologico_by_estudiante(id_estudiante: int, db_tuple: tuple = Depends(get_db)):
    conn, cursor = db_tuple
    try:
        query = "SELECT ID, IDESTUDIANTE, NOMBREESTADOPSICOLOGICO, FECHAYHORADEREGISTRO, IDINTENSIDAD, IDVALENCIA FROM ESTADOPSICOLOGICO WHERE IDESTUDIANTE = %s ORDER BY FECHAYHORADEREGISTRO DESC"
        cursor.execute(query, (id_estudiante,))
        estados_raw = cursor.fetchall()
        estados_formateadas = [format_db_record(es_dict) for es_dict in estados_raw]
        return [EstadoPsicologicoInDB(**e) for e in estados_formateadas]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener estados psicológicos: {e}")

@app.get("/estado_psicologico/", response_model=List[EstadoPsicologicoInDB])
def get_all_estados_psicologicos(db_tuple: tuple = Depends(get_db)):
    conn, cursor = db_tuple
    try:
        query = """
            SELECT
                ID AS id,
                IDESTUDIANTE AS id_estudiante,
                NOMBREESTADOPSICOLOGICO AS nombre_estado_psicologico,
                FECHAYHORADEREGISTRO AS fecha_y_hora_de_registro,
                IDINTENSIDAD AS id_intensidad,
                IDVALENCIA AS id_valencia
            FROM estadopsicologico
            ORDER BY FECHAYHORADEREGISTRO DESC
        """
        cursor.execute(query)
        estados_raw = cursor.fetchall()

        estados_list = []
        for row in estados_raw:
            estados_list.append({
                "id": row["id"],
                "id_estudiante": row["id_estudiante"],
                "nombre_estado_psicologico": row["nombre_estado_psicologico"],
                "fecha_y_hora_de_registro": row["fecha_y_hora_de_registro"],
                "id_intensidad": row["id_intensidad"],
                "id_valencia": row["id_valencia"],
            })
        return estados_list

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener todos los estados psicológicos: {e}")


@app.post("/incidencias", response_model=IncidenciaInDB, status_code=status.HTTP_201_CREATED)
def create_incidencia(incidencia: IncidenciaInput, db_tuple: tuple = Depends(get_db)):
    conn, cursor = db_tuple
    try:
        fecha_reporte = datetime.now()
        query = "INSERT INTO INCIDENCIAS (NOMBRE, FECHAYHORAREPORTE, DESCRIPCION, IDAFECTADO, IDREPORTADO) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(query, (
            incidencia.nombre,
            fecha_reporte,
            incidencia.descripcion,
            incidencia.id_afectado,
            incidencia.id_reportado
        ))
        conn.commit()
        id_incidencia = cursor.lastrowid
        return IncidenciaInDB(id=id_incidencia, fecha_y_hora_reporte=fecha_reporte, **incidencia.model_dump())
    except mysql.connector.IntegrityError as e:
        raise HTTPException(status_code=400, detail=f"Datos inválidos (ej. IDAFECTADO o IDREPORTADO no existen): {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear incidencia: {e}")

@app.get("/incidencias", response_model=List[IncidenciaInDB])
def get_all_incidencias(db_tuple: tuple = Depends(get_db)):
    conn, cursor = db_tuple
    try:
        query = """
            SELECT
                i.ID,
                i.NOMBRE,
                i.FECHAYHORAREPORTE,
                i.DESCRIPCION,
                i.IDAFECTADO,
                ea.NOMBRE AS nombre_afectado,
                ea.APELLIDO AS apellido_afectado,
                i.IDREPORTADO,
                er.NOMBRE AS nombre_reporta,
                er.APELLIDO AS apellido_reporta
            FROM INCIDENCIAS i
            JOIN ESTUDIANTES ea ON i.IDAFECTADO = ea.CODIGO
            LEFT JOIN ESTUDIANTES er ON i.IDREPORTADO = er.CODIGO
            ORDER BY i.FECHAYHORAREPORTE DESC
        """
        cursor.execute(query)
        incidencias_raw = cursor.fetchall()
        
        incidencias_list = []
        for row in incidencias_raw:
            incidencias_list.append({
                "id": row["ID"],
                "nombre": row["NOMBRE"],
                "fecha_y_hora_reporte": row["FECHAYHORAREPORTE"],
                "descripcion": row["DESCRIPCION"],
                "id_afectado": row["IDAFECTADO"],
                "nombre_afectado": row["nombre_afectado"],
                "apellido_afectado": row["apellido_afectado"],
                "id_reportado": row["IDREPORTADO"],
                "nombre_reporta": row["nombre_reporta"],
                "apellido_reporta": row["apellido_reporta"]
            })
        return incidencias_list
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener incidencias: {e}")

@app.get("/incidencias/{id_afectado}", response_model=List[IncidenciaInDB])
def get_incidencias_by_afectado(id_afectado: int, db_tuple: tuple = Depends(get_db)):
    conn, cursor = db_tuple
    try:
        query = "SELECT ID, NOMBRE, FECHAYHORAREPORTE, DESCRIPCION, IDAFECTADO, IDREPORTADO FROM INCIDENCIAS WHERE IDAFECTADO = %s ORDER BY FECHAYHORAREPORTE DESC"
        cursor.execute(query, (id_afectado,))
        incidencias_raw = cursor.fetchall()
        incidencias_formateadas = [format_db_record(inc_dict) for inc_dict in incidencias_raw]
        return [IncidenciaInDB(**i) for i in incidencias_formateadas]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener incidencias por afectado: {e}")









#SISTEMAS EXPERTOS BASADOS EN REGLAS
@app.post("/predecir_riesgo/{codigo_estudiante}", response_model=RiesgoEstudiantePrediction)
def predecir_riesgo(codigo_estudiante: int, db_tuple: tuple = Depends(get_db)):
    conn, cursor = db_tuple
    try:
        cursor.execute("SELECT NOMBRE, APELLIDO FROM ESTUDIANTES WHERE CODIGO = %s", (codigo_estudiante,))
        estudiante_info_raw = cursor.fetchone()
        if not estudiante_info_raw:
            raise HTTPException(status_code=404, detail="Estudiante no encontrado")
        estudiante_info = format_db_record(estudiante_info_raw)
        nombre_completo = f"{estudiante_info['nombre']} {estudiante_info['apellido']}"

        cursor.execute("SELECT IDESTADO FROM ASISTENCIA WHERE IDALUMNO = %s", (codigo_estudiante,))
        asistencias_records_raw = cursor.fetchall()
        asistencias_records = [format_db_record(rec) for rec in asistencias_records_raw]
        asistencias_totales = sum(1 for rec in asistencias_records if rec['id_estado'] == 1)
        faltas_totales = sum(1 for rec in asistencias_records if rec['id_estado'] == 2)

        cursor.execute("SELECT COUNT(*) AS count_negativos FROM ESTADOPSICOLOGICO WHERE IDESTUDIANTE = %s AND IDVALENCIA = 3", (codigo_estudiante,))
        negativos_psicologicos = cursor.fetchone()['count_negativos']

        cursor.execute("SELECT COUNT(*) AS count_incidencias FROM INCIDENCIAS WHERE IDAFECTADO = %s", (codigo_estudiante,))
        incidencias_registradas = cursor.fetchone()['count_incidencias']

        ml_input_faltas = min(faltas_totales, 10)
        prob_ml = reg_model.predict(np.array([[ml_input_faltas]]))[0]
        prob_ml = max(0.0, min(1.0, prob_ml))

        riesgo_regla = "bajo"
        if faltas_totales > 5:
            riesgo_regla = "alto"
        elif faltas_totales >= 3:
            riesgo_regla = "medio"

        if negativos_psicologicos > 1:
            if riesgo_regla == "bajo":
                riesgo_regla = "medio"
            elif riesgo_regla == "medio":
                riesgo_regla = "alto"

        if incidencias_registradas > 0:
            if riesgo_regla == "bajo":
                riesgo_regla = "medio"
            elif riesgo_regla == "medio":
                riesgo_regla = "alto"

        return RiesgoEstudiantePrediction(
            codigo_estudiante=codigo_estudiante,
            nombre_estudiante=nombre_completo,
            asistencias_totales=asistencias_totales,
            faltas_totales=faltas_totales,
            riesgo_ml=float(prob_ml),
            riesgo_reglas=riesgo_regla,
            estados_negativos_psicologicos=negativos_psicologicos,
            incidencias_registradas=incidencias_registradas
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al predecir riesgo para el estudiante: {e}")













#REGRESION LINEAL
@app.get("/top_riesgo", response_model=List[TopRiesgoOutput])
def top_riesgo(db_tuple: tuple = Depends(get_db)):
    conn, cursor = db_tuple
    estudiantes_con_riesgo_calculado = []

    try:
        cursor.execute("SELECT CODIGO, NOMBRE, APELLIDO FROM ESTUDIANTES")
        all_estudiantes_raw = cursor.fetchall()
        all_estudiantes = [format_db_record(est_dict) for est_dict in all_estudiantes_raw]

        for est in all_estudiantes:
            codigo = est['codigo']
            nombre = est['nombre']
            apellido = est['apellido']

            cursor.execute("SELECT IDESTADO FROM ASISTENCIA WHERE IDALUMNO = %s", (codigo,))
            asistencias_records_raw = cursor.fetchall()
            asistencias_records = [format_db_record(rec) for rec in asistencias_records_raw]
            faltas_totales = sum(1 for rec in asistencias_records if rec['id_estado'] == 2)

            cursor.execute("SELECT COUNT(*) AS count_negativos FROM ESTADOPSICOLOGICO WHERE IDESTUDIANTE = %s AND IDVALENCIA = 3", (codigo,))
            negativos_psicologicos = cursor.fetchone()['count_negativos']

            cursor.execute("SELECT COUNT(*) AS count_incidencias FROM INCIDENCIAS WHERE IDAFECTADO = %s", (codigo,))
            incidencias_registradas = cursor.fetchone()['count_incidencias']

            ml_input_faltas = min(faltas_totales, 10)
            prob_ml_base = reg_model.predict(np.array([[ml_input_faltas]]))[0]
            prob_ml_base = max(0.0, min(1.0, prob_ml_base))

            puntaje_riesgo = (prob_ml_base * 40) + \
                             (faltas_totales * 5) + \
                             (negativos_psicologicos * 10) + \
                             (incidencias_registradas * 15)

            puntaje_riesgo = max(0.0, min(100.0, puntaje_riesgo))

            estudiantes_con_riesgo_calculado.append({
                "codigo": codigo,
                "nombre": nombre,
                "apellido": apellido,
                "puntaje": round(puntaje_riesgo, 2)
            })

        sorted_estudiantes = sorted(estudiantes_con_riesgo_calculado, key=lambda x: x['puntaje'], reverse=True)
        
        return sorted_estudiantes

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al calcular top riesgo: {e}")