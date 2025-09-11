# app.py
from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime, date, timedelta
from modelo import Modelo
from ejercicios import Ejercicios
import logging

app = Flask(__name__)

# Configurar logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

modelo = Modelo('entreno_verano.json')
ejercicios = Ejercicios(modelo)

def _calcular_datos_grafica(historial_mediciones):
    logger.debug(f"Calculando datos_grafica con historial_mediciones: {historial_mediciones}")
    if not historial_mediciones or not isinstance(historial_mediciones, dict):
        logger.warning("historial_mediciones vacío o no válido, devolviendo lista vacía")
        return []

    datos_grafica = []
    historial_fechas = sorted(historial_mediciones.keys())
    for i, mes in enumerate(historial_fechas):
        medicion_actual = historial_mediciones[mes]
        estatura_actual_cm = float(medicion_actual.get('estatura', 0)) * 100
        velocidad = 0
        if i > 0:
            mes_anterior = historial_fechas[i-1]
            medicion_anterior = historial_mediciones[mes_anterior]
            diferencia_estatura = float(medicion_actual.get('estatura', 0)) - float(medicion_anterior.get('estatura', 0))
            velocidad = diferencia_estatura * 100
        datos_grafica.append({
            'mes': mes or 'Sin fecha',
            'estatura': round(estatura_actual_cm, 2),
            'velocidad': round(velocidad, 2)
        })
    logger.debug(f"datos_grafica calculado: {datos_grafica}")
    return datos_grafica

@app.template_filter('datetimeformat')
def datetimeformat(value, format='%Y-%m-%d'):
    if isinstance(value, str):
        try:
            dt = datetime.strptime(value, '%Y-%m-%d')
            return dt.strftime(format)
        except ValueError:
            return value
    return value

@app.template_filter('datetimeparse')
def datetimeparse(value):
    if isinstance(value, str):
        try:
            return datetime.strptime(value, '%Y-%m-%d').date()
        except ValueError:
            return value
    return value

@app.route('/', methods=['GET'])
def index():
    semana_ano = str(datetime.now().isocalendar()[1])
    hoy = date.today()
    inicio_semana = hoy - timedelta(days=hoy.weekday())
    fin_semana = inicio_semana + timedelta(days=6)
    semana_actual = f"Semana {semana_ano}: del {inicio_semana.strftime('%d/%m/%Y')} al {fin_semana.strftime('%d/%m/%Y')}"
    return render_template('index.html', semana_actual=semana_actual)

