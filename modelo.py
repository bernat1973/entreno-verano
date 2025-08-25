import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime, date, timedelta
import os

class Modelo:
    def __init__(self, archivo=None, use_auth=False):
        self.use_auth = use_auth  # True si usas Firebase Authentication
        # Inicializar Firebase
        try:
            if not firebase_admin._apps:
                if os.getenv('FIREBASE_PROJECT_ID'):
                    if os.getenv('FIREBASE_PROJECT_ID') != 'entreno-verano':
                        raise ValueError(f"Proyecto incorrecto: esperado 'entreno-verano', recibido {os.getenv('FIREBASE_PROJECT_ID')}")
                    cred = credentials.Certificate({
                        "type": "service_account",
                        "project_id": "entreno-verano",
                        "private_key": os.getenv('FIREBASE_PRIVATE_KEY').replace('\\n', '\n'),
                        "client_email": os.getenv('FIREBASE_CLIENT_EMAIL'),
                        "token_uri": "https://oauth2.googleapis.com/token"
                    })
                else:
                    cred = credentials.Certificate('firebase-adminsdk.json')
                firebase_admin.initialize_app(cred)
                print("[DEBUG] Firebase inicializado correctamente para proyecto: entreno-verano")
            self.db = firestore.client()
            # Verificar que el proyecto sea el correcto
            if self.db._firestore_client.project != 'entreno-verano':
                raise ValueError(f"Conectado al proyecto incorrecto: {self.db._firestore_client.project}")
            print("[DEBUG] Conectado a Firestore en proyecto: entreno-verano")
        except Exception as e:
            print(f"[DEBUG] Error al inicializar Firebase: {str(e)}")
            raise
        self.nombre = ""
        self.uid = None  # Para Firebase Authentication
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
            # Obtener usuario_actual desde Firestore
            config_ref = self.db.collection('config').document('app')
            config = config_ref.get()
            if not config.exists:
                print("[DEBUG] Documento config/app no existe. Creando con usuario por defecto.")
                self.guardar_datos()
                return
            config_data = config.to_dict() or {'usuario_actual': 'Usuario'}
            usuario_id = config_data.get('usuario_actual', 'Usuario')
            print(f"[DEBUG] usuario_actual desde Firestore: {usuario_id}")
            
            # Cargar datos del usuario
            usuario_ref = self.db.collection('usuarios').document(usuario_id)
            usuario_doc = usuario_ref.get()
            if not usuario_doc.exists:
                print(f"[DEBUG] No se encontraron datos para {usuario_id}. Inicializando.")
                self.guardar_datos()
                return
            
            usuario_datos = usuario_doc.to_dict()
            self.nombre = usuario_datos.get('nombre', '')
            if self.use_auth:
                self.uid = usuario_id
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
            print(f"[DEBUG] Datos cargados para usuario: {self.nombre} (ID: {usuario_id})")
        except Exception as e:
            print(f"[DEBUG] Error al cargar datos: {str(e)}")
            self.guardar_datos()

    def guardar_datos(self):
        try:
            if not self.nombre:
                print("[DEBUG] No se puede guardar: nombre de usuario vacío")
                return
            # Usar UID si usas Authentication, o nombre como ID
            user_id = self.uid if self.use_auth and self.uid else self.nombre
            usuario_ref = self.db.collection('usuarios').document(user_id)
            usuario_ref.set({
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
            })
            # Actualizar usuario_actual
            self.db.collection('config').document('app').set({
                'usuario_actual': user_id
            }, merge=True)
            print(f"[DEBUG] Datos guardados para usuario: {self.nombre} (ID: {user_id})")
        except Exception as e:
            print(f"[DEBUG] Error al guardar datos: {str(e)}")

    def nuevo_usuario(self, nombre, uid=None):
        try:
            if not nombre:
                raise ValueError("El nombre no puede estar vacío.")
            user_id = uid if self.use_auth and uid else nombre
            usuario_ref = self.db.collection('usuarios').document(user_id)
            if usuario_ref.get().exists:
                raise ValueError(f"El usuario '{nombre}' ya existe.")
            self.nombre = nombre
            if self.use_auth:
                self.uid = uid
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
            self.guardar_datos()
            print(f"[DEBUG] Nuevo usuario creado: {nombre} (ID: {user_id})")
        except Exception as e:
            print(f"[DEBUG] Error al crear usuario: {str(e)}")
            raise

    def cambiar_usuario(self, user_id):
        try:
            usuario_ref = self.db.collection('usuarios').document(user_id)
            if not usuario_ref.get().exists:
                raise ValueError(f"El usuario con ID '{user_id}' no existe.")
            self.db.collection('config').document('app').set({
                'usuario_actual': user_id
            }, merge=True)
            self.cargar_datos()
            print(f"[DEBUG] Cambiado a usuario: {self.nombre} (ID: {user_id})")
        except Exception as e:
            print(f"[DEBUG] Error al cambiar usuario: {str(e)}")
            raise

    def get_usuarios(self):
        try:
            usuarios = []
            for doc in self.db.collection('usuarios').stream():
                data = doc.to_dict()
                usuarios.append({'id': doc.id, 'nombre': data.get('nombre', doc.id)})
            print(f"[DEBUG] Usuarios recuperados: {usuarios}")
            if not usuarios:
                print("[DEBUG] No se encontraron usuarios en Firestore. Verifica la colección 'usuarios'.")
            return usuarios
        except Exception as e:
            print(f"[DEBUG] Error al obtener usuarios: {str(e)}")
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
            print(f"[DEBUG] Error al registrar ejercicios: {str(e)}")

    def registrar_km(self, fecha, km):
        try:
            fecha_str = fecha.strftime('%Y-%m-%d') if isinstance(fecha, date) else fecha
            self.km_corridos[fecha_str] = float(km)
            self.guardar_datos()
        except Exception as e:
            print(f"[DEBUG] Error al registrar km: {str(e)}")

    def eliminar_km(self, fecha):
        try:
            fecha_str = fecha.strftime('%Y-%m-%d') if isinstance(fecha, date) else fecha
            if fecha_str in self.km_corridos:
                del self.km_corridos[fecha_str]
                self.guardar_datos()
        except Exception as e:
            print(f"[DEBUG] Error al eliminar km: {str(e)}")

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
        except Exception as e:
            print(f"[DEBUG] Error al añadir ejercicio personalizado: {str(e)}")

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
            print(f"[DEBUG] Error en evaluar_semana: {str(e)}")
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
            print(f"[DEBUG] Error en generar_resumen: {str(e)}")
            return "Error al generar el resumen."
