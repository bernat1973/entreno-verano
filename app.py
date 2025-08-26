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
    semana_ano = str(datetime.now().isocalendar()[1])
    hoy = date.today()
    inicio_semana = hoy - timedelta(days=hoy.weekday())
    fin_semana = inicio_semana + timedelta(days=6)
    semana_actual = f"Semana {semana_ano}: del {inicio_semana.strftime('%d/%m/%Y')} al {fin_semana.strftime('%d/%m/%Y')}"
    usuarios = modelo.get_usuarios()
    try:
        nombre_usuario = request.form['usuario'].strip()
        if not nombre_usuario:
            return render_template('datos_personales.html', nombre=modelo.nombre, peso=modelo.peso, estatura=modelo.estatura, meta_km=modelo.meta_km.get(semana_ano, 0), ejercicios_type=modelo.ejercicios_type, error="Selecciona un usuario.", semana_actual=semana_actual, usuarios=usuarios)
        if nombre_usuario not in usuarios:
            return render_template('datos_personales.html', nombre=modelo.nombre, peso=modelo.peso, estatura=modelo.estatura, meta_km=modelo.meta_km.get(semana_ano, 0), ejercicios_type=modelo.ejercicios_type, error=f"Usuario '{nombre_usuario}' no encontrado en la lista: {usuarios}", semana_actual=semana_actual, usuarios=usuarios)
        success = modelo.cambiar_usuario(nombre_usuario)
        if success:
            # Forzar recarga con los datos actualizados
            return render_template('datos_personales.html', nombre=modelo.nombre, peso=modelo.peso, estatura=modelo.estatura, meta_km=modelo.meta_km.get(semana_ano, 0), ejercicios_type=modelo.ejercicios_type, mensaje=f"¡Cambiado a usuario '{nombre_usuario}'!", semana_actual=semana_actual, usuarios=usuarios)
        else:
            return render_template('datos_personales.html', nombre=modelo.nombre, peso=modelo.peso, estatura=modelo.estatura, meta_km=modelo.meta_km.get(semana_ano, 0), ejercicios_type=modelo.ejercicios_type, error=f"Error al cambiar a usuario '{nombre_usuario}'.", semana_actual=semana_actual, usuarios=usuarios)
    except Exception as e:
        return render_template('datos_personales.html', nombre=modelo.nombre, peso=modelo.peso, estatura=modelo.estatura, meta_km=modelo.meta_km.get(semana_ano, 0), ejercicios_type=modelo.ejercicios_type, error=f"Error al cambiar usuario: {str(e)}", semana_actual=semana_actual, usuarios=usuarios)

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
            return render_template('datos_personales.html', nombre=modelo.nombre, peso=modelo.peso, estatura=modelo.estatura, meta_km=modelo.meta_km.get(semana_ano, 0), ejercicios_type=modelo.ejercicios_type, error="El nombre no puede estar vacío.", semana_actual=semana_actual, usuarios=usuarios)
        if nuevo_nombre in usuarios:
            return render_template('datos_personales.html', nombre=modelo.nombre, peso=modelo.peso, estatura=modelo.estatura, meta_km=modelo.meta_km.get(semana_ano, 0), ejercicios_type=modelo.ejercicios_type, error="El usuario ya existe.", semana_actual=semana_actual, usuarios=usuarios)
        modelo.nuevo_usuario(nuevo_nombre)
        return render_template('datos_personales.html', nombre=modelo.nombre, peso=modelo.peso, estatura=modelo.estatura, meta_km=modelo.meta_km.get(semana_ano, 0), ejercicios_type=modelo.ejercicios_type, mensaje=f"¡Usuario '{nuevo_nombre}' creado correctamente!", semana_actual=semana_actual, usuarios=usuarios)
    except ValueError as e:
        return render_template('datos_personales.html', nombre=modelo.nombre, peso=modelo.peso, estatura=modelo.estatura, meta_km=modelo.meta_km.get(semana_ano, 0), ejercicios_type=modelo.ejercicios_type, error=str(e), semana_actual=semana_actual, usuarios=usuarios)

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
            ejercicios_dict = {ejercicios.get_base_exercise_name(ej): (ej in ejercicios_seleccionados) for ej in ejercicios_dia}
            modelo.registrar_ejercicios(fecha, ejercicios_dict)
            puntos_totales = sum(ejercicios.get_puntos(ejercicios.get_base_exercise_name(ejercicio)) for ejercicio in ejercicios_dia if modelo.ejercicios_completados.get(fecha_str, {}).get(ejercicios.get_base_exercise_name(ejercicio), False))
            fecha_anterior = (fecha - timedelta(days=1)).strftime('%Y-%m-%d')
            fecha_siguiente = (fecha + timedelta(days=1)).strftime('%Y-%m-%d')
            return render_template('entreno.html', mensaje="¡Ejercicios guardados correctamente!", fecha=fecha_str, ejercicios=ejercicios_dia, puntos_totales=puntos_totales, modelo=modelo, ejercicios_obj=ejercicios, fecha_anterior=fecha_anterior, fecha_siguiente=fecha_siguiente)
        else:
            fecha_str = request.args.get('fecha', date.today().strftime('%Y-%m-%d'))
            fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date() if fecha_str else date.today()
            fecha_str = fecha.strftime('%Y-%m-%d')
            ejercicios_dia = ejercicios.get_ejercicios_dia(fecha, modelo.historial_semanal)
            puntos_totales = sum(ejercicios.get_puntos(ejercicios.get_base_exercise_name(ejercicio)) for ejercicio in ejercicios_dia if modelo.ejercicios_completados.get(fecha_str, {}).get(ejercicios.get_base_exercise_name(ejercicio), False))
            fecha_anterior = (fecha - timedelta(days=1)).strftime('%Y-%m-%d')
            fecha_siguiente = (fecha + timedelta(days=1)).strftime('%Y-%m-%d')
            return render_template('entreno.html', fecha=fecha_str, ejercicios=ejercicios_dia, puntos_totales=puntos_totales, modelo=modelo, ejercicios_obj=ejercicios, fecha_anterior=fecha_anterior, fecha_siguiente=fecha_siguiente)
    except Exception as e:
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
                    return render_template('correr.html', error="Los kilómetros deben ser positivos.", fecha=fecha_str, km_semanal=km_semanal, meta_km=meta_km, semanas=semanas, km_por_dia=km_por_dia, km_dia=km_dia)
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
                return render_template('correr.html', mensaje="¡Kilómetros registrados!", fecha=fecha_str, km_semanal=km_semanal, meta_km=meta_km, semanas=semanas, km_por_dia=km_por_dia, km_dia=km_dia)
            elif accion == 'eliminar':
                if fecha_str in modelo.km_corridos:
                    del modelo.km_corridos[fecha_str]
                    modelo.guardar_datos()
                    km_dia = 0.0
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
                    return render_template('correr.html', mensaje="¡Kilómetros eliminados!", fecha=fecha_str, km_semanal=km_semanal, meta_km=meta_km, semanas=semanas, km_por_dia=km_por_dia, km_dia=km_dia)
        return render_template('correr.html', fecha=fecha_str, km_semanal=km_semanal, meta_km=meta_km, semanas=semanas, km_por_dia=km_por_dia, km_dia=km_dia)
    except Exception as e:
        return render_template('correr.html', error=f"Error: {str(e)}", fecha=date.today().strftime('%Y-%m-%d'), km_semanal=0.0, meta_km=0.0, semanas=[], km_por_dia={}, km_dia=0.0)