@app.route('/datos_personales', methods=['GET', 'POST'])
def datos_personales():
    semana_ano = str(datetime.now().isocalendar()[1])
    hoy = date.today()
    inicio_semana = hoy - timedelta(days=hoy.weekday())
    fin_semana = inicio_semana + timedelta(days=6)
    semana_actual = f"Semana {semana_ano}: del {inicio_semana.strftime('%d/%m/%Y')} al {fin_semana.strftime('%d/%m/%Y')}"
    usuarios = modelo.get_usuarios()
    logger.debug(f"Usuarios disponibles: {usuarios}")

    if request.method == 'POST':
        try:
            nombre = request.form['nombre'].strip()
            peso = float(request.form.get('peso', 0))
            estatura = float(request.form.get('estatura', 0)) / 100
            talla_sentada = float(request.form.get('talla_sentada', 0)) / 100
            envergadura = float(request.form.get('envergadura', 0)) / 100
            meta_km = float(request.form.get('meta_km', 0))
            ejercicios_type = request.form.get('ejercicios_type', 'bodyweight')
            mes_medicion = request.form.get('mes_medicion', date.today().strftime('%Y-%m'))

            if not nombre:
                return render_template('datos_personales.html', nombre=modelo.nombre, peso=modelo.peso, estatura=modelo.estatura * 100 if modelo.estatura else 0, talla_sentada=modelo.talla_sentada * 100 if modelo.talla_sentada else 0, envergadura=modelo.envergadura * 100 if modelo.envergadura else 0, meta_km=modelo.meta_km.get(semana_ano, 0), ejercicios_type=modelo.ejercicios_type, error="El nombre no puede estar vacío.", semana_actual=semana_actual, usuarios=usuarios, mes_medicion=mes_medicion, datos_grafica=[])

            if peso < 0 or estatura < 0 or talla_sentada < 0 or envergadura < 0 or meta_km < 0:
                return render_template('datos_personales.html', nombre=modelo.nombre, peso=modelo.peso, estatura=modelo.estatura * 100 if modelo.estatura else 0, talla_sentada=modelo.talla_sentada * 100 if modelo.talla_sentada else 0, envergadura=modelo.envergadura * 100 if modelo.envergadura else 0, meta_km=modelo.meta_km.get(semana_ano, 0), ejercicios_type=modelo.ejercicios_type, error="Los valores deben ser positivos.", semana_actual=semana_actual, usuarios=usuarios, mes_medicion=mes_medicion, datos_grafica=[])

            modelo.nombre = nombre
            modelo.peso = peso
            modelo.estatura = estatura
            modelo.talla_sentada = talla_sentada
            modelo.envergadura = envergadura
            modelo.meta_km[semana_ano] = meta_km
            modelo.ejercicios_type = ejercicios_type
            modelo.historial_mediciones[mes_medicion] = {
                'estatura': estatura, 'peso': peso,
                'talla_sentada': talla_sentada, 'envergadura': envergadura
            }
            modelo.guardar_datos()

            segmento_inferior = estatura - talla_sentada if estatura and talla_sentada else 0
            imc = peso / (estatura ** 2) if estatura and peso else 0
            datos_grafica = _calcular_datos_grafica(modelo.historial_mediciones) or []
            return render_template('datos_personales.html', nombre=modelo.nombre, peso=modelo.peso, estatura=estatura * 100, talla_sentada=talla_sentada * 100, envergadura=envergadura * 100, meta_km=modelo.meta_km.get(semana_ano, 0), ejercicios_type=modelo.ejercicios_type, mensaje="¡Datos guardados correctamente!", semana_actual=semana_actual, usuarios=usuarios, segmento_inferior=segmento_inferior * 100, imc=imc, mes_medicion=mes_medicion, datos_grafica=datos_grafica)
        except ValueError as e:
            logger.error(f"Error en /datos_personales: {str(e)}")
            return render_template('datos_personales.html', nombre=modelo.nombre, peso=modelo.peso, estatura=modelo.estatura * 100 if modelo.estatura else 0, talla_sentada=modelo.talla_sentada * 100 if modelo.talla_sentada else 0, envergadura=modelo.envergadura * 100 if modelo.envergadura else 0, meta_km=modelo.meta_km.get(semana_ano, 0), ejercicios_type=modelo.ejercicios_type, error=f"Error en los datos: {str(e)}", semana_actual=semana_actual, usuarios=usuarios, mes_medicion=date.today().strftime('%Y-%m'), datos_grafica=[])
        except Exception as e:
            logger.error(f"Error interno en /datos_personales: {str(e)}")
            return render_template('datos_personales.html', nombre=modelo.nombre, peso=modelo.peso, estatura=modelo.estatura * 100 if modelo.estatura else 0, talla_sentada=modelo.talla_sentada * 100 if modelo.talla_sentada else 0, envergadura=modelo.envergadura * 100 if modelo.envergadura else 0, meta_km=modelo.meta_km.get(semana_ano, 0), ejercicios_type=modelo.ejercicios_type, error=f"Error interno: {str(e)}", semana_actual=semana_actual, usuarios=usuarios, mes_medicion=date.today().strftime('%Y-%m'), datos_grafica=[])

    segmento_inferior = (modelo.estatura - modelo.talla_sentada) * 100 if modelo.estatura and modelo.talla_sentada else 0
    imc = modelo.peso / (modelo.estatura ** 2) if modelo.estatura and modelo.peso else 0
    datos_grafica = _calcular_datos_grafica(modelo.historial_mediciones) or []
    return render_template('datos_personales.html', nombre=modelo.nombre, peso=modelo.peso, estatura=modelo.estatura * 100 if modelo.estatura else 0, talla_sentada=modelo.talla_sentada * 100 if modelo.talla_sentada else 0, envergadura=modelo.envergadura * 100 if modelo.envergadura else 0, meta_km=modelo.meta_km.get(semana_ano, 0), ejercicios_type=modelo.ejercicios_type, semana_actual=semana_actual, usuarios=usuarios, segmento_inferior=segmento_inferior, imc=imc, mes_medicion=date.today().strftime('%Y-%m'), datos_grafica=datos_grafica)

