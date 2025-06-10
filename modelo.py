import json
import os
from datetime import datetime, date, timedelta

class Modelo:
    def __init__(self, archivo):
        # Usar la ruta en /tmp/ como caché
        self.archivo = '/tmp/entreno_verano.json'
        print(f"Inicializando con archivo: {self.archivo}")
        self.nombre = ""
        self.peso = 0.0
        self.estatura = 0.0
        self.meta_km = {}
        self.km_corridos = {}
        self.ejercicios_completados = {}
        self.usuarios = {}
        self.usuario_actual = ""
        self.historial_semanal = []
        self.mensaje = ""
        self.ejercicios_personalizados = []
        self.ejercicios_personalizados_por_fecha = {}
        self.record_puntos = 0
        self.cargar_datos()

    def cargar_datos(self):
        try:
            with open(self.archivo, 'r', encoding='utf-8') as f:
                datos = json.load(f)
                self.usuarios = datos.get('usuarios', {})
                usuario = datos.get('usuario_actual', 'Usuario')
                usuario_datos = self.usuarios.get(usuario, {})
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
                self.usuario_actual = usuario
                print(f"Datos cargados desde {self.archivo}: {datos}")
        except FileNotFoundError:
            print(f"Archivo {self.archivo} no encontrado, inicializando vacío")
            self.guardar_datos()
        except json.JSONDecodeError as e:
            print(f"Error al decodificar JSON en {self.archivo}: {e}")
            self.guardar_datos()
        except Exception as e:
            print(f"Error al cargar datos desde {self.archivo}: {e}")

    def guardar_datos(self):
        try:
            if self.usuario_actual and self.usuario_actual in self.usuarios:
                self.usuarios[self.usuario_actual].update({
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
                    'record_puntos': self.record_puntos
                })
            datos = {
                'usuarios': self.usuarios,
                'usuario_actual': self.usuario_actual
            }
            os.makedirs(os.path.dirname(self.archivo) or '.', exist_ok=True)
            temp_file = self.archivo + '.tmp'
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(datos, f, indent=4, ensure_ascii=False)
            os.replace(temp_file, self.archivo)
            with open(self.archivo, 'r', encoding='utf-8') as f:
                verificados = json.load(f)
                if verificados != datos:
                    print(f"Advertencia: Datos escritos ({verificados}) no coinciden con datos esperados ({datos})")
                print(f"Datos guardados correctamente en {self.archivo}: {verificados}")
        except PermissionError as e:
            print(f"Error de permisos al guardar {self.archivo}: {e}. Contacta al soporte de Render.")
        except Exception as e:
            print(f"Error al guardar datos en {self.archivo}: {e}. Revisa la ruta y permisos.")

    def nuevo_usuario(self, nombre):
        if not nombre or nombre.strip() == "":
            raise ValueError("El nombre no puede estar vacío.")
        if nombre in self.usuarios:
            raise ValueError(f"El usuario '{nombre}' ya existe.")
        self.usuarios[nombre] = {
            'nombre': nombre,
            'peso': 0.0,
            'estatura': 0.0,
            'meta_km': {},
            'km_corridos': {},
            'ejercicios_completados': {},
            'historial_semanal': [],
            'mensaje': '',
            'ejercicios_personalizados': [],
            'ejercicios_personalizados_por_fecha': {},
            'record_puntos': 0
        }
        self.usuario_actual = nombre
        self.nombre = nombre
        self.peso = 0.0
        self.estatura = 0.0
        self.meta_km = {}
        self.km_corridos = {}
        self.ejercicios_completados = {}
        self.historial_semanal = []
        self.mensaje = ''
        self.ejercicios_personalizados = []
        self.ejercicios_personalizados_por_fecha = {}
        self.record_puntos = 0
        self.guardar_datos()

    def cambiar_usuario(self, nombre):
        if nombre not in self.usuarios:
            raise ValueError(f"El usuario '{nombre}' no existe.")
        self.usuario_actual = nombre
        usuario_datos = self.usuarios[nombre]
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
        self.guardar_datos()

    def get_usuarios(self):
        return list(self.usuarios.keys())

    def anadir_ejercicio_personalizado(self, ejercicio, fecha):
        if not ejercicio.strip():
            raise ValueError("El ejercicio no puede estar vacío.")
        if not fecha:
            raise ValueError("La fecha no puede estar vacía.")
        if fecha not in self.ejercicios_personalizados_por_fecha:
            self.ejercicios_personalizados_por_fecha[fecha] = []
        if ejercicio not in self.ejercicios_personalizados_por_fecha[fecha]:
            self.ejercicios_personalizados_por_fecha[fecha].append(ejercicio)
            if ejercicio not in self.ejercicios_personalizados:
                self.ejercicios_personalizados.append(ejercicio)
        self.guardar_datos()

    def evaluar_semana(self, get_ejercicios_dia, fecha, get_puntos):
        try:
            if isinstance(fecha, str):
                fecha = datetime.strptime(fecha, '%Y-%m-%d').date()
            semana_ano = fecha.isocalendar()[1]
            inicio_semana = fecha - timedelta(days=fecha.weekday())
            fin_semana = inicio_semana + timedelta(days=6)
            puntos_totales = 0
            km_totales = 0.0
            ejercicios_totales = 0
            ejercicios_completados = 0
            puntos_por_dia = {}
            dia_mas_activo = (inicio_semana, 0)

            for i in range(7):
                dia = inicio_semana + timedelta(days=i)
                dia_str = dia.strftime("%Y-%m-%d")
                ejercicios_dia = get_ejercicios_dia(dia)
                ejercicios_totales += len(ejercicios_dia)
                puntos_dia = 0
                for ejercicio in ejercicios_dia:
                    base_ejercicio = ejercicio
                    for prefix in [" series de ", " segundos "]:
                        if prefix in ejercicio:
                            base_ejercicio = ejercicio.split(prefix)[-1].strip()
                            break
                    if self.ejercicios_completados.get(dia_str, {}).get(base_ejercicio, False):
                        ejercicios_completados += 1
                        puntos_dia += get_puntos(base_ejercicio)
                puntos_totales += puntos_dia
                puntos_por_dia[dia_str] = puntos_dia
                if puntos_dia > dia_mas_activo[1]:
                    dia_mas_activo = (dia, puntos_dia)
                km_totales += float(self.km_corridos.get(dia_str, 0.0))

            promedio_puntos = puntos_totales / 7 if puntos_totales > 0 else 0
            dia_mas_activo_str = dia_mas_activo[0].strftime("%d/%m/%Y") if dia_mas_activo[1] > 0 else "Ninguno"
            meta_km = float(self.meta_km.get(str(semana_ano), 0.0))
            progreso_km = (km_totales / meta_km * 100) if meta_km > 0 else 0

            if puntos_totales < 50:
                ranking = "Looser"
                recompensas = ["Tarea doméstica: Lavar los platos"]
                imagen_ranking = "😣"
            elif puntos_totales < 100:
                ranking = "Noob"
                recompensas = ["Penalización: 30 min menos de Play"]
                imagen_ranking = "😐"
            elif puntos_totales < 150:
                ranking = "Chill"
                recompensas = ["Premio: 30 min más de Play"]
                imagen_ranking = "😎"
            else:
                ranking = "Mega Crack"
                recompensas = ["Premio: Actividad que te apetezca"]
                imagen_ranking = "🏆"

            if puntos_totales > self.record_puntos:
                self.record_puntos = puntos_totales
                self.guardar_datos()

            if km_totales >= meta_km and meta_km > 0:
                recompensas.append("¡Meta de kilómetros alcanzada!")

            estadisticas = {
                'promedio_puntos': round(promedio_puntos, 1),
                'dia_mas_activo': dia_mas_activo_str,
                'progreso_km': round(progreso_km, 1)
            }

            self.historial_semanal.append({
                'semana': inicio_semana.strftime('%Y-%m-%d'),
                'puntos': puntos_totales,
                'km': km_totales,
                'completados': ejercicios_completados,
                'totales': ejercicios_totales,
                'ranking': ranking
            })
            self.guardar_datos()

            print(f"Evaluando semana {semana_ano} desde {inicio_semana}: Puntos={puntos_totales}, Completados={ejercicios_completados}/{ejercicios_totales}, Ranking={ranking}, Estadísticas={estadisticas}")
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
