import firebase_admin
from firebase_admin import credentials, firestore
from datetime import date, timedelta
import os

class Modelo:
    def __init__(self, use_auth=False):
        try:
            # Depurar variables de entorno
            project_id = os.getenv("FIREBASE_PROJECT_ID")
            client_email = os.getenv("FIREBASE_CLIENT_EMAIL")
            private_key = os.getenv("FIREBASE_PRIVATE_KEY")
            print(f"[DEBUG] FIREBASE_PROJECT_ID: {project_id}")
            print(f"[DEBUG] FIREBASE_CLIENT_EMAIL: {client_email}")
            print(f"[DEBUG] FIREBASE_PRIVATE_KEY: {'[present]' if private_key else 'None'}")
            print(f"[DEBUG] Longitud de FIREBASE_PRIVATE_KEY: {len(private_key) if private_key else 0}")

            # Verificar que las variables existen
            if not project_id:
                raise ValueError("FIREBASE_PROJECT_ID no está configurado")
            if not client_email:
                raise ValueError("FIREBASE_CLIENT_EMAIL no está configurado")
            if not private_key:
                raise ValueError("FIREBASE_PRIVATE_KEY no está configurado")

            # Inicializar Firebase con las credenciales
            try:
                cred = credentials.Certificate({
                    "type": "service_account",
                    "project_id": project_id,
                    "private_key": private_key.replace('\\n', '\n'),
                    "client_email": client_email,
                    "token_uri": "https://oauth2.googleapis.com/token"
                })
                firebase_admin.initialize_app(cred)
                self.db = firestore.client()
            except Exception as e:
                print(f"[DEBUG] Error al inicializar credenciales de Firebase: {str(e)}")
                raise ValueError(f"Fallo al inicializar Firebase: {str(e)}")

            # Verificar ID del proyecto (opcional, para depuración)
            app_project_id = firebase_admin.get_app().options.get('projectId')
            print(f"[DEBUG] Firebase inicializado, projectId detectado: {app_project_id}")
            if app_project_id != 'entreno-verano':
                print(f"[WARNING] Proyecto Firebase esperado: 'entreno-verano', encontrado: {app_project_id}")

            self.use_auth = use_auth
            self.nombre = ""
            self.peso = 0.0
            self.estatura = 0.0
            self.meta_km = {}
            self.ejercicios_type = "bodyweight"
            self.km_corridos = {}
            self.ejercicios_completados = {}
            self.ejercicios_personalizados = []
            self.ejercicios_personalizados_por_fecha = {}
            self.historial_semanal = []
            self.record_puntos = 0
            self.mensaje = ""
            self.user_id = None
            self.cargar_datos()
        except Exception as e:
            print(f"[DEBUG] Error al inicializar Modelo: {str(e)}")
            raise

    def cargar_datos(self):
        try:
            # Cargar usuario actual desde config/app
            config_ref = self.db.collection('config').document('app')
            config = config_ref.get().to_dict() or {}
            self.user_id = config.get('usuario_actual', None)
            if not self.user_id:
                print("[DEBUG] No hay usuario actual en config/app")
                return
            # Cargar datos del usuario
            user_ref = self.db.collection('usuarios').document(self.user_id)
            user_data = user_ref.get().to_dict() or {}
            self.nombre = user_data.get('nombre', '')
            self.peso = user_data.get('peso', 0.0)
            self.estatura = user_data.get('estatura', 0.0)
            self.meta_km = user_data.get('meta_km', {})
            self.ejercicios_type = user_data.get('ejercicios_type', 'bodyweight')
            self.km_corridos = user_data.get('km_corridos', {})
            self.ejercicios_completados = user_data.get('ejercicios_completados', {})
            self.ejercicios_personalizados = user_data.get('ejercicios_personalizados', [])
            self.ejercicios_personalizados_por_fecha = user_data.get('ejercicios_personalizados_por_fecha', {})
            self.historial_semanal = user_data.get('historial_semanal', [])
            self.record_puntos = user_data.get('record_puntos', 0)
            self.mensaje = user_data.get('mensaje', '')
            print(f"[DEBUG] Datos cargados para usuario {self.user_id}: ejercicios_type={self.ejercicios_type}")
        except Exception as e:
            print(f"[DEBUG] Error al cargar datos: {str(e)}")

    def guardar_datos(self):
        try:
            user_ref = self.db.collection('usuarios').document(self.user_id)
            user_ref.set({
                'nombre': self.nombre,
                'peso': self.peso,
                'estatura': self.estatura,
                'meta_km': self.meta_km,
                'ejercicios_type': self.ejercicios_type,
                'km_corridos': self.km_corridos,
                'ejercicios_completados': self.ejercicios_completados,
                'ejercicios_personalizados': self.ejercicios_personalizados,
                'ejercicios_personalizados_por_fecha': self.ejercicios_personalizados_por_fecha,
                'historial_semanal': self.historial_semanal,
                'record_puntos': self.record_puntos,
                'mensaje': self.mensaje
            })
            # Actualizar usuario actual
            config_ref = self.db.collection('config').document('app')
            config_ref.set({'usuario_actual': self.user_id}, merge=True)
            print(f"[DEBUG] Datos guardados para usuario {self.user_id}")
        except Exception as e:
            print(f"[DEBUG] Error al guardar datos: {str(e)}")

    def nuevo_usuario(self, nombre, uid=None):
        self.user_id = nombre if not self.use_auth else uid
        if not self.user_id:
            raise ValueError("El ID de usuario no puede estar vacío")
        self.nombre = nombre
        self.peso = 0.0
        self.estatura = 0.0
        self.meta_km = {}
        self.ejercicios_type = "bodyweight"
        self.km_corridos = {}
        self.ejercicios_completados = {}
        self.ejercicios_personalizados = []
        self.ejercicios_personalizados_por_fecha = {}
        self.historial_semanal = []
        self.record_puntos = 0
        self.mensaje = ""
        self.guardar_datos()

    def cambiar_usuario(self, user_id):
        try:
            print(f"[DEBUG] Intentando cambiar a usuario: {user_id}")
            if not user_id or user_id not in self.get_usuarios():
                print(f"[DEBUG] Usuario {user_id} no encontrado o inválido")
                return False
            self.user_id = user_id
            self.cargar_datos()
            print(f"[DEBUG] Cambio a usuario {self.user_id} realizado, ejercicios_type={self.ejercicios_type}")
            config_ref = self.db.collection('config').document('app')
            config_ref.set({'usuario_actual': self.user_id}, merge=True)
            return True
        except Exception as e:
            print(f"[DEBUG] Error al cambiar usuario: {str(e)}")
            return False

    def registrar_km(self, fecha, km):
        self.km_corridos[fecha] = km
        self.guardar_datos()

    def eliminar_km(self, fecha):
        if fecha in self.km_corridos:
            del self.km_corridos[fecha]
            self.guardar_datos()

    def registrar_ejercicios(self, fecha, ejercicios_dict):
        fecha_str = fecha.strftime('%Y-%m-%d') if isinstance(fecha, date) else fecha
        self.ejercicios_completados[fecha_str] = ejercicios_dict
        self.guardar_datos()

    def anadir_ejercicio_personalizado(self, fecha, ejercicio):
        fecha_str = fecha.strftime('%Y-%m-%d') if isinstance(fecha, date) else fecha
        if fecha_str not in self.ejercicios_personalizados_por_fecha:
            self.ejercicios_personalizados_por_fecha[fecha_str] = []
        if ejercicio not in self.ejercicios_personalizados_por_fecha[fecha_str]:
            self.ejercicios_personalizados_por_fecha[fecha_str].append(ejercicio)
            self.ejercicios_personalizados.append(ejercicio)
            self.guardar_datos()

    def get_usuarios(self):
        try:
            usuarios = [doc.id for doc in self.db.collection('usuarios').stream()]
            print(f"[DEBUG] Usuarios obtenidos: {usuarios}")
            return usuarios
        except Exception as e:
            print(f"[DEBUG] Error al obtener usuarios: {str(e)}")
            return []

    def evaluar_semana(self, get_ejercicios_dia, fecha, get_puntos):
        try:
            inicio_semana = fecha - timedelta(days=fecha.weekday())
            fin_semana = inicio_semana + timedelta(days=6)
            puntos = 0
            km = 0.0
            completados = 0
            totales = 0
            for i in range(7):
                dia = (inicio_semana + timedelta(days=i)).strftime('%Y-%m-%d')
                ejercicios_dia = get_ejercicios_dia(dia, self.historial_semanal)
                totales += len(ejercicios_dia)
                if dia in self.ejercicios_completados:
                    for ejercicio, completado in self.ejercicios_completados[dia].items():
                        if completado:
                            puntos += get_puntos(ejercicio)
                            completados += 1
                if dia in self.km_corridos:
                    km += float(self.km_corridos[dia])
            semana_ano = fecha.isocalendar()[1]
            meta_km = self.meta_km.get(str(semana_ano), 0.0)
            recompensas = []
            if km >= meta_km and meta_km > 0:
                recompensas.append("¡Cumpliste tu meta de km!")
            if puntos > self.record_puntos:
                self.record_puntos = puntos
                self.guardar_datos()
                recompensas.append("¡Nuevo récord de puntos!")
            if puntos >= 150:
                ranking = "Mega Crack"
                imagen_ranking = "/static/mega_crack.png"
            elif puntos >= 100:
                ranking = "Chill"
                imagen_ranking = "/static/chill.png"
            elif puntos >= 50:
                ranking = "Noob"
                imagen_ranking = "/static/noob.png"
            else:
                ranking = "Looser"
                imagen_ranking = "/static/looser.png"
            estadisticas = {
                'porcentaje_completados': (completados / totales * 100) if totales > 0 else 0,
                'km_porcentaje': (km / meta_km * 100) if meta_km > 0 else 0
            }
            print(f"[DEBUG] Evaluación semana {semana_ano}: puntos={puntos}, km={km}, completados={completados}, totales={totales}, ranking={ranking}")
            return puntos, km, completados, totales, recompensas, ranking, imagen_ranking, self.record_puntos, estadisticas
        except Exception as e:
            print(f"[DEBUG] Error en evaluar_semana: {str(e)}")
            return 0, 0.0, 0, 0, [], "Sin ranking", "", 0, {}

    def generar_resumen(self, puntos, km, completados, totales, recompensas, ranking, imagen_ranking, record_puntos, meta_km):
        try:
            porcentaje = (completados / totales * 100) if totales > 0 else 0
            texto = f"Resumen de la semana:\n"
            texto += f"- Puntos: {puntos} (Récord: {record_puntos})\n"
            texto += f"- Ejercicios completados: {completados}/{totales} ({porcentaje:.1f}%)\n"
            texto += f"- Kilómetros corridos: {km:.1f}/{meta_km:.1f} km\n"
            texto += f"- Ranking: {ranking}\n"
            if recompensas:
                texto += "- Recompensas:\n" + "\n".join([f"  * {r}" for r in recompensas])
            return texto
        except Exception as e:
            print(f"[DEBUG] Error en generar_resumen: {str(e)}")
            return "Error al generar el resumen."