@app.route('/cambiar_usuario', methods=['POST'])
def cambiar_usuario():
    semana_ano = str(datetime.now().isocalendar()[1])
    hoy = date.today()
    inicio_semana = hoy - timedelta(days=hoy.weekday())
    fin_semana = inicio_semana + timedelta(days=6)
    semana_actual = f"Semana {semana_ano}: del {inicio_semana.strftime('%d/%m/%Y')} al {fin_semana.strftime('%d/%m/%Y')}"
    usuarios = modelo.get_usuarios()
    logger.debug(f"Usuarios disponibles en /cambiar_usuario: {usuarios}")

    try:
        nombre_usuario = request.form['usuario'].strip()
        logger.debug(f"Solicitud para cambiar a usuario: {nombre_usuario}")
        if not nombre_usuario or nombre_usuario not in usuarios:
            error = "Selecciona un usuario válido."
            logger.error(f"Error: {error}")
            return render_template('datos_personales.html', nombre="", peso=0, estatura=0, talla_sentada=0, envergadura=0, meta_km=0, ejercicios_type='bodyweight', error=error, semana_actual=semana_actual, usuarios=usuarios, mes_medicion=date.today().strftime('%Y-%m'), datos_grafica=[])

        if modelo.cambiar_usuario(nombre_usuario):
            segmento_inferior = (modelo.estatura - modelo.talla_sentada) * 100 if modelo.estatura and modelo.talla_sentada else 0
            imc = modelo.peso / (modelo.estatura ** 2) if modelo.estatura and modelo.peso else 0
            datos_grafica = _calcular_datos_grafica(modelo.historial_mediciones) or []
            logger.debug(f"Cambio exitoso a {nombre_usuario}. Estado: nombre={modelo.nombre}, peso={modelo.peso}, estatura={modelo.estatura}")
            return render_template('datos_personales.html', nombre=modelo.nombre, peso=modelo.peso, estatura=modelo.estatura * 100 if modelo.estatura else 0, talla_sentada=modelo.talla_sentada * 100 if modelo.talla_sentada else 0, envergadura=modelo.envergadura * 100 if modelo.envergadura else 0, meta_km=modelo.meta_km.get(semana_ano, 0), ejercicios_type=modelo.ejercicios_type, mensaje=f"¡Cambiado a usuario '{nombre_usuario}'!", semana_actual=semana_actual, usuarios=usuarios, segmento_inferior=segmento_inferior, imc=imc, mes_medicion=date.today().strftime('%Y-%m'), datos_grafica=datos_grafica)
        else:
            error = f"Error al cambiar a usuario '{nombre_usuario}'."
            logger.error(f"Error: {error}")
            return render_template('datos_personales.html', error=error, semana_actual=semana_actual, usuarios=usuarios, nombre="", peso=0, estatura=0, talla_sentada=0, envergadura=0, meta_km=0, ejercicios_type='bodyweight', mes_medicion=date.today().strftime('%Y-%m'), datos_grafica=[])

    except Exception as e:
        logger.error(f"Excepción en /cambiar_usuario: {str(e)}")
        return render_template('datos_personales.html', error=f"Error al cambiar usuario: {str(e)}", semana_actual=semana_actual, usuarios=usuarios, nombre="", peso=0, estatura=0, talla_sentada=0, envergadura=0, meta_km=0, ejercicios_type='bodyweight', mes_medicion=date.today().strftime('%Y-%m'), datos_grafica=[])

