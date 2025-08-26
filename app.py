from flask import Flask, render_template, request, redirect, url_for, send_file
from datetime import datetime, date, timedelta
from modelo import Modelo
from ejercicios import Ejercicios
from generar_pdf import generar_pdf_progreso

app = Flask(__name__)
modelo = Modelo('entreno_verano.json')
ejercicios = Ejercicios(modelo)

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
    hoy = date.today()
    inicio_semana = hoy - timedelta(days=hoy.weekday())
    fin_semana = inicio_semana + timedelta(days=6)
    semana_actual = f"Semana {hoy.isocalendar()[1]}: del {inicio_semana.strftime('%d/%m/%Y')} al {fin_semana.strftime('%d/%m/%Y')}"
    return render_template('index.html', semana_actual=semana_actual)

@app.route('/datos_personales', methods=['GET', 'POST'])
def datos_personales():
    hoy = date.today()
    inicio_semana = hoy - timedelta(days=hoy.weekday())
    fin_semana = inicio_semana + timedelta(days=6)
    semana_ano = str(hoy.isocalendar()[1])
    semana_actual = f"Semana {semana_ano}: del {inicio_semana.strftime('%d/%m/%Y')} al {fin_semana.strftime('%d/%m/%Y')}"
    usuarios = modelo.get_usuarios()
    if request.method == 'POST':
        try:
            nombre = request.form['nombre'].strip()
            peso = float(request.form.get('peso', 0))
            estatura = float(request.form.get('estatura', 0))
            meta_km = float(request.form.get('meta_km', 0))
            ejercicios_type = request.form.get('ejercicios_type', 'bodyweight')
            if not nombre:
                return render_template('datos_personales.html', nombre=modelo.nombre, peso=modelo.peso, estatura=modelo.estatura, meta_km=modelo.meta_km.get(semana_ano, 0), ejercicios_type=modelo.ejercicios_type, error="El nombre no puede estar vacío.", semana_actual=semana_actual, usuarios=usuarios)
            if peso < 0 or estatura < 0 or meta_km < 0:
                return render_template('datos_personales.html', nombre=modelo.nombre, peso=modelo.peso, estatura=modelo.estatura, meta_km=modelo.meta_km.get(semana_ano, 0), ejercicios_type=modelo.ejercicios_type, error="Peso, estatura y meta de km deben ser positivos.", semana_actual=semana_actual, usuarios=usuarios)
            modelo.nombre = nombre
            modelo.peso = peso
            modelo.estatura = estatura
            modelo.meta_km[semana_ano] = meta_km
            modelo.ejercicios_type = ejercicios_type
            modelo.guardar_datos()
            return render_template('datos_personales.html', nombre=modelo.nombre, peso=modelo.peso, estatura=modelo.estatura, meta_km=modelo.meta_km.get(semana_ano, 0), ejercicios_type=modelo.ejercicios_type, mensaje="¡Datos guardados correctamente!", semana_actual=semana_actual, usuarios=usuarios)
        except ValueError as e:
            return render_template('datos_personales.html', nombre=modelo.nombre, peso=modelo.peso, estatura=modelo.estatura, meta_km=modelo.meta_km.get(semana_ano, 0), ejercicios_type=modelo.ejercicios_type, error=str(e), semana_actual=semana_actual, usuarios=usuarios)
    return render_template('datos_personales.html', nombre=modelo.nombre, peso=modelo.peso, estatura=modelo.estatura, meta_km=modelo.meta_km.get(semana_ano, 0), ejercicios_type=modelo.ejercicios_type, semana_actual=semana_actual, usuarios=usuarios)

