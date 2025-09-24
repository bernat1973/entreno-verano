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
            ["Estiramientos dinámicos de cuerpo completo", "Rotaciones de hombros con brazos en L", 
             "Movilidad articular de cadera", "Respiración diafragmática profunda", "Estiramiento de isquiotibiales", 
             "Movilidad de tobillos"],
            # Domingo
            ["Estiramientos dinámicos de cuerpo completo", "Gato-vaca para movilidad espinal", 
             "Respiración diafragmática profunda", "Movilidad articular de cadera", "Estiramiento de isquiotibiales", 
             "Movilidad de tobillos"]
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
            # Sábado - Baja (estiramientos, mismos que bodyweight)
            ["Estiramientos dinámicos de cuerpo completo", "Rotaciones de hombros con brazos en L", 
             "Movilidad articular de cadera", "Respiración diafragmática profunda", "Estiramiento de isquiotibiales", 
             "Movilidad de tobillos"],
            # Domingo - Baja (estiramientos, mismos que bodyweight)
            ["Estiramientos dinámicos de cuerpo completo", "Gato-vaca para movilidad espinal", 
             "Respiración diafragmática profunda", "Movilidad articular de cadera", "Estiramiento de isquiotibiales", 
             "Movilidad de tobillos"]
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
            puntos = 5  # Todos los ejercicios valen 5 puntos
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
            
            # Progresión ajustada
            if contador < 10:  # Primeros 10 entrenamientos
                series, repeticiones, segundos = 3, 10, 30
            elif contador < 20:  # Entrenamientos 11-20
                series, repeticiones, segundos = 3, 12, 40
            elif contador < 30:  # Entrenamientos 21-30
                series, repeticiones, segundos = 3, 15, 50
            else:  # Más de 30 entrenamientos
                series, repeticiones, segundos = 4, 12, 60

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
            self.contador_progresion = 9
            self.ejercicios_personalizados_por_fecha = {}

    modelo = Modelo()
    ejercicios = Ejercicios(modelo)
    fecha = date(2025, 9, 24)  # Miércoles
    print(ejercicios.get_ejercicios_dia(fecha))