@app.route('/nuevo_usuario', methods=['POST'])
def nuevo_usuario():
    semana_ano = str(datetime.now().isocalendar()[1])
    hoy = date.today()
    inicio_semana = hoy - timedelta(days=hoy.weekday())
    fin_semana = inicio_semana + timedelta(days=6)
    semana_actual = f"Semana {semana_ano}: del {inicio_semana.strftime('%d/%m/%Y')} al {fin_semana.strftime('%d/%m/%Y')}"
    usuarios = modelo.get_usuarios()
    try:
        nuevo_nombre = request.form.get('nuevo_usuario').strip()
        if not nuevo_nombre:
            return render_template('datos_personales.html', nombre=modelo.nombre, peso=modelo.peso, estatura=modelo.estatura * 100 if modelo.estatura else 0, talla_sentada=modelo.talla_sentada * 100 if modelo.talla_sentada else 0, envergadura=modelo.envergadura * 100 if modelo.envergadura else 0, meta_km=modelo.meta_km.get(semana_ano, 0), ejercicios_type=modelo.ejercicios_type, error="El nombre no puede estar vacío.", semana_actual=semana_actual, usuarios=usuarios, mes_medicion=date.today().strftime('%Y-%m'), datos_grafica=[])
        if nuevo_nombre in usuarios:
            return render_template('datos_personales.html', nombre=modelo.nombre, peso=modelo.peso, estatura=modelo.estatura * 100 if modelo.estatura else 0, talla_sentada=modelo.talla_sentada * 100 if modelo.talla_sentada else 0, envergadura=modelo.envergadura * 100 if modelo.envergadura else 0, meta_km=modelo.meta_km.get(semana_ano, 0), ejercicios_type=modelo.ejercicios_type, error="El usuario ya existe.", semana_actual=semana_actual, usuarios=usuarios, mes_medicion=date.today().strftime('%Y-%m'), datos_grafica=[])
        modelo.nuevo_usuario(nuevo_nombre)
        usuarios_actualizados = modelo.get_usuarios()
        return render_template('datos_personales.html', nombre=modelo.nombre, peso=modelo.peso, estatura=modelo.estatura * 100 if modelo.estatura else 0, talla_sentada=modelo.talla_sentada * 100 if modelo.talla_sentada else 0, envergadura=modelo.envergadura * 100 if modelo.envergadura else 0, meta_km=modelo.meta_km.get(semana_ano, 0), ejercicios_type=modelo.ejercicios_type, mensaje=f"¡Usuario '{nuevo_nombre}' creado correctamente!", semana_actual=semana_actual, usuarios=usuarios_actualizados, mes_medicion=date.today().strftime('%Y-%m'), datos_grafica=[])
    except Exception as e:
        logger.error(f"Error al crear nuevo usuario: {str(e)}")
        return render_template('datos_personales.html', nombre=modelo.nombre, peso=modelo.peso, estatura=modelo.estatura * 100 if modelo.estatura else 0, talla_sentada=modelo.talla_sentada * 100 if modelo.talla_sentada else 0, envergadura=modelo.envergadura * 100 if modelo.envergadura else 0, meta_km=modelo.meta_km.get(semana_ano, 0), ejercicios_type=modelo.ejercicios_type, error=f"Error interno: {str(e)}", semana_actual=semana_actual, usuarios=usuarios, mes_medicion=date.today().strftime('%Y-%m'), datos_grafica=[])

@app.route('/entreno', methods=['GET', 'POST'])
def entreno():
    try:
        if request.method == 'POST':
            fecha_str = request.form.get('fecha')
            ejercicios_seleccionados = request.form.getlist('ejercicios')
            if not fecha_str:
                return render_template('entreno.html', error="Selecciona una fecha válida.", fecha=date.today().strftime('%Y-%m-%d'), ejercicios=[], puntos_totales=0, modelo=modelo, ejercicios_obj=ejercicios, fecha_anterior=date.today().strftime('%Y-%m-%d'), fecha_siguiente=date.today().strftime('%Y-%m-%d'))
            fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
            fecha_str = fecha.strftime('%Y-%m-%d')
            ejercicios_dia = ejercicios.get_ejercicios_dia(fecha, modelo.historial_semanal)
            if ejercicios_dia is None or not ejercicios_dia:
                logger.warning(f"No se encontraron ejercicios para la fecha {fecha_str}. Usando lista vacía.")
                ejercicios_dia = []
            ejercicios_dict = {ejercicios.get_base_exercise_name(ej): (ej in ejercicios_seleccionados) for ej in ejercicios_dia}
            modelo.registrar_ejercicios(fecha, ejercicios_dict)
            modelo.guardar_datos()
            puntos_totales = sum(ejercicios.get_puntos(ejercicios.get_base_exercise_name(ejercicio)) for ejercicio in ejercicios_dia if modelo.ejercicios_completados.get(fecha_str, {}).get(ejercicios.get_base_exercise_name(ejercicio), False))
            fecha_anterior = (fecha - timedelta(days=1)).strftime('%Y-%m-%d')
            fecha_siguiente = (fecha + timedelta(days=1)).strftime('%Y-%m-%d')
            return render_template('entreno.html', mensaje="¡Ejercicios guardados correctamente!", fecha=fecha_str, ejercicios=ejercicios_dia, puntos_totales=puntos_totales, modelo=modelo, ejercicios_obj=ejercicios, fecha_anterior=fecha_anterior, fecha_siguiente=fecha_siguiente, ejercicios_type=modelo.ejercicios_type)
        else:
            fecha_str = request.args.get('fecha', date.today().strftime('%Y-%m-%d'))
            fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date() if fecha_str else date.today()
            fecha_str = fecha.strftime('%Y-%m-%d')
            ejercicios_dia = ejercicios.get_ejercicios_dia(fecha, modelo.historial_semanal)
            if ejercicios_dia is None or not ejercicios_dia:
                logger.warning(f"No se encontraron ejercicios para la fecha {fecha_str}. Usando lista vacía.")
                ejercicios_dia = []
            puntos_totales = sum(ejercicios.get_puntos(ejercicios.get_base_exercise_name(ejercicio)) for ejercicio in ejercicios_dia if modelo.ejercicios_completados.get(fecha_str, {}).get(ejercicios.get_base_exercise_name(ejercicio), False))
            fecha_anterior = (fecha - timedelta(days=1)).strftime('%Y-%m-%d')
            fecha_siguiente = (fecha + timedelta(days=1)).strftime('%Y-%m-%d')
            return render_template('entreno.html', fecha=fecha_str, ejercicios=ejercicios_dia, puntos_totales=puntos_totales, modelo=modelo, ejercicios_obj=ejercicios, fecha_anterior=fecha_anterior, fecha_siguiente=fecha_siguiente, ejercicios_type=modelo.ejercicios_type)
    except Exception as e:
        logger.error(f"Error en /entreno: {str(e)}")
        return render_template('error.html', error=f"Error al cargar entreno: {str(e)}"), 500

