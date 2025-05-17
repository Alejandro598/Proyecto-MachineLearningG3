from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class EstudianteRiesgoMinimoOutput(BaseModel):
    codigo: int
    nombre: str
    apellido: str
    puntaje: float

class LoginData(BaseModel):
    username: str
    password: str

class AuthResponse(BaseModel):
    role: str
    token: str

class EstudianteBase(BaseModel):
    nombre: str
    apellido: str
    telefono: Optional[str] = None

class EstudianteCreate(EstudianteBase):
    pass

class EstudianteInDB(EstudianteBase):
    codigo: int

    class Config:
        from_attributes = True

class AsistenciaInput(BaseModel):
    id_alumno: int
    id_estado: int

class AsistenciaInDB(BaseModel):
    id_asistencia: int
    id_alumno: int
    fecha_y_hora_de_registro: datetime
    id_estado: int

    class Config:
        from_attributes = True

class EstadoPsicologicoInput(BaseModel):
    id_estudiante: int
    nombre_estado_psicologico: str
    id_intensidad: int
    id_valencia: int

class EstadoPsicologicoInDB(BaseModel):
    id: int
    id_estudiante: int
    nombre_estado_psicologico: str
    fecha_y_hora_de_registro: datetime
    id_intensidad: int
    id_valencia: int
    nombre_estudiante: Optional[str] = None
    apellido_estudiante: Optional[str] = None

class IncidenciaInput(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    id_afectado: int
    id_reportado: Optional[int] = None

class IncidenciaInDB(BaseModel):
    id: int
    nombre: str
    fecha_y_hora_reporte: datetime
    descripcion: Optional[str] = None
    id_afectado: int
    nombre_afectado: Optional[str] = None
    apellido_afectado: Optional[str] = None
    id_reportado: Optional[int] = None
    nombre_reporta: Optional[str] = None
    apellido_reporta: Optional[str] = None

    class Config:
        from_attributes = True

class RiesgoEstudiantePrediction(BaseModel):
    codigo_estudiante: int
    nombre_estudiante: str
    asistencias_totales: int
    faltas_totales: int
    riesgo_ml: float
    riesgo_reglas: str
    estados_negativos_psicologicos: int
    incidencias_registradas: int

class TopRiesgoOutput(BaseModel):
    codigo: int
    nombre: str
    apellido: str
    puntaje: float

    class Config:
        from_attributes = True