@app.route('/cambiar_usuario', methods=['POST'])
def cambiar_usuario():
    hoy = date.today()
    inicio_semana = hoy - timedelta(days=hoy.weekday())
    fin_semana = inicio_semana + timedelta(days=6)
    semana_ano = str(hoy.isocalendar()[1])
    semana_actual = f"Semana {semana_ano}: del {inicio_semana.strftime('%d/%m/%Y')} al {fin_semana.strftime('%d/%m/%Y')}"
    usuarios = modelo.get_usuarios()
    try:
        nombre_usuario = request.form['usuario'].strip()
        if not nombre_usuario:
            return render_template('datos_personales.html', nombre=modelo.nombre, peso=modelo.peso, estatura=modelo.estatura, meta_km=modelo.meta_km.get(semana_ano, 0), ejercicios_type=modelo.ejercicios_type, error="Selecciona un usuario.", semana_actual=semana_actual, usuarios=usuarios)
        if nombre_usuario not in usuarios:
            return render_template('datos_personales.html', nombre=modelo.nombre, peso=modelo.peso, estatura=modelo.estatura, meta_km=modelo.meta_km.get(semana_ano, 0), ejercicios_type=modelo.ejercicios_type, error=f"Usuario '{nombre_usuario}' no encontrado en la lista: {usuarios}", semana_actual=semana_actual, usuarios=usuarios)
        if modelo.cambiar_usuario(nombre_usuario):
            modelo.guardar_datos()  # Asegurar que los datos se guarden tras el cambio
            return render_template('datos_personales.html', nombre=modelo.nombre, peso=modelo.peso, estatura=modelo.estatura, meta_km=modelo.meta_km.get(semana_ano, 0), ejercicios_type=modelo.ejercicios_type, mensaje=f"¡Cambiado a usuario '{nombre_usuario}'!", semana_actual=semana_actual, usuarios=usuarios)
        else:
            return render_template('datos_personales.html', nombre=modelo.nombre, peso=modelo.peso, estatura=modelo.estatura, meta_km=modelo.meta_km.get(semana_ano, 0), ejercicios_type=modelo.ejercicios_type, error=f"Error al cambiar a usuario '{nombre_usuario}'. Verifica los datos.", semana_actual=semana_actual, usuarios=usuarios)
    except ValueError as e:
        return render_template('datos_personales.html', nombre=modelo.nombre, peso=modelo.peso, estatura=modelo.estatura, meta_km=modelo.meta_km.get(semana_ano, 0), ejercicios_type=modelo.ejercicios_type, error=f"Error: {str(e)}", semana_actual=semana_actual, usuarios=usuarios)
    except Exception as e:
        return render_template('datos_personales.html', nombre=modelo.nombre, peso=modelo.peso, estatura=modelo.estatura, meta_km=modelo.meta_km.get(semana_ano, 0), ejercicios_type=modelo.ejercicios_type, error=f"Error inesperado: {str(e)}", semana_actual=semana_actual, usuarios=usuarios)

@app.route('/nuevo_usuario', methods=['POST'])
def nuevo_usuario():
    hoy = date.today()
    inicio_semana = hoy - timedelta(days=hoy.weekday())
    fin_semana = inicio_semana + timedelta(days=6)
    semana_ano = str(hoy.isocalendar()[1])
    semana_actual = f"Semana {semana_ano}: del {inicio_semana.strftime('%d/%m/%Y')} al {fin_semana.strftime('%d/%m/%Y')}"
    usuarios = modelo.get_usuarios()
    try:
        nuevo_nombre = request.form.get('nuevo_usuario', '').strip()
        if not nuevo_nombre:
            return render_template('datos_personales.html', nombre=modelo.nombre, peso=modelo.peso, estatura=modelo.estatura, meta_km=modelo.meta_km.get(semana_ano, 0), ejercicios_type=modelo.ejercicios_type, error="El nombre no puede estar vacío.", semana_actual=semana_actual, usuarios=usuarios)
        if nuevo_nombre in usuarios:
            return render_template('datos_personales.html', nombre=modelo.nombre, peso=modelo.peso, estatura=modelo.estatura, meta_km=modelo.meta_km.get(semana_ano, 0), ejercicios_type=modelo.ejercicios_type, error="El usuario ya existe.", semana_actual=semana_actual, usuarios=usuarios)
        modelo.nuevo_usuario(nuevo_nombre)
        modelo.guardar_datos()
        return render_template('datos_personales.html', nombre=modelo.nombre, peso=modelo.peso, estatura=modelo.estatura, meta_km=modelo.meta_km.get(semana_ano, 0), ejercicios_type=modelo.ejercicios_type, mensaje=f"¡Usuario '{nuevo_nombre}' creado correctamente!", semana_actual=semana_actual, usuarios=usuarios)
    except ValueError as e:
        return render_template('datos_personales.html', nombre=modelo.nombre, peso=modelo.peso, estatura=modelo.estatura, meta_km=modelo.meta_km.get(semana_ano, 0), ejercicios_type=modelo.ejercicios_type, error=str(e), semana_actual=semana_actual, usuarios=usuarios)