@app.route('/anadir_ejercicio', methods=['GET', 'POST'])
def anadir_ejercicio():
    try:
        fecha_str = request.args.get('fecha', date.today().strftime('%Y-%m-%d'))
        fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        if request.method == 'POST':
            ejercicio = request.form.get('ejercicio')
            if not ejercicio or not ejercicio.strip():
                return render_template('anadir_ejercicio.html', error="El ejercicio no puede estar vacío.", fecha=fecha_str)
            ejercicio_limpio = ejercicio.strip()
            modelo.anadir_ejercicio_personalizado(fecha, ejercicio_limpio)
            modelo.guardar_datos()
            return redirect(url_for('entreno', fecha=fecha_str))
        return render_template('anadir_ejercicio.html', fecha=fecha_str)
    except Exception as e:
        logger.error(f"Error en /anadir_ejercicio: {str(e)}")
        return render_template('error.html', error=f"Error al añadir ejercicio: {str(e)}"), 500

@app.route('/correr', methods=['GET', 'POST'])
def correr():
    try:
        fecha_str = request.args.get('fecha', date.today().strftime('%Y-%m-%d')) if request.method == 'GET' else request.form.get('fecha')
        fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date() if fecha_str else date.today()
        fecha_str = fecha.strftime('%Y-%m-%d')
        km_dia = modelo.km_corridos.get(fecha_str, 0.0)
        tiempo_dia = modelo.tiempo_corridos.get(fecha_str, 0.0)
        km_por_dia = modelo.km_corridos
        tiempo_por_dia = modelo.tiempo_corridos
        semana_ano = fecha.isocalendar()[1]
        meta_km = modelo.meta_km.get(str(semana_ano), 0.0)
        inicio_semana = fecha - timedelta(days=fecha.weekday())
        fin_semana = inicio_semana + timedelta(days=6)
        km_semanal = sum(float(km) for fecha_key, km in modelo.km_corridos.items() if inicio_semana.strftime('%Y-%m-%d') <= fecha_key <= fin_semana.strftime('%Y-%m-%d'))
        tiempo_semanal = sum(float(t) for fecha_key, t in modelo.tiempo_corridos.items() if inicio_semana.strftime('%Y-%m-%d') <= fecha_key <= fin_semana.strftime('%Y-%m-%d'))
        semanas = []
        for i in range(-1, 3):
            semana_inicio = inicio_semana + timedelta(days=i*7)
            semana_fin = semana_inicio + timedelta(days=6)
            km_semana = sum(float(km) for fecha_key, km in modelo.km_corridos.items() if semana_inicio.strftime('%Y-%m-%d') <= fecha_key <= semana_fin.strftime('%Y-%m-%d'))
            tiempo_semana = sum(float(t) for fecha_key, t in modelo.tiempo_corridos.items() if semana_inicio.strftime('%Y-%m-%d') <= fecha_key <= semana_fin.strftime('%Y-%m-%d'))
            semanas.append({
                'inicio_semana': semana_inicio.strftime('%Y-%m-%d'),
                'fin_semana': semana_fin.strftime('%Y-%m-%d'),
                'km': round(km_semana, 2),
                'tiempo': round(tiempo_semana, 2)
            })
        if request.method == 'POST':
            accion = request.form.get('accion')
            if accion == 'registrar':
                km = float(request.form.get('km', 0))
                tiempo_str = request.form.get('tiempo', '0:00')
                try:
                    minutos, segundos = map(int, tiempo_str.split(':'))
                    if minutos < 0 or segundos < 0 or segundos >= 60:
                        raise ValueError("Los segundos deben estar entre 0 y 59, y los minutos no pueden ser negativos.")
                    tiempo_segundos = minutos * 60 + segundos
                except ValueError as e:
                    return render_template('correr.html', error=f"Formato de tiempo inválido. Usa 'minutos:segundos' (ejemplo: '15:30'). Error: {str(e)}", fecha=fecha_str, km_semanal=km_semanal, tiempo_semanal=tiempo_semanal, meta_km=meta_km, semanas=semanas, km_por_dia=km_por_dia, tiempo_por_dia=tiempo_por_dia, km_dia=km_dia, tiempo_dia=tiempo_dia)
                if km < 0:
                    return render_template('correr.html', error="Los kilómetros deben ser un valor positivo.", fecha=fecha_str, km_semanal=km_semanal, tiempo_semanal=tiempo_semanal, meta_km=meta_km, semanas=semanas, km_por_dia=km_por_dia, tiempo_por_dia=tiempo_por_dia, km_dia=km_dia, tiempo_dia=tiempo_dia)
                
                modelo.registrar_km(fecha_str, modelo.km_corridos.get(fecha_str, 0.0) + km)
                modelo.registrar_tiempo(fecha_str, modelo.tiempo_corridos.get(fecha_str, 0.0) + tiempo_segundos)
                modelo.guardar_datos()
                km_semanal = sum(float(km) for fecha_key, km in modelo.km_corridos.items() if inicio_semana.strftime('%Y-%m-%d') <= fecha_key <= fin_semana.strftime('%Y-%m-%d'))
                tiempo_semanal = sum(float(t) for fecha_key, t in modelo.tiempo_corridos.items() if inicio_semana.strftime('%Y-%m-%d') <= fecha_key <= fin_semana.strftime('%Y-%m-%d'))
                km_dia = modelo.km_corridos.get(fecha_str, 0.0)
                tiempo_dia = modelo.tiempo_corridos.get(fecha_str, 0.0)
                return render_template('correr.html', mensaje="¡Kilómetros y tiempo registrados!", fecha=fecha_str, km_semanal=round(km_semanal, 2), tiempo_semanal=round(tiempo_semanal, 2), meta_km=meta_km, semanas=semanas, km_por_dia=km_por_dia, tiempo_por_dia=tiempo_por_dia, km_dia=km_dia, tiempo_dia=tiempo_dia)
            elif accion == 'eliminar':
                if fecha_str in modelo.km_corridos:
                    del modelo.km_corridos[fecha_str]
                    del modelo.tiempo_corridos[fecha_str]
                    modelo.guardar_datos()
                    km_semanal = sum(float(km) for fecha_key, km in modelo.km_corridos.items() if inicio_semana.strftime('%Y-%m-%d') <= fecha_key <= fin_semana.strftime('%Y-%m-%d'))
                    tiempo_semanal = sum(float(t) for fecha_key, t in modelo.tiempo_corridos.items() if inicio_semana.strftime('%Y-%m-%d') <= fecha_key <= fin_semana.strftime('%Y-%m-%d'))
                    km_dia = 0.0
                    tiempo_dia = 0.0
                    return render_template('correr.html', mensaje="¡Datos del día eliminados!", fecha=fecha_str, km_semanal=round(km_semanal, 2), tiempo_semanal=round(tiempo_semanal, 2), meta_km=meta_km, semanas=semanas, km_por_dia=km_por_dia, tiempo_por_dia=tiempo_por_dia, km_dia=km_dia, tiempo_dia=tiempo_dia)
        return render_template('correr.html', fecha=fecha_str, km_semanal=round(km_semanal, 2), tiempo_semanal=round(tiempo_semanal, 2), meta_km=meta_km, semanas=semanas, km_por_dia=km_por_dia, tiempo_por_dia=tiempo_por_dia, km_dia=km_dia, tiempo_dia=tiempo_dia)
    except Exception as e:
        logger.error(f"Error en /correr: {str(e)}")
        return render_template('error.html', error=f"Error al cargar la página de correr: {str(e)}"), 500

