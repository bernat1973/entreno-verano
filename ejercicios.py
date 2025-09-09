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
            # Lunes: Pectorales y hombros
            ["Press de banca con barra", "Press inclinado con mancuernas", "Press militar con barra", "Elevaciones laterales con mancuernas", "Aperturas con mancuernas en banco plano", "Face pulls con polea"],
            # Martes: Espalda y brazos
            ["Remo con barra inclinado", "Dominadas con peso asistido", "Curl de bíceps con mancuernas", "Extensiones de tríceps por encima de la cabeza con mancuerna", "Remo con mancuerna a una mano", "Curl martillo con mancuernas"],
            # Miércoles: Pectorales y hombros
            ["Press de banca declinado con barra", "Aperturas en banco inclinado con mancuernas", "Press Arnold con mancuernas", "Elevaciones frontales con barra", "Fondos en paralelas con peso", "Elevaciones traseras para deltoides con mancuernas"],
            # Jueves: Espalda y brazos
            ["Remo sentado en polea baja", "Pull-over con mancuerna", "Curl de bíceps en banco predicador", "Press francés con barra EZ", "Remo invertido con barra", "Extensiones de tríceps en polea alta"],
            # Viernes: Pectorales y hombros
            ["Press de banca con mancuernas", "Cruces en polea para pecho", "Press de hombros con mancuernas", "Elevaciones laterales en banco inclinado", "Fondos en banco con peso", "Elevaciones frontales con disco"],
            # Sábado: Espalda y brazos
            ["Peso muerto con barra", "Remo con barra T", "Curl de bíceps con barra recta", "Extensiones de tríceps con mancuerna a una mano", "Dominadas supinas con peso", "Curl concentrado con mancuerna"],
            # Domingo: Recuperación activa
            ["Press de banca ligero con mancuernas", "Elevaciones laterales ligeras con mancuernas", "Remo ligero con mancuernas", "Curl de bíceps ligero con mancuernas", "Extensiones de tríceps ligero en polea", "Face pulls ligeros con polea"]
        ]
        self.base_ejercicios_new_bodyweight = [
            # Lunes
            ["Tuck L-sit", "Plancha frontal en antebrazos", "Flexiones estándar con manos anchas", "Elevaciones frontales de hombros sin peso", "Saltos verticales suaves", "Puente de glúteos"],
            # Martes
            ["Russian Twist", "Up Wipers", "Fondos en silla para tríceps", "Plancha con toques de hombros", "Burpees modificados", "Estiramientos dinámicos"],
            # Miércoles
            ["Handstand contra pared", "Tuck Front Lever", "Flexiones diamante", "Rotaciones de hombros", "Escaladores pliométricos", "Gato-vaca"],
            # Jueves
            ["Heel Toucher", "Plancha frontal", "Aperturas de pecho", "Elevaciones laterales sin peso", "Saltos laterales suaves", "Respiración diafragmática"],
            # Viernes
            ["Rotacional Punch", "Plancha lateral", "Flexiones estándar", "Flexiones pica", "Saltos patinador", "Abdominales isométricos"],
            # Sábado
            ["Tuck L-sit", "Russian Twist", "Fondos en silla", "Plancha con toques", "Burpees modificados", "Yoga suave"],
            # Domingo
            ["Handstand contra pared", "Up Wipers", "Flexiones diamante", "Elevaciones frontales sin peso", "Saltos verticales", "Movilidad articular"]
        ]
        self.base_ejercicios_mixta = [
            # Lunes
            ["Press de banca con barra", "Plancha frontal", "Elevaciones laterales con mancuernas", "Flexiones estándar", "Russian Twist", "Puente de glúteos"],
            # Martes
            ["Remo con barra", "Heel Toucher", "Curl de bíceps", "Fondos en silla", "Burpees modificados", "Estiramientos dinámicos"],
            # Miércoles
            ["Press inclinado con mancuernas", "Handstand contra pared", "Press militar", "Tuck Front Lever", "Escaladores pliométricos", "Gato-vaca"],
            # Jueves
            ["Remo sentado en polea", "Plancha frontal", "Curl de bíceps en banco", "Aperturas de pecho", "Saltos laterales", "Respiración"],
            # Viernes
            ["Press de hombros", "Plancha lateral", "Elevaciones laterales", "Flexiones pica", "Saltos patinador", "Abdominales isométricos"],
            # Sábado
            ["Peso muerto", "Russian Twist", "Curl martillo", "Plancha con toques", "Burpees", "Yoga suave"],
            # Domingo
            ["Press ligero", "Up Wipers", "Remo ligero", "Flexiones diamante", "Saltos verticales", "Movilidad articular"]
        ]
        self.base_ejercicios_correccion = [
            # Lunes
            ["Estiramientos de pecho en puerta", "Remo con banda elástica", "Elevaciones de hombros con peso ligero", "Plancha con rotación", "Cat-Cow", "Aperturas de pecho"],
            # Martes
            ["Estiramientos de espalda inclinada", "Pull-over ligero", "Rotaciones de hombros", "Plancha lateral", "Movilidad espinal", "Press de hombros suave"],
            # Miércoles
            ["Estiramientos de pecho", "Remo con mancuerna ligera", "Elevaciones frontales", "Plancha con apoyo", "Cat-Cow", "Aperturas de pecho con manos atrás"],
            # Jueves
            ["Estiramientos de espalda", "Pull-over con banda", "Rotaciones de hombros", "Plancha lateral", "Movilidad espinal", "Press de hombros ligero"],
            # Viernes
            ["Estiramientos de pecho en puerta", "Remo con banda", "Elevaciones laterales ligeras", "Plancha con rotación", "Cat-Cow", "Aperturas de pecho"],
            # Sábado
            ["Estiramientos de espalda inclinada", "Pull-over ligero", "Rotaciones de hombros", "Plancha lateral", "Movilidad espinal", "Press de hombros suave"],
            # Domingo
            ["Estiramientos de pecho", "Remo con mancuerna", "Elevaciones frontales", "Plancha con apoyo", "Cat-Cow", "Aperturas de pecho con manos atrás"]
        ]
        print(f"[DEBUG] Inicializado Ejercicios con modelo.categoria_entrenamiento: {self.modelo.categoria_entrenamiento if self.modelo else 'None'}")

    def get_base_exercise_name(self, ejercicio):
        try:
            for prefix in [" series de ", " segundos "]:
                if prefix in ejercicio:
                    return ejercicio.split(prefix)[-1].strip()
            return ejercicio
        except Exception as e:
            print(f"[DEBUG] Error al extraer nombre base de {ejercicio}: {str(e)}")
            return ejercicio

    def get_puntos(self, ejercicio):
        try:
            base_name = self.get_base_exercise_name(ejercicio)
            # Todos los ejercicios valen 5 puntos por defecto
            puntos = 5
            print(f"[DEBUG] Puntos para {ejercicio} ({base_name}): {puntos}")
            return puntos
        except Exception as e:
            print(f"[DEBUG] Error en get_puntos: {str(e)}")
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
            # Seleccionar ejercicios según la categoría
            categoria = self.modelo.categoria_entrenamiento if self.modelo and self.modelo.categoria_entrenamiento else "bodyweight"
            base_ejercicios = {
                "bodyweight": self.base_ejercicios_bodyweight,
                "weight": self.base_ejercicios_weights,
                "new_bodyweight": self.base_ejercicios_new_bodyweight,
                "mixta": self.base_ejercicios_mixta,
                "correccion": self.base_ejercicios_correccion
            }.get(categoria, self.base_ejercicios_bodyweight)
            ejercicios_base = base_ejercicios[dia_semana].copy()
            print(f"[DEBUG] Ejercicios base para {fecha.strftime('%Y-%m-%d')} (categoria: {categoria}): {ejercicios_base}")

            fecha_str = fecha.strftime('%Y-%m-%d')
            if self.modelo and self.modelo.ejercicios_personalizados_por_fecha.get(fecha_str):
                ejercicios_base.extend(self.modelo.ejercicios_personalizados_por_fecha[fecha_str])
                print(f"[DEBUG] Ejercicios personalizados añadidos para {fecha_str}: {self.modelo.ejercicios_personalizados_por_fecha[fecha_str]}")

            ciclo = (fecha.isocalendar()[1] - 1) % 16
            if ciclo < 4:
                series, repeticiones, segundos = 3, 10, 60
            elif cycle < 8:
                series, repeticiones, segundos = 3, 12, 70
            elif cycle < 12:
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
            print(f"[DEBUG] Ejercicios progresivos para {fecha_str}: {ejercicios_progresivos}")
            return ejercicios_progresivos
        except Exception as e:
            print(f"[DEBUG] Error en get_ejercicios_dia: {str(e)}")
            return ["Ejercicio no disponible"]
