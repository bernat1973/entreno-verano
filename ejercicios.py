from datetime import datetime, date
import random

class Ejercicios:
    def __init__(self, modelo=None):
        self.modelo = modelo
        self.base_ejercicios_bodyweight = [
            # Lunes
            ["Abdominales crunch con rodillas dobladas", "Plancha frontal en antebrazos", "Flexiones estándar con manos anchas", "Elevaciones frontales de hombros sin peso", "Saltos verticales suaves con aterrizaje controlado", "Puente de glúteos con rodillas dobladas"],
            # Martes
            ["Abdominales bicicleta lentos", "Elevaciones de piernas suaves", "Fondos en silla para tríceps", "Plancha con toques de hombros", "Burpees modificados sin flexión", "Estiramientos dinámicos de cuerpo completo"],
            # Miércoles
            ["Plancha lateral con apoyo en antebrazo", "Abdominales crunch con rodillas dobladas", "Flexiones diamante para tríceps", "Rotaciones de hombros con brazos en L", "Escaladores pliométricos lentos", "Gato-vaca para movilidad espinal"],
            # Jueves
            ["Abdominales bicicleta lentos", "Plancha frontal en antebrazos", "Aperturas de pecho con brazos en T", "Elevaciones laterales de hombros sin peso", "Saltos laterales suaves sobre línea", "Respiración diafragmática profunda"],
            # Viernes
            ["Elevaciones de piernas suaves", "Plancha lateral con apoyo en antebrazo", "Flexiones estándar con manos anchas", "Flexiones pica para hombros", "Saltos patinador con cambio lento", "Abdominales isométricos de contracción"],
            # Sábado
            ["Abdominales crunch con rodillas dobladas", "Abdominales bicicleta lentos", "Fondos en silla para tríceps", "Plancha con toques de hombros", "Burpees modificados sin flexión", "Yoga suave con posturas básicas"],
            # Domingo
            ["Plancha frontal en antebrazos", "Elevaciones de piernas suaves", "Flexiones diamante para tríceps", "Elevaciones frontales de hombros sin peso", "Saltos verticales suaves con fuerza", "Movilidad articular de cadera"]
        ]
        self.base_ejercicios_weights = [
            # Lunes: Foco en pectorales y hombros
            ["Press de banca con barra", "Aperturas con mancuernas en banco", "Press militar con mancuernas", "Elevaciones laterales con mancuernas", "Elevaciones frontales con mancuernas", "Extensiones de tríceps con mancuerna por encima de la cabeza"],
            # Martes: Foco en espalda y brazos
            ["Remo con barra inclinado", "Remo con mancuernas", "Curl de bíceps con mancuernas", "Curl martillo con mancuernas", "Dominadas asistidas en barra", "Extensiones de tríceps en banco"],
            # Miércoles: Foco en pectorales y espalda
            ["Press inclinado con barra", "Fondos en banco con peso", "Remo invertido en barra", "Elevaciones traseras para deltoides con mancuernas", "Curl concentrado con mancuerna", "Press francés con barra"],
            # Jueves: Foco en hombros y brazos
            ["Press de hombros con barra", "Elevaciones laterales con mancuernas", "Remo alto con mancuernas", "Curl de bíceps con barra", "Extensiones de tríceps con mancuerna", "Elevaciones frontales con barra"],
            # Viernes: Foco en pectorales y hombros
            ["Press de banca con mancuernas", "Aperturas en banco inclinado con mancuernas", "Press Arnold con mancuernas", "Elevaciones laterales en banco", "Curl de bíceps alterno con mancuernas", "Patadas de tríceps con mancuerna"],
            # Sábado: Foco en espalda y brazos
            ["Remo con barra T", "Remo sentado con mancuernas", "Curl de bíceps en banco predicador", "Extensiones de tríceps por encima de la cabeza con barra", "Dominadas en barra con peso asistido", "Curl concentrado alterno"],
            # Domingo: Foco mixto (recuperación activa con pesas ligeras)
            ["Press de banca ligero con barra", "Elevaciones frontales con mancuernas ligeras", "Remo con mancuernas ligero", "Curl de bíceps ligero con mancuernas", "Extensiones de tríceps ligero", "Elevaciones laterales ligeras con mancuernas"]
        ]
        if self.modelo and self.modelo.ejercicios_type == 'weights':
            self.base_ejercicios = self.base_ejercicios_weights
        else:
            self.base_ejercicios = self.base_ejercicios_bodyweight

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
            semana_ano = fecha.isocalendar()[1]
            ejercicios_base = self.base_ejercicios[dia_semana].copy()

            fecha_str = fecha.strftime('%Y-%m-%d')
            if self.modelo and self.modelo.ejercicios_personalizados_por_fecha.get(fecha_str):
                ejercicios_base.extend(self.modelo.ejercicios_personalizados_por_fecha[fecha_str])

            ciclo = (semana_ano - 1) % 16
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
            return ejercicios_progresivos
        except Exception as e:
            print(f"Error en get_ejercicios_dia: {e}")
            return ["Ejercicio no disponible"]