@app.route('/progreso', methods=['GET'])
def progreso():
    try:
        hoy = date.today()
        inicio_semana = hoy - timedelta(days=hoy.weekday())
        semanas_puntos = []
        for i in range(-3, 1):
            semana_inicio = inicio_semana + timedelta(days=i*7)
            semana_fin = semana_inicio + timedelta(days=6)
            puntos, km, completados, totales, recompensas, ranking, imagen_ranking, record_puntos, estadisticas = modelo.evaluar_semana(ejercicios.get_ejercicios_dia, semana_inicio, ejercicios.get_puntos)
            semanas_puntos.append({
                'inicio_semana': semana_inicio.strftime('%Y-%m-%d'),
                'fin_semana': semana_fin.strftime('%Y-%m-%d'),
                'puntos': puntos or 0,
                'km': km or 0
            })

        puntos, km, completados, totales, recompensas, ranking, imagen_ranking, record_puntos, estadisticas = modelo.evaluar_semana(ejercicios.get_ejercicios_dia, inicio_semana, ejercicios.get_puntos)

        return render_template('progreso.html', puntos=puntos, km=km, completados=completados, totales=totales, ranking=ranking, imagen_ranking=imagen_ranking, record_puntos=record_puntos, estadisticas=estadisticas, fecha=hoy.strftime('%d/%m/%Y'), semanas_puntos=semanas_puntos)
    except Exception as e:
        logger.error(f"Error en /progreso: {str(e)}")
        return render_template('error.html', error=f"Error al cargar progreso: {str(e)}"), 500

