from flask import Flask, render_template, request, redirect, url_for, send_file
from datetime import datetime, date, timedelta
from modelo import Modelo
from ejercicios import Ejercicios
from firebase_config import save_json, get_json
from generar_pdf import generar_pdf_progreso 
import json
import os

app = Flask(__name__)

# Definir la ruta del archivo en /tmp/ como caché temporal
ARCHIVO_JSON = '/tmp/entreno_verano.json'

# Cargar datos desde Firestore como fuente principal
try:
    data_from_firebase = get_json()
    if data_from_firebase:
        with open(ARCHIVO_JSON, 'w', encoding='utf-8') as f:
            json.dump(data_from_firebase[0], f, indent=4, ensure_ascii=False)
        modelo = Modelo(ARCHIVO_JSON)
        print(f"Datos iniciales cargados desde Firestore: {data_from_firebase[0]}")
    else:
        print("No se encontraron datos en Firestore, inicializando modelo vacío")
        modelo = Modelo(ARCHIVO_JSON)
except Exception as e:
    print(f"Error al cargar datos desde Firestore: {str(e)}")
    modelo = Modelo(ARCHIVO_JSON)

ejercicios = Ejercicios(modelo)

# Filtros personalizados para fechas
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
    if request.method == 'POST':
        try:
            nombre = request.form['nombre'].strip()
            peso = float(request.form.get('peso', 0))
            estatura = float(request.form.get('estatura', 0))
            meta_km = float(request.form['meta_km'])
            if not nombre:
                return render_template('datos_personales.html', nombre=modelo.nombre, peso=modelo.peso, estatura=modelo.estatura, meta_km=modelo.meta_km.get(semana_ano, 0), error="El nombre no puede estar vacío.", semana_actual=semana_actual, usuarios=usuarios)
            if peso < 0 or estatura < 0 or meta_km < 0:
                return render_template('datos_personales.html', nombre=modelo.nombre, peso=modelo.peso, estatura=modelo.estatura, meta_km=modelo.meta_km.get(semana_ano, 0), error="Peso, estatura y meta de km deben ser positivos.", semana_actual=semana_actual, usuarios=usuarios)
            if nombre not in modelo.usuarios:
                modelo.nuevo_usuario(nombre)
            modelo.nombre = nombre
            modelo.peso = peso
            modelo.estatura = estatura
            modelo.meta_km[semana_ano] = meta_km
            modelo.usuario_actual = nombre
            print(f"Antes de guardar_datos: usuarios={modelo.usuarios}, usuario_actual={modelo.usuario_actual}, peso={modelo.peso}, estatura={modelo.estatura}, meta_km={modelo.meta_km}")
            modelo.guardar_datos()
            with open(ARCHIVO_JSON, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"Datos escritos en {ARCHIVO_JSON}: {data}")
            if not save_json(data):
                raise Exception("Fallo al sincronizar con Firestore")
            modelo.cargar_datos()
            print(f"Datos recargados en modelo: usuarios={modelo.usuarios}, usuario_actual={modelo.usuario_actual}")
            data_from_firebase = get_json()
            print(f"Datos verificados en Firestore: {data_from_firebase}")
            return render_template('datos_personales.html', nombre=modelo.nombre, peso=modelo.peso, estatura=modelo.estatura, meta_km=modelo.meta_km.get(semana_ano, 0), mensaje="¡Datos guardados correctamente!", semana_actual=semana_actual, usuarios=usuarios)
        except ValueError as e:
            return render_template('datos_personales.html', nombre=modelo.nombre, peso=modelo.peso, estatura=modelo.estatura, meta_km=modelo.meta_km.get(semana_ano, 0), error="Valores inválidos. Revisa los datos.", semana_actual=semana_actual, usuarios=usuarios)
        except Exception as e:
            print(f"Excepción en /datos_personales: {str(e)}")
            return render_template('datos_personales.html', nombre=modelo.nombre, peso=modelo.peso, estatura=modelo.estatura, meta_km=modelo.meta_km.get(semana_ano, 0), error=f"Error interno: {str(e)}. Revisa los logs.", semana_actual=semana_actual, usuarios=usuarios)
    return render_template('datos_personales.html', nombre=modelo.nombre, peso=modelo.peso, estatura=modelo.estatura, meta_km=modelo.meta_km.get(semana_ano, 0), semana_actual=semana_actual, usuarios=usuarios)

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
        print(f"Recibido nuevo_usuario: {nuevo_nombre}")
        if not nuevo_nombre:
            return render_template('datos_personales.html', nombre=modelo.nombre, peso=modelo.peso, estatura=modelo.estatura, meta_km=modelo.meta_km.get(semana_ano, 0), error="El nombre no puede estar vacío.", semana_actual=semana_actual, usuarios=usuarios)
        modelo.nuevo_usuario(nuevo_nombre)
        print(f"Antes de guardar_datos: usuarios={modelo.usuarios}, usuario_actual={modelo.usuario_actual}")
        modelo.guardar_datos()
        with open(ARCHIVO_JSON, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"Datos escritos en {ARCHIVO_JSON}: {data}")
        if not save_json(data):
            raise Exception("Fallo al sincronizar con Firestore")
        modelo.cargar_datos()
        print(f"Datos recargados en modelo: usuarios={modelo.usuarios}, usuario_actual={modelo.usuario_actual}")
        return render_template('datos_personales.html', nombre=modelo.nombre, peso=modelo.peso, estatura=modelo.estatura, meta_km=modelo.meta_km.get(semana_ano, 0), mensaje=f"¡Usuario '{nuevo_nombre}' creado correctamente!", semana_actual=semana_actual, usuarios=usuarios)
    except ValueError as e:
        print(f"ValueError en /nuevo_usuario: {str(e)}")
        return render_template('datos_personales.html', nombre=modelo.nombre, peso=modelo.peso, estatura=modelo.estatura, meta_km=modelo.meta_km.get(semana_ano, 0), error=str(e), semana_actual=semana_actual, usuarios=usuarios)
    except Exception as e:
        print(f"Excepción no manejada en /nuevo_usuario: {str(e)}")
        return render_template('datos_personales.html', nombre=modelo.nombre, peso=modelo.peso, estatura=modelo.estatura, meta_km=modelo.meta_km.get(semana_ano, 0), error="Error interno al crear usuario. Revisa los logs.", semana_actual=semana_actual, usuarios=usuarios)