@app.route('/entreno', methods=['GET', 'POST'])
def entreno():
    hoy = date.today()
    inicio_semana = hoy - timedelta(days=hoy.weekday())
    fin_semana = inicio_semana + timedelta(days=6)
    semana_actual = f"Semana {hoy.isocalendar()[1]}: del {inicio_semana.strftime('%d/%m/%Y')} al {fin_semana.strftime('%d/%m/%Y')}"
    try:
        if request.method == 'POST':
            fecha_str = request.form.get('fecha')
            ejercicios_seleccionados = request.form.getlist('ejercicios')
            if not fecha_str:
                return render_template('entreno.html', error="Selecciona una fecha válida.", fecha=hoy.strftime('%Y-%m-%d'), ejercicios=[], puntos_totales=0, modelo=modelo, ejercicios_obj=ejercicios, fecha_anterior=hoy.strftime('%Y-%m-%d'), fecha_siguiente=hoy.strftime('%Y-%m-%d'), semana_actual=semana_actual)
            fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
            fecha_str = fecha.strftime('%Y-%m-%d')
            ejercicios_dia = ejercicios.get_ejercicios_dia(fecha, modelo.historial_semanal)
            ejercicios_dict = {ejercicios.get_base_exercise_name(ej): (ej in ejercicios_seleccionados) for ej in ejercicios_dia}
            modelo.registrar_ejercicios(fecha, ejercicios_dict)
            puntos_totales = sum(ejercicios.get_puntos(ejercicios.get_base_exercise_name(ejercicio)) for ejercicio in ejercicios_dia if modelo.ejercicios_completados.get(fecha_str, {}).get(ejercicios.get_base_exercise_name(ejercicio), False))
            fecha_anterior = (fecha - timedelta(days=1)).strftime('%Y-%m-%d')
            fecha_siguiente = (fecha + timedelta(days=1)).strftime('%Y-%m-%d')
            return render_template('entreno.html', mensaje="¡Ejercicios guardados correctamente!", fecha=fecha_str, ejercicios=ejercicios_dia, puntos_totales=puntos_totales, modelo=modelo, ejercicios_obj=ejercicios, fecha_anterior=fecha_anterior, fecha_siguiente=fecha_siguiente, semana_actual=semana_actual)
        else:
            fecha_str = request.args.get('fecha', hoy.strftime('%Y-%m-%d'))
            fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date() if fecha_str else hoy
            fecha_str = fecha.strftime('%Y-%m-%d')
            ejercicios_dia = ejercicios.get_ejercicios_dia(fecha, modelo.historial_semanal)
            puntos_totales = sum(ejercicios.get_puntos(ejercicios.get_base_exercise_name(ejercicio)) for ejercicio in ejercicios_dia if modelo.ejercicios_completados.get(fecha_str, {}).get(ejercicios.get_base_exercise_name(ejercicio), False))
            fecha_anterior = (fecha - timedelta(days=1)).strftime('%Y-%m-%d')
            fecha_siguiente = (fecha + timedelta(days=1)).strftime('%Y-%m-%d')
            return render_template('entreno.html', fecha=fecha_str, ejercicios=ejercicios_dia, puntos_totales=puntos_totales, modelo=modelo, ejercicios_obj=ejercicios, fecha_anterior=fecha_anterior, fecha_siguiente=fecha_siguiente, semana_actual=semana_actual)
    except Exception as e:
        fecha_anterior = hoy.strftime('%Y-%m-%d')
        fecha_siguiente = hoy.strftime('%Y-%m-%d')
        return render_template('entreno.html', error=f"Error: {str(e)}", fecha=hoy.strftime('%Y-%m-%d'), ejercicios=None, puntos_totales=0, modelo=modelo, ejercicios_obj=ejercicios, fecha_anterior=fecha_anterior, fecha_siguiente=fecha_siguiente, semana_actual=semana_actual)