@app.route('/resumen', methods=['GET', 'POST'])
def resumen():
    try:
        hoy = date.today()
        inicio_semana = hoy - timedelta(days=hoy.weekday())
        semana_seleccionada = request.form.get('semana_seleccionada', '')

        if semana_seleccionada:
            inicio_semana = datetime.strptime(semana_seleccionada, '%Y-%m-%d').date()
        fin_semana = inicio_semana + timedelta(days=6)

        resultado_semana = modelo.evaluar_semana(ejercicios.get_ejercicios_dia, inicio_semana, ejercicios.get_puntos)
        if len(resultado_semana) != 9:
            raise ValueError(f"Esperados 9 valores de evaluar_semana, recibidos: {len(resultado_semana)}")
        puntos, km, completados, totales, recompensas, ranking, imagen_ranking, record_puntos, estadisticas = resultado_semana
        resumen = modelo.generar_resumen(puntos, km, completados, totales, recompensas, ranking, imagen_ranking, record_puntos, modelo.meta_km.get(str(hoy.isocalendar()[1]), 0.0))

        semanas_pasadas = []
        for i in range(-4, 1):
            semana_inicio = hoy - timedelta(days=(hoy.weekday() + 7 * (i + 1)))
            semana_fin = semana_inicio + timedelta(days=6)
            semanas_pasadas.append({
                'inicio_semana': semana_inicio.strftime('%Y-%m-%d'),
                'fin_semana': semana_fin.strftime('%d/%m/%Y')
            })

        semanas_puntos = []
        semanas_km = []
        for i in range(-3, 1):
            semana_inicio = inicio_semana + timedelta(days=i*7)
            semana_fin = semana_inicio + timedelta(days=6)
            puntos_semana, km_semana, _, _, _, _, _, _, _ = modelo.evaluar_semana(ejercicios.get_ejercicios_dia, semana_inicio, ejercicios.get_puntos)
            km_semana_total = sum(float(km) for fecha_key, km in modelo.km_corridos.items() if semana_inicio.strftime('%Y-%m-%d') <= fecha_key <= semana_fin.strftime('%Y-%m-%d'))
            semanas_puntos.append({
                'inicio_semana': semana_inicio.strftime('%Y-%m-%d'),
                'fin_semana': semana_fin.strftime('%Y-%m-%d'),
                'puntos': puntos_semana or 0
            })
            semanas_km.append({
                'inicio_semana': semana_inicio.strftime('%Y-%m-%d'),
                'fin_semana': semana_fin.strftime('%Y-%m-%d'),
                'km': round(km_semana_total, 2) or 0
            })

        datos_grafica = _calcular_datos_grafica(modelo.historial_mediciones) or []
        logger.debug(f"En /resumen: resumen={resumen}, semanas_puntos={semanas_puntos}, semanas_km={semanas_km}, datos_grafica={datos_grafica}")

        return render_template('resumen.html', resumen=resumen, imagen_ranking=imagen_ranking, estadisticas=estadisticas, fecha=f"{inicio_semana.strftime('%d/%m/%Y')} - {fin_semana.strftime('%d/%m/%Y')}", puntos=puntos, record_puntos=record_puntos, recompensas=recompensas, ranking=ranking, semanas_puntos=semanas_puntos, semanas_km=semanas_km, modelo=modelo, datos_grafica=datos_grafica, semanas_pasadas=semanas_pasadas, semana_seleccionada=semana_seleccionada)
    except Exception as e:
        logger.error(f"Error en /resumen: {str(e)}")
        return render_template('error.html', error=f"Error al generar resumen: {str(e)}"), 500

