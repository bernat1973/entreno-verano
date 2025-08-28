import firebase_admin
from firebase_admin import credentials, firestore
from datetime import date, timedelta, datetime
import os
import random

class Modelo:
    def __init__(self, config_file='entreno_verano.json', use_auth=False):
        try:
            project_id = os.getenv("FIREBASE_PROJECT_ID")
            client_email = os.getenv("FIREBASE_CLIENT_EMAIL")
            private_key = os.getenv("FIREBASE_PRIVATE_KEY")
            print(f"[DEBUG] FIREBASE_PROJECT_ID: {project_id}")
            print(f"[DEBUG] FIREBASE_CLIENT_EMAIL: {client_email}")
            print(f"[DEBUG] FIREBASE_PRIVATE_KEY: {'[present]' if private_key else 'None'}")
            print(f"[DEBUG] Longitud de FIREBASE_PRIVATE_KEY: {len(private_key) if private_key else 0}")

            if not all([project_id, client_email, private_key]):
                raise ValueError("Faltan variables de entorno de Firebase")

            cred = credentials.Certificate({
                "type": "service_account",
                "project_id": project_id,
                "private_key": private_key.replace('\\n', '\n'),
                "client_email": client_email,
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "client_id": "your-client-id",
                "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/your-service-account-email"
            })
            firebase_admin.initialize_app(cred)
            self.db = firestore.client()

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
            self.recompensas_usadas = {}
            self.cargar_datos()
        except Exception as e:
            print(f"[DEBUG] Error al inicializar Modelo: {str(e)}")
            raise

    def cargar_datos(self):
        try:
            print(f"[DEBUG] Cargando datos para user_id: {self.user_id}")
            if not self.user_id:
                print("[DEBUG] self.user_id no está definido, usando 'Juan' como predeterminado")
                self.user_id = 'Juan'
                config_ref = self.db.collection('config').document('app')
                config_ref.set({'usuario_actual': self.user_id}, merge=True)

            user_ref = self.db.collection('usuarios').document(self.user_id)
            user_data = user_ref.get()
            if user_data.exists:
                data = user_data.to_dict()
                self.nombre = data.get('nombre', '')
                self.peso = data.get('peso', 0.0)
                self.estatura = data.get('estatura', 0.0)
                self.meta_km = data.get('meta_km', {})
                self.ejercicios_type = data.get('ejercicios_type', 'bodyweight')
                self.km_corridos = data.get('km_corridos', {})
                self.ejercicios_completados = data.get('ejercicios_completados', {})
                self.ejercicios_personalizados = data.get('ejercicios_personalizados', [])
                self.ejercicios_personalizados_por_fecha = data.get('ejercicios_personalizados_por_fecha', {})
                self.historial_semanal = data.get('historial_semanal', [])
                self.record_puntos = data.get('record_puntos', 0)
                self.mensaje = data.get('mensaje', '')
                self.recompensas_usadas = data.get('recompensas_usadas', {})
                print(f"[DEBUG] Datos cargados para usuario {self.user_id}: nombre={self.nombre}, ejercicios_type={self.ejercicios_type}")
            else:
                print(f"[DEBUG] No se encontraron datos para {self.user_id}, inicializando como nuevo usuario")
                self.nuevo_usuario(self.user_id)
            print(f"[DEBUG] Datos finales para {self.user_id}: nombre={self.nombre}, peso={self.peso}")
        except Exception as e:
            print(f"[DEBUG] Error al cargar datos para {self.user_id}: {str(e)}")
            raise

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
                'mensaje': self.mensaje,
                'recompensas_usadas': self.recompensas_usadas
            })
            config_ref = self.db.collection('config').document('app')
            config_ref.set({'usuario_actual': self.user_id}, merge=True)
            print(f"[DEBUG] Datos guardados para usuario {self.user_id}")
        except Exception as e:
            print(f"[DEBUG] Error al guardar datos: {str(e)}")
            raise

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
        self.recompensas_usadas = {}
        self.guardar_datos()

    def cambiar_usuario(self, user_id):
        try:
            print(f"[DEBUG] Intentando cambiar a usuario: {user_id}")
            if not user_id or user_id not in self.get_usuarios():
                print(f"[DEBUG] Usuario {user_id} no encontrado o inválido. Usuarios disponibles: {self.get_usuarios()}")
                raise ValueError(f"Usuario '{user_id}' no encontrado en la lista: {self.get_usuarios()}")

            old_user_id = self.user_id
            self.user_id = user_id
            print(f"[DEBUG] user_id actualizado a {self.user_id} antes de cargar datos")

            self.cargar_datos()
            print(f"[DEBUG] Datos recargados para {self.user_id}: nombre={self.nombre}, peso={self.peso}")

            if self.user_id != old_user_id:
                print(f"[DEBUG] Cambio a usuario {self.user_id} realizado exitosamente")
            self.guardar_datos()
            return self.user_id != old_user_id
        except Exception as e:
            print(f"[DEBUG] Error al cambiar usuario {user_id}: {str(e)}")
            self.user_id = old_user_id if 'old_user_id' in locals() else self.user_id
            raise

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
            if ejercicio not in self.ejercicios_personalizados:
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
                    print(f"[DEBUG] Ejercicios completados para {dia}: {self.ejercicios_completados[dia]}")
                    for ejercicio, completado in self.ejercicios_completados[dia].items():
                        if completado:
                            puntos_ejercicio = get_puntos(ejercicio) if get_puntos else 5
                            print(f"[DEBUG] Puntos para {ejercicio} ({completado}): {puntos_ejercicio}")
                            puntos += puntos_ejercicio
                            completados += 1
                if dia in self.km_corridos:
                    km += float(self.km_corridos[dia])
            semana_ano = fecha.isocalendar()[1]
            meta_km = self.meta_km.get(str(semana_ano), 0.0)
            recompensas = []
            if km >= meta_km and meta_km > 0:
                recompensas.append("¡Meta de km alcanzada!")
            if puntos > self.record_puntos:
                self.record_puntos = puntos
                self.guardar_datos()
                recompensas.append("¡Nuevo récord de puntos!")

            frases_animadoras = {
                "Semidios": ["¡Eres un dios del entreno!", "¡Dominas el gimnasio!"],
                "Crack": ["¡Eres un crack!", "¡Sigue así, campeón!"],
                "Chill": ["¡Buen trabajo, chill!", "¡Relájate y disfruta!"],
                "Noob": ["¡Sigue practicando, noob!", "¡Mejora poco a poco!"],
                "Looser": ["¡Anímate, looser!", "¡No te rindas!"]
            }
            recompensas_categoria = {
                "Semidios": ["Gana un día libre de entreno", "Elige tu próxima meta especial"],
                "Crack": ["Disfruta de un batido proteico", "Descansa con una película favorita"],
                "Chill": ["Toma un smoothie saludable", "Escucha tu playlist de motivación"],
                "Noob": ["Prueba un nuevo ejercicio divertido", "Gana 15 min extra de descanso"],
                "Looser": ["¡Sigue intentándolo, recompensa sorpresa pronto!", "Elige un amigo para entrenar"]
            }

            semana_actual = inicio_semana.strftime('%Y-%W')
            if semana_actual not in self.recompensas_usadas:
                self.recompensas_usadas[semana_actual] = []

            # Limpiar recompensas de semanas antiguas (mantener solo la semana actual)
            self.recompensas_usadas = {semana_actual: self.recompensas_usadas.get(semana_actual, [])}

            # Asignar categoría según puntos
            if puntos >= 150:
                recompensa_categoria = "Semidios"
            elif puntos >= 100:
                recompensa_categoria = "Crack"
            elif puntos >= 50:
                recompensa_categoria = "Chill"
            elif puntos >= 25:
                recompensa_categoria = "Noob"
            else:
                recompensa_categoria = "Looser"

            # Seleccionar una frase animadora única
            frases_disponibles = [f for f in frases_animadoras[recompensa_categoria] 
                                if f not in self.recompensas_usadas[semana_actual]]
            frase_animadora = random.choice(frases_disponibles) if frases_disponibles else random.choice(frases_animadoras[recompensa_categoria])

            # Seleccionar una recompensa única
            recompensas_disponibles = [r for r in recompensas_categoria[recompensa_categoria] 
                                    if r not in self.recompensas_usadas[semana_actual]]
            recompensa = random.choice(recompensas_disponibles) if recompensas_disponibles else random.choice(recompensas_categoria[recompensa_categoria])

            # Añadir solo la frase y la recompensa seleccionadas
            self.recompensas_usadas[semana_actual].append(frase_animadora)
            self.recompensas_usadas[semana_actual].append(recompensa)
            self.guardar_datos()

            recompensas = [frase_animadora, recompensa]  # Reemplazar en lugar de extender

            imagen_ranking = f"recompensas/{recompensa_categoria.lower()}.png"
            ranking = recompensa_categoria

            estadisticas = {
                'porcentaje_completados': (completados / totales * 100) if totales > 0 else 0,
                'km_porcentaje': (km / meta_km * 100) if meta_km > 0 else 0
            }
            print(f"[DEBUG] Evaluación semana {semana_ano}: puntos={puntos}, km={km}, completados={completados}, totales={totales}, ranking={ranking}, recompensas={recompensas}")
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