@app.route('/resumen', methods=['GET'])
def resumen():
    try:
        hoy = date.today()
        puntos, km, completados, totales, recompensas, ranking, imagen_ranking, record_puntos, estadisticas = modelo.evaluar_semana(ejercicios.get_ejercicios_dia, hoy, ejercicios.get_puntos)
        texto_resumen = modelo.generar_resumen(puntos, km, completados, totales, recompensas, ranking, imagen_ranking, record_puntos, modelo.meta_km.get(str(hoy.isocalendar()[1]), 0.0))
        return render_template('resumen.html', resumen=texto_resumen, imagen_ranking=imagen_ranking, estadisticas=estadisticas)
    except Exception as e:
        return render_template('resumen.html', error=f"Error al generar resumen: {str(e)}", resumen="", imagen_ranking="", estadisticas={})

@app.route('/descargar_pdf', methods=['GET'])
def descargar_pdf():
    try:
        hoy = date.today()
        puntos, km, completados, totales, recompensas, ranking, imagen_ranking, record_puntos, estadisticas = modelo.evaluar_semana(ejercicios.get_ejercicios_dia, hoy, ejercicios.get_puntos)
        texto_resumen = modelo.generar_resumen(puntos, km, completados, totales, recompensas, ranking, imagen_ranking, record_puntos, modelo.meta_km.get(str(hoy.isocalendar()[1]), 0.0))
        output_path = f"static/progreso_{modelo.nombre}.pdf"  # Corregida indentación
        pdf_path = generar_pdf_progreso(texto_resumen, imagen_ranking, estadisticas)
        return send_file(pdf_path, as_attachment=True, download_name='progreso_semanal.pdf', mimetype='application/pdf')
    except Exception as e:
        return render_template('resumen.html', error=f"Error al generar PDF: {str(e)}", resumen="", imagen_ranking="", estadisticas={})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=10000)