@app.route('/informe_semanal', methods=['GET'])
def informe_semanal():
    try:
        hoy = date.today()
        inicio_semana = hoy - timedelta(days=hoy.weekday())

        informe = {}
        semanas_puntos = []
        semanas_km = []
        for i in range(-3, 1):
            semana_inicio = inicio_semana + timedelta(days=i*7)
            semana_fin = semana_inicio + timedelta(days=6)
            semana_str = f"{semana_inicio.strftime('%d/%m/%Y')} - {semana_fin.strftime('%d/%m/%Y')}"
            informe[semana_str] = {
                'pectorales': [], 'espalda': [], 'abdominales': [], 'hombros': [],
                'brazos': [], 'piernas': [], 'core': [], 'otros': []
            }

            for dia in (semana_inicio + timedelta(days=d) for d in range(7)):
                dia_str = dia.strftime('%Y-%m-%d')
                if dia_str in modelo.ejercicios_completados:
                    for ejercicio, completado in modelo.ejercicios_completados[dia_str].items():
                        if completado:
                            base_name = ejercicios.get_base_exercise_name(ejercicio)
                            base_name_lower = base_name.lower() if base_name else ""
                            grupo = 'otros'
                            if base_name_lower:
                                if any(keyword in base_name_lower for keyword in ['pectorales', 'pecho', 'press de banca', 'apertura', 'cruces', 'flexiones', 'push-up']):
                                    grupo = 'pectorales'
                                elif any(keyword in base_name_lower for keyword in ['espalda', 'remo', 'dominada', 'pull-over', 'jalón']):
                                    grupo = 'espalda'
                                elif any(keyword in base_name_lower for keyword in ['abdominal', 'abdominales', 'crunch', 'elevación de piernas']):
                                    grupo = 'abdominales'
                                elif any(keyword in base_name_lower for keyword in ['hombros', 'elevaciones', 'press militar', 'press de hombros']):
                                    grupo = 'hombros'
                                elif any(keyword in base_name_lower for keyword in ['bíceps', 'tríceps', 'curl', 'extensiones', 'fondos']):
                                    grupo = 'brazos'
                                elif any(keyword in base_name_lower for keyword in ['piernas', 'sentadilla', 'zancadas', 'peso muerto']):
                                    grupo = 'piernas'
                                elif any(keyword in base_name_lower for keyword in ['plancha', 'core', 'escaladores', 'puente']):
                                    grupo = 'core'
                            informe[semana_str][grupo].append(base_name or "Ejercicio desconocido")

            puntos_semana, km_semana, _, _, _, _, _, _, _ = modelo.evaluar_semana(ejercicios.get_ejercicios_dia, semana_inicio, ejercicios.get_puntos)
            km_semana_total = sum(float(km) for fecha_key, km in modelo.km_corridos.items() if semana_inicio.strftime('%Y-%m-%d') <= fecha_key <= semana_fin.strftime('%Y-%m-%d'))
            semanas_puntos.append({
                'inicio_semana': semana_inicio.strftime('%Y-%m-%d'),
                'fin_semana': semana_fin.strftime('%Y-%m-%d'),
                'puntos': puntos_semana or 0
            })
            semanas_km.append({
                'inicio_semana': semana_inicio.strftime('%Y-%m-%d'),
                'fin_semana': semana_fin.strftime('%Y-%m-%d'),
                'km': round(km_semana_total, 2) or 0
            })

        datos_grafica = _calcular_datos_grafica(modelo.historial_mediciones) or []
        logger.debug(f"En /informe_semanal: informe={informe}, semanas_puntos={semanas_puntos}, semanas_km={semanas_km}, datos_grafica={datos_grafica}")

        return render_template('informe_semanal.html', informe=informe or {}, fecha=hoy.strftime('%d/%m/%Y'), semanas_puntos=semanas_puntos or [], semanas_km=semanas_km or [], datos_grafica=datos_grafica or [])
    except Exception as e:
        logger.error(f"Error en /informe_semanal: {str(e)}")
        return render_template('error.html', error=f"Error al generar informe: {str(e)}"), 500

@app.route('/recompensas', methods=['GET'])
def redirigir_recompensas():
    return redirect(url_for('resumen'))

if __name__ == '__main__':
    app.run(debug=True)