@app.route('/cambiar_usuario', methods=['POST'])
def cambiar_usuario():
    semana_ano = str(datetime.now().isocalendar()[1])
    hoy = date.today()
    inicio_semana = hoy - timedelta(days=hoy.weekday())
    fin_semana = inicio_semana + timedelta(days=6)
    semana_actual = f"Semana {semana_ano}: del {inicio_semana.strftime('%d/%m/%Y')} al {fin_semana.strftime('%d/%m/%Y')}"
    usuarios = modelo.get_usuarios()
    try:
        nombre_usuario = request.form.get('usuario').strip()
        if not nombre_usuario:
            return render_template('datos_personales.html', nombre=modelo.nombre, peso=modelo.peso, estatura=modelo.estatura, meta_km=modelo.meta_km.get(semana_ano, 0), error="Selecciona un usuario.", semana_actual=semana_actual, usuarios=usuarios)
        modelo.cambiar_usuario(nombre_usuario)
        print(f"Antes de guardar_datos: usuarios={modelo.usuarios}, usuario_actual={modelo.usuario_actual}")
        modelo.guardar_datos()
        with open(ARCHIVO_JSON, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"Datos escritos en {ARCHIVO_JSON}: {data}")
        if not save_json(data):
            raise Exception("Fallo al sincronizar con Firestore")
        modelo.cargar_datos()
        print(f"Datos recargados en modelo: usuarios={modelo.usuarios}, usuario_actual={modelo.usuario_actual}")
        return render_template('datos_personales.html', nombre=modelo.nombre, peso=modelo.peso, estatura=modelo.estatura, meta_km=modelo.meta_km.get(semana_ano, 0), mensaje=f"¡Cambiado a usuario '{nombre_usuario}'!", semana_actual=semana_actual, usuarios=usuarios)
    except ValueError as e:
        return render_template('datos_personales.html', nombre=modelo.nombre, peso=modelo.peso, estatura=modelo.estatura, meta_km=modelo.meta_km.get(semana_ano, 0), error=str(e), semana_actual=semana_actual, usuarios=usuarios)

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
            modelo.ejercicios_completados[fecha_str] = {}
            ejercicios_dia = ejercicios.get_ejercicios_dia(fecha)
            for ejercicio in ejercicios_dia:
                base_ejercicio = ejercicios.get_base_exercise_name(ejercicio)
                modelo.ejercicios_completados[fecha_str][base_ejercicio] = ejercicio in ejercicios_seleccionados
            print(f"Antes de guardar_datos: ejercicios_completados={modelo.ejercicios_completados}")
            modelo.guardar_datos()
            with open(ARCHIVO_JSON, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"Datos escritos en {ARCHIVO_JSON}: {data}")
            if not save_json(data):
                raise Exception("Fallo al sincronizar con Firestore")
            modelo.cargar_datos()
            print(f"Datos recargados en modelo: ejercicios_completados={modelo.ejercicios_completados}")
            puntos_totales = sum(ejercicios.get_puntos(ejercicios.get_base_exercise_name(ejercicio)) for ejercicio in ejercicios_dia if modelo.ejercicios_completados.get(fecha_str, {}).get(ejercicios.get_base_exercise_name(ejercicio), False))
            print(f"Guardado en {fecha_str}: {modelo.ejercicios_completados[fecha_str]}")
            print(f"Puntos calculados: {puntos_totales}")
            fecha_anterior = (fecha - timedelta(days=1)).strftime('%Y-%m-%d')
            fecha_siguiente = (fecha + timedelta(days=1)).strftime('%Y-%m-%d')
            return render_template('entreno.html', mensaje="¡Ejercicios guardados correctamente!", fecha=fecha_str, ejercicios=ejercicios_dia, puntos_totales=puntos_totales, modelo=modelo, ejercicios_obj=ejercicios, fecha_anterior=fecha_anterior, fecha_siguiente=fecha_siguiente)
        else:
            fecha_str = request.args.get('fecha', date.today().strftime('%Y-%m-%d'))
            fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date() if fecha_str else date.today()
            fecha_str = fecha.strftime('%Y-%m-%d')
            ejercicios_dia = ejercicios.get_ejercicios_dia(fecha)
            puntos_totales = sum(ejercicios.get_puntos(ejercicios.get_base_exercise_name(ejercicio)) for ejercicio in ejercicios_dia if modelo.ejercicios_completados.get(fecha_str, {}).get(ejercicios.get_base_exercise_name(ejercicio), False))
            print(f"Cargando {fecha_str}: {modelo.ejercicios_completados.get(fecha_str, {})}")
            print(f"Puntos calculados: {puntos_totales}")
            fecha_anterior = (fecha - timedelta(days=1)).strftime('%Y-%m-%d')
            fecha_siguiente = (fecha + timedelta(days=1)).strftime('%Y-%m-%d')
            return render_template('entreno.html', fecha=fecha_str, ejercicios=ejercicios_dia, puntos_totales=puntos_totales, modelo=modelo, ejercicios_obj=ejercicios, fecha_anterior=fecha_anterior, fecha_siguiente=fecha_siguiente)
    except Exception as e:
        print(f"Error en entreno: {str(e)}")
        fecha_anterior = date.today().strftime('%Y-%m-%d')
        fecha_siguiente = date.today().strftime('%Y-%m-%d')
        return render_template('entreno.html', error=f"Error: {str(e)}", fecha=date.today().strftime('%Y-%m-%d'), ejercicios=None, puntos_totales=0, modelo=modelo, ejercicios_obj=ejercicios, fecha_anterior=fecha_anterior, fecha_siguiente=fecha_siguiente)

