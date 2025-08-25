import json
import os
from datetime import datetime, date, timedelta

class Modelo:
    def __init__(self, archivo):
        self.archivo = archivo
        self.nombre = ""
        self.peso = 0.0
        self.estatura = 0.0
        self.meta_km = {}
        self.km_corridos = {}
        self.ejercicios_completados = {}
        self.historial_semanal = []
        self.mensaje = ""
        self.ejercicios_personalizados = []
        self.ejercicios_personalizados_por_fecha = {}
        self.record_puntos = 0
        self.ejercicios_type = "bodyweight"
        self.cargar_datos()

    def cargar_datos(self):
        try:
            if os.path.exists(self.archivo):
                with open(self.archivo, 'r', encoding='utf-8') as f:
                    datos = json.load(f)
                usuario = datos.get('usuario_actual', '')
                if not usuario or usuario not in datos.get('usuarios', {}):
                    usuario = next(iter(datos.get('usuarios', {})), '')
                if usuario:
                    usuario_datos = datos['usuarios'].get(usuario, {})
                    self.nombre = usuario_datos.get('nombre', '')
                    self.peso = float(usuario_datos.get('peso', 0.0))
                    self.estatura = float(usuario_datos.get('estatura', 0.0))
                    self.meta_km = {str(k): float(v) for k, v in usuario_datos.get('meta_km', {}).items()}
                    self.km_corridos = {k: float(v) for k, v in usuario_datos.get('km_corridos', {}).items()}
                    self.ejercicios_completados = usuario_datos.get('ejercicios_completados', {})
                    self.historial_semanal = usuario_datos.get('historial_semanal', [])
                    self.mensaje = usuario_datos.get('mensaje', '')
                    self.ejercicios_personalizados = usuario_datos.get('ejercicios_personalizados', [])
                    self.ejercicios_personalizados_por_fecha = usuario_datos.get('ejercicios_personalizados_por_fecha', {})
                    self.record_puntos = int(usuario_datos.get('record_puntos', 0))
                    self.ejercicios_type = usuario_datos.get('ejercicios_type', 'bodyweight')
                    print(f"Datos cargados para usuario: {self.nombre}")
                else:
                    print("No se encontró usuario_actual. Inicializando datos vacíos.")
                    self.guardar_datos()
            else:
                print(f"Archivo {self.archivo} no encontrado. Creando datos iniciales.")
                self.guardar_datos()
        except Exception as e:
            print(f"Error al cargar datos: {e}")
            self.guardar_datos()

    def guardar_datos(self):
        try:
            datos = {}
            try:
                if os.path.exists(self.archivo):
                    with open(self.archivo, 'r', encoding='utf-8') as f:
                        datos = json.load(f)
            except FileNotFoundError:
                datos = {'usuarios': {}, 'usuario_actual': self.nombre or 'Usuario'}
            
            if self.nombre:
                datos['usuario_actual'] = self.nombre
                datos['usuarios'][self.nombre] = {
                    'nombre': self.nombre,
                    'peso': self.peso,
                    'estatura': self.estatura,
                    'meta_km': self.meta_km,
                    'km_corridos': self.km_corridos,
                    'ejercicios_completados': self.ejercicios_completados,
                    'historial_semanal': self.historial_semanal,
                    'mensaje': self.mensaje,
                    'ejercicios_personalizados': self.ejercicios_personalizados,
                    'ejercicios_personalizados_por_fecha': self.ejercicios_personalizados_por_fecha,
                    'record_puntos': self.record_puntos,
                    'ejercicios_type': self.ejercicios_type
                }
            with open(self.archivo, 'w', encoding='utf-8') as f:
                json.dump(datos, f, indent=4, ensure_ascii=False)
            print(f"Datos guardados para usuario: {self.nombre}")
        except Exception as e:
            print(f"Error al guardar datos: {e}")

    def nuevo_usuario(self, nombre):
        try:
            if not nombre:
                raise ValueError("El nombre no puede estar vacío.")
            datos = {'usuarios': {}, 'usuario_actual': ''}
            if os.path.exists(self.archivo):
                with open(self.archivo, 'r', encoding='utf-8') as f:
                    datos = json.load(f)
            if nombre in datos['usuarios']:
                raise ValueError(f"El usuario '{nombre}' ya existe.")
            self.nombre = nombre
            self.peso = 0.0
            self.estatura = 0.0
            self.meta_km = {}
            self.km_corridos = {}
            self.ejercicios_completados = {}
            self.historial_semanal = []
            self.mensaje = ""
            self.ejercicios_personalizados = []
            self.ejercicios_personalizados_por_fecha = {}
            self.record_puntos = 0
            self.ejercicios_type = "bodyweight"
            datos['usuario_actual'] = nombre
            datos['usuarios'][nombre] = {
                'nombre': nombre,
                'peso': self.peso,
                'estatura': self.estatura,
                'meta_km': self.meta_km,
                'km_corridos': self.km_corridos,
                'ejercicios_completados': self.ejercicios_completados,
                'historial_semanal': self.historial_semanal,
                'mensaje': self.mensaje,
                'ejercicios_personalizados': self.ejercicios_personalizados,
                'ejercicios_personalizados_por_fecha': self.ejercicios_personalizados_por_fecha,
                'record_puntos': self.record_puntos,
                'ejercicios_type': self.ejercicios_type
            }
            with open(self.archivo, 'w', encoding='utf-8') as f:
                json.dump(datos, f, indent=4, ensure_ascii=False)
            print(f"Nuevo usuario creado: {nombre}")
        except Exception as e:
            print(f"Error al crear usuario: {e}")
            raise

    def cambiar_usuario(self, nombre):
        try:
            datos = {}
            if os.path.exists(self.archivo):
                with open(self.archivo, 'r', encoding='utf-8') as f:
                    datos = json.load(f)
            if nombre not in datos['usuarios']:
                raise ValueError(f"El usuario '{nombre}' no existe.")
            datos['usuario_actual'] = nombre
            with open(self.archivo, 'w', encoding='utf-8') as f:
                json.dump(datos, f, indent=4, ensure_ascii=False)
            self.cargar_datos()
            print(f"Cambiado a usuario: {nombre}")
        except Exception as e:
            print(f"Error al cambiar usuario: {e}")
            raise

    def get_usuarios(self):
        try:
            datos = {}
            if os.path.exists(self.archivo):
                with open(self.archivo, 'r', encoding='utf-8') as f:
                    datos = json.load(f)
            return list(datos['usuarios'].keys())
        except Exception as e:
            print(f"Error al obtener usuarios: {e}")
            return []

    def registrar_ejercicios(self, fecha, ejercicios):
        try:
            fecha_str = fecha.strftime('%Y-%m-%d') if isinstance(fecha, date) else fecha
            if fecha_str not in self.ejercicios_completados:
                self.ejercicios_completados[fecha_str] = {}
            for ejercicio, completado in ejercicios.items():
                self.ejercicios_completados[fecha_str][ejercicio] = completado
            self.guardar_datos()
        except Exception as e:
            print(f"Error al registrar ejercicios: {e}")

    def registrar_km(self, fecha, km):
        try:
            fecha_str = fecha.strftime('%Y-%m-%d') if isinstance(fecha, date) else fecha
            self.km_corridos[fecha_str] = float(km)
            self.guardar_datos()
        except Exception as e:
            print(f"Error al registrar km: {e}")

    def eliminar_km(self, fecha):
        try:
            fecha_str = fecha.strftime('%Y-%m-%d') if isinstance(fecha, date) else fecha
            if fecha_str in self.km_corridos:
                del self.km_corridos[fecha_str]
                self.guardar_datos()
        except Exception as e:
            print(f"Error al eliminar km: {e}")

    def anadir_ejercicio_personalizado(self, fecha, ejercicio):
        try:
            fecha_str = fecha.strftime('%Y-%m-%d') if isinstance(fecha, date) else fecha
            if fecha_str not in self.ejercicios_personalizados_por_fecha:
                self.ejercicios_personalizados_por_fecha[fecha_str] = []
            if ejercicio not in self.ejercicios_personalizados_por_fecha[fecha_str]:
                self.ejercicios_personalizados_por_fecha[fecha_str].append(ejercicio)
                if ejercicio not in self.ejercicios_personalizados:
                    self.ejercicios_personalizados.append(ejercicio)
                self.guardar_datos()
            print(f"Ejercicio personalizado añadido: {ejercicio} para {fecha_str}")
        except Exception as e:
            print(f"Error al añadir ejercicio personalizado: {e}")

    def evaluar_semana(self, get_ejercicios_dia, fecha, get_puntos):
        try:
            fecha = fecha if isinstance(fecha, date) else datetime.strptime(fecha, '%Y-%m-%d').date()
            semana_ano = str(fecha.isocalendar()[1])
            inicio_semana = fecha - timedelta(days=fecha.weekday())
            puntos_totales = 0
            km_totales = 0
            ejercicios_completados = 0
            ejercicios_totales = 0
            estadisticas = {
                'promedio_puntos': 0,
                'dia_mas_activo': '',
                'progreso_km': 0
            }
            max_puntos_dia = 0
            recompensas = []

            for i in range(7):
                dia = inicio_semana + timedelta(days=i)
                dia_str = dia.strftime('%Y-%m-%d')
                ejercicios_dia = get_ejercicios_dia(dia)
                ejercicios_totales += len(ejercicios_dia)
                puntos_dia = 0
                completados_dia = 0

                if dia_str in self.ejercicios_completados:
                    for ejercicio, completado in self.ejercicios_completados[dia_str].items():
                        if completado:
                            puntos_dia += get_puntos(ejercicio)
                            completados_dia += 1
                if dia_str in self.km_corridos:
                    km_totales += self.km_corridos[dia_str]
                puntos_totales += puntos_dia
                ejercicios_completados += completados_dia
                if puntos_dia > max_puntos_dia:
                    max_puntos_dia = puntos_dia
                    estadisticas['dia_mas_activo'] = dia_str

            estadisticas['promedio_puntos'] = round(puntos_totales / 7, 1) if puntos_totales > 0 else 0
            meta_km = self.meta_km.get(semana_ano, 0)
            estadisticas['progreso_km'] = round((km_totales / meta_km * 100), 1) if meta_km > 0 else 0

            if puntos_totales >= 150:
                ranking = "Mega Crack"
                recompensas.append("Crack")
            elif puntos_totales >= 100:
                ranking = "Chill"
                recompensas.append("Chill")
            elif puntos_totales >= 50:
                ranking = "Noob"
                recompensas.append("Noob")
            else:
                ranking = "Looser"
                recompensas.append("Looser")

            imagen_ranking = f"/static/recompensas/{ranking.lower()}.png"
            if puntos_totales > self.record_puntos:
                self.record_puntos = puntos_totales
                self.guardar_datos()

            self.historial_semanal.append({
                'semana': inicio_semana.strftime('%Y-%m-%d'),
                'puntos': puntos_totales,
                'km': km_totales,
                'completados': ejercicios_completados,
                'totales': ejercicios_totales,
                'ranking': ranking
            })
            self.guardar_datos()

            return puntos_totales, km_totales, ejercicios_completados, ejercicios_totales, recompensas, ranking, imagen_ranking, self.record_puntos, estadisticas
        except Exception as e:
            print(f"Error en evaluar_semana: {e}")
            return 0, 0, 0, 0, [], "Sin ranking", "", 0, {}

    def generar_resumen(self, puntos, km, completados, totales, recompensas, ranking, imagen_ranking, record_puntos, meta_km):
        try:
            porcentaje = (completados / totales * 100) if totales > 0 else 0
            texto = f"¡Hola, {self.nombre}!\n\n"
            es_nuevo_record = puntos >= record_puntos and puntos > 0

            if ranking == "Looser":
                texto += "Esta semana no fue tu mejor momento, pero ¡tú puedes con esto! 😔\n"
                texto += f"Lograste {puntos} puntos ({porcentaje:.1f}% de ejercicios completados).\n"
                texto += "💪 **Reto para la próxima semana**: Completa al menos 3 ejercicios diarios.\n"
                texto += "Consejo: Empieza con ejercicios cortos como estiramientos para crear un hábito.\n\n"
            elif ranking == "Noob":
                texto += "¡Buen esfuerzo, Noob! 🌟 Estás en el camino correcto.\n"
                texto += f"Conseguiste {puntos} puntos ({porcentaje:.1f}% de ejercicios completados).\n"
                texto += "🚀 **Propósito**: Añade un ejercicio personalizado para subir a Chill.\n"
                texto += "Consejo: Planea tus entrenos al inicio de la semana para mantenerte constante.\n\n"
            elif ranking == "Chill":
                texto += "¡Estás en la onda, Chill! 😎 ¡Gran trabajo!\n"
                texto += f"Sumaste {puntos} puntos ({porcentaje:.1f}% de ejercicios completados).\n"
                texto += "🏅 **Desafío**: Apunta a 150 puntos para ser Mega Crack.\n"
                texto += "Consejo: Si corriste mucho, incluye estiramientos para evitar lesiones.\n\n"
            else:  # Mega Crack
                texto += "¡Eres un Mega Crack! 🏆 ¡Impresionante!\n"
                texto += f"Arrasaste con {puntos} puntos ({porcentaje:.1f}% de ejercicios completados).\n"
                texto += "🎉 **Sigue así**: Elige una actividad divertida como premio.\n"
                texto += "Consejo: Mantén la variedad con nuevos ejercicios personalizados.\n\n"

            if es_nuevo_record:
                texto += f"🎊 **¡Nuevo récord!** Has superado tu mejor marca con {puntos} puntos.\n\n"

            if recompensas:
                texto += "🎁 **Recompensas**:\n"
                for recompensa in recompensas:
                    texto += f"- {recompensa}\n"
            else:
                texto += "😢 No obtuviste recompensas esta semana, pero ¡sigue dándole duro!\n"

            if km < meta_km and meta_km > 0:
                texto += f"\n🏃 **Desafío semanal**: Corre {round(meta_km - km, 2)} km más para alcanzar tu meta de {meta_km} km.\n"
            else:
                texto += "\n🏃 **Desafío semanal**: Aumenta tu meta de kilómetros en 5 km para la próxima semana.\n"

            return texto
        except Exception as e:
            print(f"Error en generar_resumen: {e}")
            return "Error al generar el resumen."
