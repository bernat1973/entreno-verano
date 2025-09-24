from datetime import datetime, date
import random

class Ejercicios:
    def __init__(self, modelo=None):
        self.modelo = modelo
        
        # EJERCICIOS SIN PESAS ORIGINALES (mantenidos para historial)
        self.base_ejercicios_bodyweight = [
            # Lunes
            ["Flexiones estándar con manos anchas", "Fondos en silla para tríceps", "Plancha frontal en antebrazos", 
             "Elevaciones frontales de hombros sin peso", "Aperturas de pecho con brazos en T", "Flexiones pica para hombros"],
            # Martes
            ["Abdominales bicicleta lentos", "Flexiones diamante para tríceps", "Plancha con toques de hombros", 
             "Elevaciones laterales de hombros sin peso", "Abdominales crunch con rodillas dobladas", "Plancha lateral con apoyo en antebrazo"],
            # Miércoles
            ["Plancha frontal en antebrazos", "Abdominales crunch con rodillas dobladas", "Elevaciones de piernas suaves", 
             "Rotaciones de hombros con brazos en L", "Gato-vaca para movilidad espinal", "Puente de glúteos con rodillas dobladas"],
            # Jueves
            ["Burpees modificados sin flexión", "Flexiones diamante para tríceps", "Escaladores pliométricos lentos", 
             "Saltos verticales suaves con fuerza", "Fondos en silla para tríceps", "Abdominales isométricos de contracción"],
            # Viernes
            ["Plancha frontal en antebrazos", "Abdominales crunch con rodillas dobladas", "Flexiones pica para hombros", 
             "Saltos laterales suaves sobre línea", "Elevaciones laterales de hombros sin peso", "Yoga suave con posturas básicas"],
            # Sábado
            ["Estiramientos dinámicos de cuerpo completo", "Saltos verticales suaves con aterrizaje controlado", 
             "Rotaciones de hombros con brazos en L", "Movilidad articular de cadera", "Saltos patinador con cambio lento", 
             "Respiración diafragmática profunda"],
            # Domingo
            ["Estiramientos dinámicos de cuerpo completo", "Gato-vaca para movilidad espinal", "Respiración diafragmática profunda", 
             "Puente de glúteos con rodillas dobladas", "Aperturas de pecho con brazos en T", "Movilidad articular de cadera"]
        ]
        
        # EJERCICIOS CON PESAS ORIGINALES
        self.base_ejercicios_weights = [
            # Lunes: Pectorales y hombros
            ["Press de banca con barra", "Press inclinado con mancuernas", "Press militar con barra", 
             "Elevaciones laterales con mancuernas", "Aperturas con mancuernas en banco plano", "Face pulls con polea"],
            # Martes: Espalda y brazos
            ["Remo con barra inclinado", "Dominadas con peso asistido", "Curl de bíceps con mancuernas", 
             "Extensiones de tríceps por encima de la cabeza con mancuerna", "Remo con mancuerna a una mano", 
             "Curl martillo con mancuernas"],
            # Miércoles: Pectorales y hombros
            ["Press de banca declinado con barra", "Aperturas en banco inclinado con mancuernas", "Press Arnold con mancuernas", 
             "Elevaciones frontales con barra", "Fondos en paralelas con peso", "Elevaciones traseras para deltoides con mancuernas"],
            # Jueves: Espalda y brazos
            ["Remo sentado en polea baja", "Pull-over con mancuerna", "Curl de bíceps en banco predicador", 
             "Press francés con barra EZ", "Remo invertido con barra", "Extensiones de tríceps en polea alta"],
            # Viernes: Pectorales y hombros
            ["Press de banca con mancuernas", "Cruces en polea para pecho", "Press de hombros con mancuernas", 
             "Elevaciones laterales en banco inclinado", "Fondos en banco con peso", "Elevaciones frontales con disco"],
            # Sábado: Espalda y brazos
            ["Peso muerto con barra", "Remo con barra T", "Curl de bíceps con barra recta", 
             "Extensiones de tríceps con mancuerna a una mano", "Dominadas supinas con peso", "Curl concentrado con mancuerna"],
            # Domingo: Recuperación activa
            ["Press de banca ligero con mancuernas", "Elevaciones laterales ligeras con mancuernas", "Remo ligero con mancuernas", 
             "Curl de bíceps ligero con mancuernas", "Extensiones de tríceps ligero en polea", "Face pulls ligeros con polea"]
        ]
        
        # EJERCICIOS SIN PESAS PARA FÚTBOL (Juan 16 años y Nico 13 años)
        self.base_ejercicios_futbol = [
            # Lunes - Media-alta (core, tren superior, saltos explosivos)
            ["Tuck L-sit", "Plancha frontal en antebrazos", "Flexiones estándar con manos anchas", 
             "Elevaciones frontales de hombros sin peso", "Saltos verticales suaves", "Puente de glúteos"],
            # Martes - Media-alta (core, resistencia, tríceps, explosividad)
            ["Russian Twist", "Up Wipers", "Fondos en silla para tríceps", "Plancha con toques de hombros", 
             "Burpees modificados", "Estiramientos dinámicos"],
            # Miércoles - Media (core, estabilidad lateral, coordinación)
            ["Handstand contra pared", "Tuck Front Lever", "Flexiones diamante", "Rotaciones de hombros", 
             "Escaladores pliométricos", "Gato-vaca"],
            # Jueves - Alta (explosividad, core, tren superior, más intenso)
            ["Heel Toucher", "Plancha frontal", "Aperturas de pecho", "Elevaciones laterales sin peso", 
             "Saltos laterales suaves", "Respiración diafragmática"],
            # Viernes - Media-alta (core, agilidad lateral, hombros)
            ["Rotacional Punch", "Plancha lateral", "Flexiones estándar", "Flexiones pica", "Saltos patinador", 
             "Abdominales isométricos"],
            # Sábado - Baja (recuperación activa, yoga, movilidad ligera)
            ["Tuck L-sit", "Russian Twist", "Fondos en silla", "Plancha con toques", "Burpees modificados", "Yoga suave"],
            # Domingo - Baja (estiramientos, movilidad, recuperación suave)
            ["Handstand contra pared", "Up Wipers", "Flexiones diamante", "Elevaciones frontales sin peso", 
             "Saltos verticales", "Movilidad articular"]
        ]
        
        # EJERCICIOS MIXTOS (Combinación de con y sin pesas, para Juan y Nico)
        self.base_ejercicios_mixtos = [
            # Lunes - Fuerza + Explosividad
            ["Press de banca ligero", "Flexiones explosivas", "Sentadillas con salto", "Remo con mancuernas", 
             "Plancha frontal", "Saltos de caja"],
            # Martes - Core + Resistencia
            ["Russian Twist con peso", "Mountain climbers", "Curl de bíceps", "Fondos en silla", "Burpees", 
             "Elevaciones laterales"],
            # Miércoles - Técnica + Movilidad
            ["Press militar ligero", "Flexiones diamante", "Peso muerto rumano", "Plancha lateral", "Gato-vaca", 
             "Face pulls"],
            # Jueves - Potencia + Agilidad
            ["Clean and press", "Saltos al cajón", "Dominadas asistidas", "Sprint en el sitio", "Medicine ball slams", 
             "Battle ropes"],
            # Viernes - Full Body
            ["Sentadillas con mancuernas", "Press de banca", "Remo con barra", "Plancha frontal", "Flexiones", 
             "Elevaciones de gemelos"],
            # Sábado - Recuperación Activa
            ["Yoga con pesas ligeras", "Estiramientos dinámicos", "Remo suave", "Caminar con mancuernas", 
             "Movilidad articular", "Respiración profunda"],
            # Domingo - Cardio + Fuerza ligera
            ["Circuito de peso corporal", "Press ligero", "Jumping jacks", "Curl martillo ligero", "Abdominales", 
             "Estiramientos estáticos"]
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
                # Bodyweight originales
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
                "Aperturas de pecho con brazos en T": 6,
                "Saltos laterales suaves sobre línea": 7,
                "Respiración diafragmática profunda": 4,
                "Flexiones pica para hombros": 10,
                "Saltos patinador con cambio lento": 7,
                "Abdominales isométricos de contracción": 6,
                "Yoga suave con posturas básicas": 5,
                "Movilidad articular de cadera": 5,
                
                # Nuevos ejercicios sin pesas para fútbol
                "Tuck L-sit": 12,
                "Russian Twist": 8,
                "Up Wipers": 10,
                "Handstand contra pared": 14,
                "Tuck Front Lever": 15,
                "Heel Toucher": 6,
                "Rotacional Punch": 7,
                "Plancha lateral": 8,
                "Flexiones estándar": 9,
                "Flexiones pica": 10,
                "Saltos patinador": 8,
                "Abdominales isométricos": 7,
                "Plancha frontal": 8,
                "Burpees modificados": 9,
                "Escaladores pliométricos": 8,
                "Gato-vaca": 5,
                "Elevaciones laterales sin peso": 5,
                "Saltos laterales suaves": 7,
                "Respiración diafragmática": 4,
                "Plancha con toques": 9,
                "Yoga suave": 5,
                "Movilidad articular": 5,
                "Saltos verticales suaves": 7,
                "Saltos verticales": 8,
                "Puente de glúteos": 6,
                "Estiramientos dinámicos": 5,
                "Rotaciones de hombros": 5,
                "Fondos en silla": 8,
                "Flexiones diamante": 10,
                
                # Ejercicios mixtos
                "Press de banca ligero": 10,
                "Flexiones explosivas": 11,
                "Sentadillas con salto": 10,
                "Remo con mancuernas": 12,
                "Saltos de caja": 9,
                "Russian Twist con peso": 10,
                "Mountain climbers": 8,
                "Curl de bíceps": 8,
                "Press militar ligero": 10,
                "Peso muerto rumano": 14,
                "Clean and press": 16,
                "Saltos al cajón": 10,
                "Dominadas asistidas": 14,
                "Sprint en el sitio": 7,
                "Medicine ball slams": 12,
                "Battle ropes": 11,
                "Sentadillas con mancuernas": 12,
                "Elevaciones de gemelos": 6,
                "Yoga con pesas ligeras": 7,
                "Caminar con mancuernas": 6,
                "Circuito de peso corporal": 10,
                "Press ligero": 8,
                "Jumping jacks": 5,
                "Curl martillo ligero": 7,
                "Abdominales": 6,
                "Estiramientos estáticos": 4,
                
                # Weights (mantener los originales)
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
            if self.modelo and hasattr(self.modelo, 'ejercicios_type'):
                if self.modelo.ejercicios_type == 'weights':
                    base_ejercicios = self.base_ejercicios_weights
                elif self.modelo.ejercicios_type == 'futbol':
                    base_ejercicios = self.base_ejercicios_futbol
                elif self.modelo.ejercicios_type == 'mixtos':
                    base_ejercicios = self.base_ejercicios_mixtos
                else:  # 'bodyweight' o por defecto
                    base_ejercicios = self.base_ejercicios_bodyweight
            else:
                base_ejercicios = self.base_ejercicios_bodyweight
                
            ejercicios_base = base_ejercicios[dia_semana].copy()
            print(f"[DEBUG] Ejercicios base para {fecha.strftime('%Y-%m-%d')} (tipo: {self.modelo.ejercicios_type if self.modelo else 'None'}): {ejercicios_base}")

            fecha_str = fecha.strftime('%Y-%m-%d')
            if self.modelo and self.modelo.ejercicios_personalizados_por_fecha.get(fecha_str):
                ejercicios_base.extend(self.modelo.ejercicios_personalizados_por_fecha[fecha_str])
                print(f"[DEBUG] Ejercicios personalizados añadidos para {fecha_str}: {self.modelo.ejercicios_personalizados_por_fecha[fecha_str]}")

            # Progresión basada en entrenamientos completados
            if self.modelo and hasattr(self.modelo, 'contador_progresion'):
                contador = self.modelo.contador_progresion
            else:
                contador = 0
            
            # Progresión para un niño de 13 años (ajustada para menor intensidad)
            if contador < 10:  # Primeros 10 entrenamientos
                series, repeticiones, segundos = 2, 8, 30
            elif contador < 20:  # Entrenamientos 11-20
                series, repeticiones, segundos = 2, 10, 40
            elif contador < 30:  # Entrenamientos 21-30
                series, repeticiones, segundos = 3, 10, 50
            else:  # Más de 30 entrenamientos
                series, repeticiones, segundos = 3, 12, 60

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

# Ejemplo de uso
if __name__ == "__main__":
    class Modelo:
        def __init__(self):
            self.ejercicios_type = 'futbol'
            self.contador_progresion = 5
            self.ejercicios_personalizados_por_fecha = {}

    modelo = Modelo()
    ejercicios = Ejercicios(modelo)
    fecha = date(2025, 9, 24)  # Miércoles
    print(ejercicios.get_ejercicios_dia(fecha))
