from datetime import datetime, date
import random

class Ejercicios:
    def __init__(self, modelo=None):
        self.modelo = modelo
        # Cambia esta fecha por la de tu primer día de entreno (formato 'YYYY-MM-DD')
        self.fecha_inicio = "2025-06-16"

        self.base_ejercicios = [
    # Lunes: pliométricos + core + estiramiento
    [
        "Saltos en estrella",
        "Jumping lunges",
        "Plancha frontal en antebrazos",
        "Plancha lateral derecha",
        "Dead bug",
        "Gato-vaca"
    ],
    # Martes: core + flexiones + movilidad
    [
        "Plancha con toque de hombros",
        "Flexiones estándar",
        "Flexiones inclinadas",
        "Hollow hold",
        "Superman",
        "Estiramiento psoas"
    ],
    # Miércoles: pliométricos + abdominales + movilidad
    [
        "Saltos rodilla al pecho",
        "Skipping alto rápido",
        "Crunch inverso",
        "Crunch bicicleta",
        "Postura del niño",
        "Cobra"
    ],
    # Jueves: core dinámico + flexiones + estiramiento
    [
        "Plancha dinámica",
        "Flexiones diamante",
        "Flexiones tocando hombro",
        "Abdominales isométricos",
        "Inclinaciones pélvicas tumbado",
        "Movilidad lumbar en L"
    ],
    # Viernes: pliométricos + abdominales + movilidad
    [
        "Saltos laterales sobre línea",
        "Burpee con salto",
        "Elevaciones de piernas tumbado",
        "Ab roll",
        "Estiramiento glúteo piriforme",
        "Gato-vaca"
    ],
    # Sábado: movilidad y recuperación
    [
        "Gato-vaca",
        "Postura del niño",
        "Cobra",
        "Estiramiento psoas",
        "Movilidad lumbar en L",
        "Estiramiento glúteo piriforme"
    ],
    # Domingo: descanso activo o repetir favoritos
    [
        "Saltos patinador",
        "Plancha lateral izquierda",
        "Plancha lateral derecha",
        "Superman",
        "Crunch inverso",
        "Gato-vaca"
    ]
]

    def get_base_exercise_name(self, ejercicio):
        try:
            for prefix in [" series de ", " segundos "]:
                if prefix in ejercicio:
                    return ejercicio.split(prefix)[-1].strip()
            return ejercicio
        except Exception as e:
            print(f"Error al extraer nombre base de {ejercicio}: {e}")
            return ejercicio

    def get_puntos(self, ejercicio):
        return 5

    def get_ejercicios_dia(self, fecha, historial_semanal=None):
        try:
            if not isinstance(fecha, date):
                if isinstance(fecha, datetime):
                    fecha = fecha.date()
                elif isinstance(fecha, str):
                    fecha = datetime.strptime(fecha, "%Y-%m-%d").date()
                else:
                    raise ValueError(f"Formato de fecha no válido: {fecha}")
            
            dia_semana = fecha.weekday()
            ejercicios_base = self.base_ejercicios[dia_semana].copy()

            # Añadir ejercicios personalizados para la fecha especificada
            fecha_str = fecha.strftime('%Y-%m-%d')
            if self.modelo and self.modelo.ejercicios_personalizados_por_fecha.get(fecha_str):
                ejercicios_base.extend(self.modelo.ejercicios_personalizados_por_fecha[fecha_str])

            # --- PROGRESIÓN DESDE FECHA DE INICIO ---
            fecha_inicio_dt = datetime.strptime(self.fecha_inicio, "%Y-%m-%d").date()
            semanas_desde_inicio = max(0, (fecha - fecha_inicio_dt).days // 7)
            ciclo = semanas_desde_inicio % 24
            # -----------------------------------------

            if ciclo < 4:
                series, repeticiones, segundos = 3, 10, 60
            elif ciclo < 8:
                series, repeticiones, segundos = 3, 12, 70
            elif ciclo < 12:
                series, repeticiones, segundos = 4, 12, 70
            else:
                series, repeticiones, segundos = 4, 15, 80

            ejercicios_progresivos = []
            for ej in ejercicios_base:
                if any(palabra in ej.lower() for palabra in ["estiramiento", "movilidad", "respiración", "yoga", "isométrico", "gato-vaca", "puente"]):
                    ejercicios_progresivos.append(f"{series} series de {segundos} segundos {ej}")
                else:
                    ejercicios_progresivos.append(f"{series} series de {repeticiones} {ej}")

            random.shuffle(ejercicios_progresivos)
            return ejercicios_progresivos  # Eliminar el límite [:6]
        except Exception as e:
            print(f"Error en get_ejercicios_dia: {e}")
            return ["Ejercicio no disponible"]