@app.route('/correr', methods=['GET', 'POST'])
def correr():
    try:
        fecha_str = request.args.get('fecha', date.today().strftime('%Y-%m-%d')) if request.method == 'GET' else request.form.get('fecha')
        fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date() if fecha_str else date.today()
        fecha_str = fecha.strftime('%Y-%m-%d')
        km_dia = modelo.km_corridos.get(fecha_str, 0.0)
        km_por_dia = modelo.km_corridos
        semana_ano = fecha.isocalendar()[1]
        meta_km = modelo.meta_km.get(str(semana_ano), 0.0)
        inicio_semana = fecha - timedelta(days=fecha.weekday())
        fin_semana = inicio_semana + timedelta(days=6)
        km_semanal = sum(float(km) for fecha, km in modelo.km_corridos.items() if inicio_semana.strftime('%Y-%m-%d') <= fecha <= fin_semana.strftime('%Y-%m-%d'))
        semanas = []
        for i in range(-1, 3):
            semana_inicio = inicio_semana + timedelta(days=i*7)
            semana_fin = semana_inicio + timedelta(days=6)
            km_semana = sum(float(km) for fecha, km in modelo.km_corridos.items() if semana_inicio.strftime('%Y-%m-%d') <= fecha <= semana_fin.strftime('%Y-%m-%d'))
            semanas.append({
                'inicio_semana': semana_inicio.strftime('%Y-%m-%d'),
                'fin_semana': semana_fin.strftime('%Y-%m-%d'),
                'km': round(km_semana, 2)
            })
        print(f"Correr - Fecha: {fecha_str}, km_dia: {km_dia}, km_por_dia: {km_por_dia}, km_semanal: {km_semanal}, meta_km: {meta_km}, semanas: {semanas}")
        if request.method == 'POST':
            accion = request.form.get('accion')
            if accion == 'registrar':
                km = float(request.form.get('km', 0))
                if km < 0:
                    return render_template('correr.html', error="Los kilómetros deben ser positivos.", fecha=fecha_str, km_semanal=km_semanal, meta_km=meta_km, semanas=semanas, km_por_dia=km_por_dia, km_dia=km_dia)
                modelo.km_corridos[fecha_str] = modelo.km_corridos.get(fecha_str, 0.0) + km
                print(f"Antes de guardar_datos: km_corridos={modelo.km_corridos}")
                modelo.guardar_datos()
                with open(ARCHIVO_JSON, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                print(f"Datos escritos en {ARCHIVO_JSON}: {data}")
                if not save_json(data):
                    raise Exception("Fallo al sincronizar con Firestore")
                modelo.cargar_datos()
                print(f"Datos recargados en modelo: km_corridos={modelo.km_corridos}")
                km_dia = modelo.km_corridos.get(fecha_str, 0.0)
                km_por_dia = modelo.km_corridos
                km_semanal = sum(float(km) for fecha, km in modelo.km_corridos.items() if inicio_semana.strftime('%Y-%m-%d') <= fecha <= fin_semana.strftime('%Y-%m-%d'))
                semanas = []
                for i in range(-1, 3):
                    semana_inicio = inicio_semana + timedelta(days=i*7)
                    semana_fin = semana_inicio + timedelta(days=6)
                    km_semana = sum(float(km) for fecha, km in modelo.km_corridos.items() if semana_inicio.strftime('%Y-%m-%d') <= fecha <= semana_fin.strftime('%Y-%m-%d'))
                    semanas.append({
                        'inicio_semana': semana_inicio.strftime('%Y-%m-%d'),
                        'fin_semana': semana_fin.strftime('%Y-%m-%d'),
                        'km': round(km_semana, 2)
                    })
                print(f"Post registrar - Fecha: {fecha_str}, km_dia: {km_dia}, km_por_dia: {km_por_dia}, km_semanal: {km_semanal}, semanas: {semanas}")
                return render_template('correr.html', mensaje="¡Kilómetros registrados correctamente!", fecha=fecha_str, km_semanal=km_semanal, meta_km=meta_km, semanas=semanas, km_por_dia=km_por_dia, km_dia=km_dia)
            elif accion == 'eliminar':
                fecha_eliminar = request.form.get('fecha_eliminar')
                if fecha_eliminar in modelo.km_corridos:
                    del modelo.km_corridos[fecha_eliminar]
                    print(f"Antes de guardar_datos: km_corridos={modelo.km_corridos}")
                    modelo.guardar_datos()
                    with open(ARCHIVO_JSON, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    print(f"Datos escritos en {ARCHIVO_JSON}: {data}")
                    if not save_json(data):
                        raise Exception("Fallo al sincronizar con Firestore")
                modelo.cargar_datos()
                print(f"Datos recargados en modelo: km_corridos={modelo.km_corridos}")
                km_por_dia = modelo.km_corridos
                km_dia = modelo.km_corridos.get(fecha_str, 0.0)
                km_semanal = sum(float(km) for fecha, km in modelo.km_corridos.items() if inicio_semana.strftime('%Y-%m-%d') <= fecha <= fin_semana.strftime('%Y-%m-%d'))
                semanas = []
                for i in range(-1, 3):
                    semana_inicio = inicio_semana + timedelta(days=i*7)
                    semana_fin = semana_inicio + timedelta(days=6)
                    km_semana = sum(float(km) for fecha, km in modelo.km_corridos.items() if semana_inicio.strftime('%Y-%m-%d') <= fecha <= semana_fin.strftime('%Y-%m-%d'))
                    semanas.append({
                        'inicio_semana': semana_inicio.strftime('%Y-%m-%d'),
                        'fin_semana': semana_fin.strftime('%Y-%m-%d'),
                        'km': round(km_semana, 2)
                    })
                print(f"Post eliminar - Fecha: {fecha_str}, km_dia: {km_dia}, km_por_dia: {km_por_dia}, km_semanal: {km_semanal}, semanas: {semanas}")
                return render_template('correr.html', mensaje="Registro eliminado correctamente.", fecha=fecha_str, km_semanal=km_semanal, meta_km=meta_km, semanas=semanas, km_por_dia=km_por_dia, km_dia=km_dia)
        return render_template('correr.html', fecha=fecha_str, km_semanal=km_semanal, meta_km=meta_km, semanas=semanas, km_por_dia=km_por_dia, km_dia=km_dia)
    except Exception as e:
        print(f"Error en correr: {str(e)}")
        return render_template('correr.html', error=f"Error: {str(e)}", fecha=date.today().strftime('%Y-%m-%d'), km_semanal=0, meta_km=0, semanas=[], km_por_dia={}, km_dia=0)

@app.route('/anadir_ejercicio', methods=['GET', 'POST'])
def anadir_ejercicio():
    try:
        fecha_str = request.args.get('fecha', date.today().strftime('%Y-%m-%d'))
        if request.method == 'POST':
            ejercicio = request.form['ejercicio'].strip()
            fecha_str = request.form.get('fecha', date.today().strftime('%Y-%m-%d'))
            if not ejercicio:
                return render_template('anadir_ejercicio.html', error="El ejercicio no puede estar vacío.", fecha=fecha_str)
            print(f"Antes de anadir_ejercicio_personalizado: ejercicios_personalizados={modelo.ejercicios_personalizados}")
            modelo.anadir_ejercicio_personalizado(ejercicio, fecha_str)
            print(f"Después de anadir_ejercicio_personalizado: ejercicios_personalizados={modelo.ejercicios_personalizados}")
            modelo.guardar_datos()
            with open(ARCHIVO_JSON, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"Datos escritos en {ARCHIVO_JSON}: {data}")
            if not save_json(data):
                raise Exception("Fallo al sincronizar con Firestore")
            modelo.cargar_datos()
            print(f"Datos recargados en modelo: ejercicios_personalizados={modelo.ejercicios_personalizados}")
            return redirect(url_for('entreno', fecha=fecha_str))
        return render_template('anadir_ejercicio.html', fecha=fecha_str)
    except Exception as e:
        print(f"Error en anadir_ejercicio: {str(e)}")
        return render_template('anadir_ejercicio.html', error=f"Error: {str(e)}", fecha=date.today().strftime('%Y-%m-%d'))

@app.route('/progreso')
def progreso():
    try:
        fecha_str = request.args.get('fecha', date.today().strftime('%Y-%m-%d'))
        fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        puntos, km, completados, totales, recompensas, ranking, imagen_ranking, record_puntos, estadisticas = modelo.evaluar_semana(ejercicios.get_ejercicios_dia, fecha, ejercicios.get_puntos)
        semanas_puntos = []
        semanas_km = []
        semanas_totales_completados = []
        inicio_semana = fecha - timedelta(days=fecha.weekday())
        for i in range(-1, 3):
            semana_inicio = inicio_semana + timedelta(days=i*7)
            semana_fin = semana_inicio + timedelta(days=6)
            puntos_semana, km_semana, completados_semana, totales_semana, _, _, _, _, _ = modelo.evaluar_semana(ejercicios.get_ejercicios_dia, semana_inicio, ejercicios.get_puntos)
            semanas_puntos.append({
                'inicio_semana': semana_inicio.strftime('%Y-%m-%d'),
                'fin_semana': semana_fin.strftime('%Y-%m-%d'),
                'puntos': puntos_semana
            })
            semanas_km.append({
                'inicio_semana': semana_inicio.strftime('%Y-%m-%d'),
                'fin_semana': semana_fin.strftime('%Y-%m-%d'),
                'km': round(km_semana, 2)
            })
            semanas_totales_completados.append({
                'completados': completados_semana,
                'totales': totales_semana
            })
        print(f"Progreso - Fecha: {fecha_str}, Puntos: {puntos}, Completados: {completados}/{totales}, Estadísticas: {estadisticas}, Semanas puntos: {semanas_puntos}, Semanas km: {semanas_km}, Semanas completados: {semanas_totales_completados}")
        return render_template('progreso.html', puntos=puntos, km=km, completados=completados, totales=totales, fecha=fecha_str, recompensas=recompensas, ranking=ranking, imagen_ranking=imagen_ranking, record_puntos=record_puntos, estadisticas=estadisticas, semanas_puntos=semanas_puntos, semanas_km=semanas_km, semanas_totales_completados=semanas_totales_completados)
    except Exception as e:
        print(f"Error en progreso: {str(e)}")
        return render_template('progreso.html', error=f"Error: {str(e)}", puntos=0, km=0, completados=0, totales=0, fecha=date.today().strftime('%Y-%m-%d'), recompensas=[], ranking="Sin ranking", imagen_ranking="", record_puntos=0, estadisticas={}, semanas_puntos=[], semanas_km=[], semanas_totales_completados=[])

@app.route('/resumen')
def resumen():
    try:
        fecha_str = request.args.get('fecha', date.today().strftime('%Y-%m-%d'))
        fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        puntos, km, completados, totales, recompensas, ranking, imagen_ranking, record_puntos, _ = modelo.evaluar_semana(ejercicios.get_ejercicios_dia, fecha, ejercicios.get_puntos)
        texto_resumen = modelo.generar_resumen(puntos, km, completados, totales, recompensas, ranking, imagen_ranking, record_puntos, modelo.meta_km.get(str(fecha.isocalendar()[1]), 0))
        print(f"Resumen - Fecha: {fecha_str}, Puntos: {puntos}, Ranking: {ranking}, Texto: {texto_resumen}")
        return render_template('resumen.html', texto_resumen=texto_resumen, fecha=fecha_str, puntos=puntos, ranking=ranking, imagen_ranking=imagen_ranking, record_puntos=record_puntos, recompensas=recompensas)
    except Exception as e:
        print(f"Error en resumen: {str(e)}")
        return render_template('resumen.html', error=f"Error: {str(e)}", texto_resumen="Error al generar el resumen.", fecha=date.today().strftime('%Y-%m-%d'), puntos=0, ranking="Sin ranking", imagen_ranking="", record_puntos=0, recompensas=[])

# NUEVA RUTA PARA PDF DE PROGRESO
@app.route('/informe_pdf', methods=['GET', 'POST'])
def informe_pdf():
    mensaje = None
    if request.method == 'POST':
        fecha_inicio = request.form.get('fecha_inicio')
        fecha_fin = request.form.get('fecha_fin')
        output_path = f"/tmp/progreso_{modelo.nombre}.pdf"
        try:
            generar_pdf_progreso(modelo, fecha_inicio, fecha_fin, output_path)
            mensaje = "PDF generado correctamente."
            return send_file(output_path, as_attachment=True)
        except Exception as e:
            mensaje = f"Error al generar PDF: {e}"
    return render_template('informe_pdf.html', mensaje=mensaje)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)
