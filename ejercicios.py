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
            # Domingo (fijo)
            ["Plancha frontal en antebrazos", "Elevaciones de piernas suaves", "Abdominales crunch con rodillas dobladas", "Movilidad articular de cadera", "Gato-vaca para movilidad espinal", "Respiración diafragmática profunda"]
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
        print(f"[DEBUG] Inicializado Ejercicios con modelo.ejercicios_type: {self.modelo.ejercicios_type if self.modelo else 'None'}")

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
            puntos = {
                # Bodyweight
                "Abdominales crunch con rodillas dobladas": 6,
                "Plancha frontal en antebrazos": 8,
                "Flexiones estándar con manos anchas": 10,
                "Elevaciones frontales de hombros sin peso": 5,
                "Saltos verticales suaves con aterrizaje controlado": 7,
                "Puente de glúteos con rodillas dobladas": 6,
                "Abdominales bicicleta lentos": 7,
                "Elevaciones de piernas suaves": 6,
                "Fondos en silla para tríceps": 8,
                "Plancha con toques de hombros": 8,
                "Burpees modificados sin flexión": 10,
                "Estiramientos dinámicos de cuerpo completo": 5,
                "Plancha lateral con apoyo en antebrazo": 8,
                "Flexiones diamante para tríceps": 10,
                "Rotaciones de hombros con brazos en L": 5,
                "Escaladores pliométricos lentos": 7,
                "Gato-vaca para movilidad espinal": 5,
                "Aperturas de pecho con brazos en T": 5,
                "Saltos laterales suaves sobre línea": 7,
                "Respiración diafragmática profunda": 5,
                "Flexiones pica para hombros": 10,
                "Saltos patinador con cambio lento": 7,
                "Abdominales isométricos de contracción": 6,
                "Yoga suave con posturas básicas": 5,
                "Movilidad articular de cadera": 5,
                # Weights
                "Press de banca con barra": 15,
                "Press inclinado con mancuernas": 14,
                "Press militar con barra": 15,
                "Elevaciones laterales con mancuernas": 12,
                "Aperturas con mancuernas en banco plano": 12,
                "Face pulls con polea": 10,
                "Remo con barra inclinado": 15,
                "Dominadas con peso asistido": 16,
                "Curl de bíceps con mancuernas": 10,
                "Extensiones de tríceps por encima de la cabeza con mancuerna": 10,
                "Remo con mancuerna a una mano": 12,
                "Curl martillo con mancuernas": 10,
                "Press de banca declinado con barra": 15,
                "Aperturas en banco inclinado con mancuernas": 12,
                "Press Arnold con mancuernas": 14,
                "Elevaciones frontales con barra": 12,
                "Fondos en paralelas con peso": 15,
                "Elevaciones traseras para deltoides con mancuernas": 12,
                "Remo sentado en polea baja": 14,
                "Pull-over con mancuerna": 12,
                "Curl de bíceps en banco predicador": 10,
                "Press francés con barra EZ": 10,
                "Remo invertido con barra": 14,
                "Extensiones de tríceps en polea alta": 10,
                "Press de banca con mancuernas": 14,
                "Cruces en polea para pecho": 12,
                "Press de hombros con mancuernas": 14,
                "Elevaciones laterales en banco inclinado": 12,
                "Fondos en banco con peso": 12,
                "Elevaciones frontales con disco": 12,
                "Peso muerto con barra": 16,
                "Remo con barra T": 14,
                "Curl de bíceps con barra recta": 10,
                "Extensiones de tríceps con mancuerna a una mano": 10,
                "Dominadas supinas con peso": 16,
                "Curl concentrado con mancuerna": 10,
                "Press de banca ligero con mancuernas": 10,
                "Elevaciones laterales ligeras con mancuernas": 8,
                "Remo ligero con mancuernas": 10,
                "Curl de bíceps ligero con mancuernas": 8,
                "Extensiones de tríceps ligero en polea": 8,
                "Face pulls ligeros con polea": 8
            }
            puntos = puntos.get(base_name, 5)  # 5 puntos por defecto para ejercicios personalizados
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
            # Seleccionar ejercicios según el tipo del usuario
            base_ejercicios = self.base_ejercicios_weights if self.modelo and self.modelo.ejercicios_type == 'weights' else self.base_ejercicios_bodyweight
            ejercicios_base = base_ejercicios[dia_semana].copy()
            print(f"[DEBUG] Ejercicios base para {fecha.strftime('%Y-%m-%d')} (tipo: {self.modelo.ejercicios_type if self.modelo else 'None'}): {ejercicios_base}")

            fecha_str = fecha.strftime('%Y-%m-%d')
            if self.modelo and self.modelo.ejercicios_personalizados_por_fecha.get(fecha_str):
                ejercicios_base.extend(self.modelo.ejercicios_personalizados_por_fecha[fecha_str])
                print(f"[DEBUG] Ejercicios personalizados añadidos para {fecha_str}: {self.modelo.ejercicios_personalizados_por_fecha[fecha_str]}")

            # Determinar si aplicar progreso_ciclo o usar rutina fija
            if self.modelo and self.modelo.ejercicios_type == 'bodyweight' and dia_semana == 6:  # Domingo
                series, repeticiones, segundos = 3, 10, 60  # Rutina fija para domingos
            else:
                # Usar progreso_ciclo para lunes a sábado (y weights)
                ciclo = self.modelo.progreso_ciclo if self.modelo else 0
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
            print(f"[DEBUG] Ejercicios progresivos para {fecha_str} (ciclo {self.modelo.progreso_ciclo if self.modelo else 0 if dia_semana != 6 or self.modelo.ejercicios_type != 'bodyweight' else 'fijo'}): {ejercicios_progresivos}")
            return ejercicios_progresivos
        except Exception as e:
            print(f"[DEBUG] Error en get_ejercicios_dia: {str(e)}")
            return ["Ejercicio no disponible"]