@app.route('/correr', methods=['GET', 'POST'])
def correr():
    hoy = date.today()
    inicio_semana = hoy - timedelta(days=hoy.weekday())
    fin_semana = inicio_semana + timedelta(days=6)
    semana_actual = f"Semana {hoy.isocalendar()[1]}: del {inicio_semana.strftime('%d/%m/%Y')} al {fin_semana.strftime('%d/%m/%Y')}"
    try:
        fecha_str = request.args.get('fecha', hoy.strftime('%Y-%m-%d')) if request.method == 'GET' else request.form.get('fecha')
        fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date() if fecha_str else hoy
        fecha_str = fecha.strftime('%Y-%m-%d')
        km_dia = modelo.km_corridos.get(fecha_str, 0.0)
        km_por_dia = modelo.km_corridos
        semana_ano = fecha.isocalendar()[1]
        meta_km = modelo.meta_km.get(str(semana_ano), 0.0)
        inicio_semana = fecha - timedelta(days=fecha.weekday())
        fin_semana = inicio_semana + timedelta(days=6)
        km_semanal = sum(float(km) for fecha_key, km in modelo.km_corridos.items() if inicio_semana.strftime('%Y-%m-%d') <= fecha_key <= fin_semana.strftime('%Y-%m-%d'))
        semanas = []
        for i in range(-1, 3):
            semana_inicio = inicio_semana + timedelta(days=i*7)
            semana_fin = semana_inicio + timedelta(days=6)
            km_semana = sum(float(km) for fecha_key, km in modelo.km_corridos.items() if semana_inicio.strftime('%Y-%m-%d') <= fecha_key <= semana_fin.strftime('%Y-%m-%d'))
            semanas.append({
                'inicio_semana': semana_inicio.strftime('%Y-%m-%d'),
                'fin_semana': semana_fin.strftime('%Y-%m-%d'),
                'km': round(km_semana, 2)
            })
        if request.method == 'POST':
            accion = request.form.get('accion')
            if accion == 'registrar':
                km = float(request.form.get('km', 0))
                if km < 0:
                    return render_template('correr.html', error="Los kilómetros deben ser positivos.", fecha=fecha_str, km_semanal=km_semanal, meta_km=meta_km, semanas=semanas, km_por_dia=km_por_dia, km_dia=km_dia, semana_actual=semana_actual)
                modelo.registrar_km(fecha_str, modelo.km_corridos.get(fecha_str, 0.0) + km)
                km_dia = modelo.km_corridos.get(fecha_str, 0.0)
                km_por_dia = modelo.km_corridos
                km_semanal = sum(float(km) for fecha_key, km in modelo.km_corridos.items() if inicio_semana.strftime('%Y-%m-%d') <= fecha_key <= fin_semana.strftime('%Y-%m-%d'))
                semanas = []
                for i in range(-1, 3):
                    semana_inicio = inicio_semana + timedelta(days=i*7)
                    semana_fin = semana_inicio + timedelta(days=6)
                    km_semana = sum(float(km) for fecha_key, km in modelo.km_corridos.items() if semana_inicio.strftime('%Y-%m-%d') <= fecha_key <= semana_fin.strftime('%Y-%m-%d'))
                    semanas.append({
                        'inicio_semana': semana_inicio.strftime('%Y-%m-%d'),
                        'fin_semana': semana_fin.strftime('%Y-%m-%d'),
                        'km': round(km_semana, 2)
                    })
                return render_template('correr.html', mensaje="¡Kilómetros registrados correctamente!", fecha=fecha_str, km_semanal=km_semanal, meta_km=meta_km, semanas=semanas, km_por_dia=km_por_dia, km_dia=km_dia, semana_actual=semana_actual)
            elif accion == 'eliminar':
                fecha_eliminar = request.form.get('fecha_eliminar')
                modelo.eliminar_km(fecha_eliminar)
                km_por_dia = modelo.km_corridos
                km_dia = modelo.km_corridos.get(fecha_str, 0.0)
                km_semanal = sum(float(km) for fecha_key, km in modelo.km_corridos.items() if inicio_semana.strftime('%Y-%m-%d') <= fecha_key <= fin_semana.strftime('%Y-%m-%d'))
                semanas = []
                for i in range(-1, 3):
                    semana_inicio = inicio_semana + timedelta(days=i*7)
                    semana_fin = semana_inicio + timedelta(days=6)
                    km_semana = sum(float(km) for fecha_key, km in modelo.km_corridos.items() if semana_inicio.strftime('%Y-%m-%d') <= fecha_key <= semana_fin.strftime('%Y-%m-%d'))
                    semanas.append({
                        'inicio_semana': semana_inicio.strftime('%Y-%m-%d'),
                        'fin_semana': semana_fin.strftime('%Y-%m-%d'),
                        'km': round(km_semana, 2)
                    })
                return render_template('correr.html', mensaje="Registro eliminado correctamente.", fecha=fecha_str, km_semanal=km_semanal, meta_km=meta_km, semanas=semanas, km_por_dia=km_por_dia, km_dia=km_dia, semana_actual=semana_actual)
        return render_template('correr.html', fecha=fecha_str, km_semanal=km_semanal, meta_km=meta_km, semanas=semanas, km_por_dia=km_por_dia, km_dia=km_dia, semana_actual=semana_actual)
    except Exception as e:
        return render_template('correr.html', error=f"Error: {str(e)}", fecha=hoy.strftime('%Y-%m-%d'), km_semanal=0, meta_km=0, semanas=[], km_por_dia={}, km_dia=0, semana_actual=semana_actual)

