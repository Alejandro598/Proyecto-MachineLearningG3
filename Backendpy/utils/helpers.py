import numpy as np
from sklearn.linear_model import LinearRegression

# Inicialización y entrenamiento del modelo ML
reg_model = LinearRegression()
X_train = np.array([[i] for i in range(11)])
y_train = np.array([0.1, 0.15, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0])
reg_model.fit(X_train, y_train)

def format_db_record(record_dict):
    """
    Formatea las claves de los diccionarios de la base de datos
    (ej. UPPERCASE, camelCase) a snake_case.
    """
    formatted_record = {}
    for key, value in record_dict.items():
        lower_key = key.lower()

        if lower_key == 'idasistencia':
            formatted_record['id_asistencia'] = value
        elif lower_key == 'idalumno':
            formatted_record['id_alumno'] = value
        elif lower_key == 'fechayhoraderegistro':
            formatted_record['fecha_y_hora_de_registro'] = value
        elif lower_key == 'idestado':
            formatted_record['id_estado'] = value
        elif lower_key == 'idestudiante':
            formatted_record['id_estudiante'] = value
        elif lower_key == 'nombreestadopsicologico':
            formatted_record['nombre_estado_psicologico'] = value
        elif lower_key == 'idintensidad':
            formatted_record['id_intensidad'] = value
        elif lower_key == 'idvalencia':
            formatted_record['id_valencia'] = value
        elif lower_key == 'fechayhorareporte':
            formatted_record['fecha_y_hora_reporte'] = value
        elif lower_key == 'idafectado':
            formatted_record['id_afectado'] = value
        elif lower_key == 'idreportado':
            formatted_record['id_reportado'] = value
        else:
            formatted_record[lower_key] = value
    return formatted_record

class EstudianteRiesgoCalculado:
    """Clase auxiliar para el cálculo del top de estudiantes en riesgo."""
    def __init__(self, codigo, nombre, puntaje):
        self.codigo = codigo
        self.nombre = nombre
        self.puntaje = puntaje
        self.visitado = False

    def __lt__(self, otro):
        return self.puntaje > otro.puntaje