@app.route('/anadir_ejercicio', methods=['GET', 'POST'])
def anadir_ejercicio():
    hoy = date.today()
    inicio_semana = hoy - timedelta(days=hoy.weekday())
    fin_semana = inicio_semana + timedelta(days=6)
    semana_actual = f"Semana {hoy.isocalendar()[1]}: del {inicio_semana.strftime('%d/%m/%Y')} al {fin_semana.strftime('%d/%m/%Y')}"
    try:
        fecha_str = request.args.get('fecha', hoy.strftime('%Y-%m-%d'))
        if request.method == 'POST':
            ejercicio = request.form['ejercicio'].strip()
            fecha_str = request.form.get('fecha', hoy.strftime('%Y-%m-%d'))
            if not ejercicio:
                return render_template('anadir_ejercicio.html', error="El ejercicio no puede estar vacío.", fecha=fecha_str, semana_actual=semana_actual)
            modelo.anadir_ejercicio_personalizado(fecha_str, ejercicio)
            return redirect(url_for('entreno', fecha=fecha_str))
        return render_template('anadir_ejercicio.html', fecha=fecha_str, semana_actual=semana_actual)
    except Exception as e:
        return render_template('anadir_ejercicio.html', error=f"Error: {str(e)}", fecha=hoy.strftime('%Y-%m-%d'), semana_actual=semana_actual)

@app.route('/progreso', methods=['GET'])
def progreso():
    hoy = date.today()
    inicio_semana = hoy - timedelta(days=hoy.weekday())
    fin_semana = inicio_semana + timedelta(days=6)
    semana_actual = f"Semana {hoy.isocalendar()[1]}: del {inicio_semana.strftime('%d/%m/%Y')} al {fin_semana.strftime('%d/%m/%Y')}"
    try:
        fecha_str = request.args.get('fecha', hoy.strftime('%Y-%m-%d'))
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
        return render_template('progreso.html', puntos=puntos, km=km, completados=completados, totales=totales, fecha=fecha_str, recompensas=recompensas, ranking=ranking, imagen_ranking=imagen_ranking, record_puntos=record_puntos, estadisticas=estadisticas, semanas_puntos=semanas_puntos, semanas_km=semanas_km, semanas_totales_completados=semanas_totales_completados, semana_actual=semana_actual)
    except Exception as e:
        return render_template('progreso.html', error=f"Error: {str(e)}", puntos=0, km=0, completados=0, totales=0, fecha=hoy.strftime('%Y-%m-%d'), recompensas=[], ranking="Sin ranking", imagen_ranking="", record_puntos=0, estadisticas={}, semanas_puntos=[], semanas_km=[], semanas_totales_completados=[], semana_actual=semana_actual)

@app.route('/resumen', methods=['GET'])
def resumen():
    hoy = date.today()
    inicio_semana = hoy - timedelta(days=hoy.weekday())
    fin_semana = inicio_semana + timedelta(days=6)
    semana_actual = f"Semana {hoy.isocalendar()[1]}: del {inicio_semana.strftime('%d/%m/%Y')} al {fin_semana.strftime('%d/%m/%Y')}"
    try:
        fecha_str = request.args.get('fecha', hoy.strftime('%Y-%m-%d'))
        fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        puntos, km, completados, totales, recompensas, ranking, imagen_ranking, record_puntos, _ = modelo.evaluar_semana(ejercicios.get_ejercicios_dia, fecha, ejercicios.get_puntos)
        texto_resumen = modelo.generar_resumen(puntos, km, completados, totales, recompensas, ranking, imagen_ranking, record_puntos, modelo.meta_km.get(str(fecha.isocalendar()[1]), 0))
        return render_template('resumen.html', texto_resumen=texto_resumen, fecha=fecha_str, puntos=puntos, ranking=ranking, imagen_ranking=imagen_ranking, record_puntos=record_puntos, recompensas=recompensas, semana_actual=semana_actual)
    except Exception as e:
        return render_template('resumen.html', error=f"Error: {str(e)}", texto_resumen="Error al generar el resumen.", fecha=hoy.strftime('%Y-%m-%d'), puntos=0, ranking="Sin ranking", imagen_ranking="", record_puntos=0, recompensas=[], semana_actual=semana_actual)

@app.route('/informe_pdf', methods=['GET', 'POST'])
def informe_pdf():
    hoy = date.today()
    inicio_semana = hoy - timedelta(days=hoy.weekday())
    fin_semana = inicio_semana + timedelta(days=6)
    semana_actual = f"Semana {hoy.isocalendar()[1]}: del {inicio_semana.strftime('%d/%m/%Y')} al {fin_semana.strftime('%d/%m/%Y')}"
    mensaje = None
    if request.method == 'POST':
        try:
            fecha_inicio = request.form.get('fecha_inicio')
            fecha_fin = request.form.get('fecha_fin')
            output_path = f"static/progreso_{modelo.nombre}.pdf"
            generar_pdf_progreso(modelo, fecha_inicio, fecha_fin, output_path)
            mensaje = "PDF generado correctamente."
            return send_file(output_path, as_attachment=True)
        except Exception as e:
            mensaje = f"Error al generar PDF: {str(e)}"
    return render_template('informe_pdf.html', mensaje=mensaje, semana_actual=semana_actual)

if __name__ == '__main__':
    port = int(os.getenv('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=True)
