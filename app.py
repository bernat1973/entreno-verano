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
        except ValueError:
            return render_template('datos_personales.html', nombre=modelo.nombre, peso=modelo.peso, estatura=modelo.estatura, meta_km=modelo.meta_km.get(semana_ano, 0), ejercicios_type=modelo.ejercicios_type, error="Valores inválidos.", semana_actual=semana_actual, usuarios=usuarios)
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
        nuevo_usuario = request.form['usuario']
        modelo.cambiar_usuario(nuevo_usuario)
        return redirect(url_for('datos_personales'))
    except ValueError as e:
        return render_template('datos_personales.html', nombre=modelo.nombre, peso=modelo.peso, estatura=modelo.estatura, meta_km=modelo.meta_km.get(semana_ano, 0), ejercicios_type=modelo.ejercicios_type, error=str(e), semana_actual=semana_actual, usuarios=usuarios)

@app.route('/nuevo_usuario', methods=['POST'])
def nuevo_usuario():
    semana_ano = str(datetime.now().isocalendar()[1])
    hoy = date.today()
    inicio_semana = hoy - timedelta(days=hoy.weekday())
    fin_semana = inicio_semana + timedelta(days=6)
    semana_actual = f"Semana {semana_ano}: del {inicio_semana.strftime('%d/%m/%Y')} al {fin_semana.strftime('%d/%m/%Y')}"
    usuarios = modelo.get_usuarios()
    try:
        nuevo_usuario = request.form['nuevo_usuario'].strip()
        if not nuevo_usuario:
            return render_template('datos_personales.html', nombre=modelo.nombre, peso=modelo.peso, estatura=modelo.estatura, meta_km=modelo.meta_km.get(semana_ano, 0), ejercicios_type=modelo.ejercicios_type, error="El nombre del nuevo usuario no puede estar vacío.", semana_actual=semana_actual, usuarios=usuarios)
        modelo.nuevo_usuario(nuevo_usuario)
        return redirect(url_for('datos_personales'))
    except ValueError as e:
        return render_template('datos_personales.html', nombre=modelo.nombre, peso=modelo.peso, estatura=modelo.estatura, meta_km=modelo.meta_km.get(semana_ano, 0), ejercicios_type=modelo.ejercicios_type, error=str(e), semana_actual=semana_actual, usuarios=usuarios)

@app.route('/entreno', methods=['GET', 'POST'])
def entreno():
    hoy = date.today()
    fecha_str = request.args.get('fecha', hoy.strftime('%Y-%m-%d'))
    try:
        fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
    except ValueError:
        fecha = hoy
        fecha_str = hoy.strftime('%Y-%m-%d')
    
    semana_ano = str(fecha.isocalendar()[1])
    inicio_semana = fecha - timedelta(days=fecha.weekday())
    fin_semana = inicio_semana + timedelta(days=6)
    semana_actual = f"Semana {semana_ano}: del {inicio_semana.strftime('%d/%m/%Y')} al {fin_semana.strftime('%d/%m/%Y')}"
    
    ejercicios_dia = ejercicios.get_ejercicios_dia(fecha)
    puntos_totales = sum(ejercicios.get_puntos(ej) for ej in ejercicios_dia if fecha_str in modelo.ejercicios_completados and modelo.ejercicios_completados[fecha_str].get(ej, False))
    
    if request.method == 'POST':
        try:
            ejercicios_completados = {ej: request.form.get(ej) == 'on' for ej in ejercicios_dia}
            modelo.registrar_ejercicios(fecha, ejercicios_completados)
            return redirect(url_for('entreno', fecha=fecha_str))
        except Exception as e:
            return render_template('entreno.html', ejercicios=ejercicios_dia, fecha=fecha_str, puntos_totales=puntos_totales, error=f"Error: {str(e)}", semana_actual=semana_actual)
    
    return render_template('entreno.html', ejercicios=ejercicios_dia, fecha=fecha_str, puntos_totales=puntos_totales, semana_actual=semana_actual)

@app.route('/correr', methods=['GET', 'POST'])
def correr():
    hoy = date.today()
    fecha_str = request.args.get('fecha', hoy.strftime('%Y-%m-%d'))
    try:
        fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
    except ValueError:
        fecha = hoy
        fecha_str = hoy.strftime('%Y-%m-%d')
    
    semana_ano = str(fecha.isocalendar()[1])
    inicio_semana = fecha - timedelta(days=fecha.weekday())
    fin_semana = inicio_semana + timedelta(days=6)
    semana_actual = f"Semana {semana_ano}: del {inicio_semana.strftime('%d/%m/%Y')} al {fin_semana.strftime('%d/%m/%Y')}"
    
    km_dia = modelo.km_corridos.get(fecha_str, 0)
    km_semanal = sum(modelo.km_corridos.get((inicio_semana + timedelta(days=i)).strftime('%Y-%m-%d'), 0) for i in range(7))
    meta_km = modelo.meta_km.get(semana_ano, 0)
    km_por_dia = {k: v for k, v in modelo.km_corridos.items() if k >= inicio_semana.strftime('%Y-%m-%d') and k <= fin_semana.strftime('%Y-%m-%d')}
    
    semanas = []
    for i in range(-2, 1):
        semana = inicio_semana + timedelta(days=i*7)
        semana_str = semana.strftime('%Y-%m-%d')
        km = sum(modelo.km_corridos.get((semana + timedelta(days=j)).strftime('%Y-%m-%d'), 0) for j in range(7))
        semanas.append({'inicio_semana': semana_str, 'km': round(km, 2)})
    
    if request.method == 'POST':
        if 'eliminar_km' in request.form:
            try:
                fecha_eliminar = request.form['fecha_eliminar']
                modelo.eliminar_km(fecha_eliminar)
                return redirect(url_for('correr', fecha=fecha_str))
            except Exception as e:
                return render_template('correr.html', fecha=fecha_str, km_dia=km_dia, km_semanal=km_semanal, meta_km=meta_km, km_por_dia=km_por_dia, semanas=semanas, error=f"Error: {str(e)}", semana_actual=semana_actual)
        try:
            km = float(request.form['km'])
            if km < 0:
                return render_template('correr.html', fecha=fecha_str, km_dia=km_dia, km_semanal=km_semanal, meta_km=meta_km, km_por_dia=km_por_dia, semanas=semanas, error="Los kilómetros no pueden ser negativos.", semana_actual=semana_actual)
            modelo.registrar_km(fecha, km)
            return redirect(url_for('correr', fecha=fecha_str))
        except ValueError:
            return render_template('correr.html', fecha=fecha_str, km_dia=km_dia, km_semanal=km_semanal, meta_km=meta_km, km_por_dia=km_por_dia, semanas=semanas, error="Kilómetros inválidos.", semana_actual=semana_actual)
    
    return render_template('correr.html', fecha=fecha_str, km_dia=km_dia, km_semanal=km_semanal, meta_km=meta_km, km_por_dia=km_por_dia, semanas=semanas, semana_actual=semana_actual)

@app.route('/progreso', methods=['GET', 'POST'])
def progreso():
    hoy = date.today()
    fecha_str = request.args.get('fecha', hoy.strftime('%Y-%m-%d'))
    try:
        fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
    except ValueError:
        fecha = hoy
        fecha_str = hoy.strftime('%Y-%m-%d')
    
    try:
        puntos, km, completados, totales, recompensas, ranking, imagen_ranking, record_puntos, estadisticas = modelo.evaluar_semana(ejercicios.get_ejercicios_dia, fecha, ejercicios.get_puntos)
        inicio_semana = fecha - timedelta(days=fecha.weekday())
        semanas_puntos = []
        semanas_km = []
        semanas_totales_completados = []
        for i in range(-2, 1):
            semana_inicio = inicio_semana + timedelta(days=i*7)
            semana_fin = semana_inicio + timedelta(days=6)
            puntos_semana = 0
            km_semana = 0
            completados_semana = 0
            totales_semana = 0
            for j in range(7):
                dia = semana_inicio + timedelta(days=j)
                dia_str = dia.strftime('%Y-%m-%d')
                ejercicios_dia = ejercicios.get_ejercicios_dia(dia)
                totales_semana += len(ejercicios_dia)
                if dia_str in modelo.ejercicios_completados:
                    for ej, completado in modelo.ejercicios_completados[dia_str].items():
                        if completado:
                            puntos_semana += ejercicios.get_puntos(ej)
                            completados_semana += 1
                if dia_str in modelo.km_corridos:
                    km_semana += modelo.km_corridos[dia_str]
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
        return render_template('progreso.html', puntos=puntos, km=km, completados=completados, totales=totales, fecha=fecha_str, recompensas=recompensas, ranking=ranking, imagen_ranking=imagen_ranking, record_puntos=record_puntos, estadisticas=estadisticas, semanas_puntos=semanas_puntos, semanas_km=semanas_km, semanas_totales_completados=semanas_totales_completados)
    except Exception as e:
        return render_template('progreso.html', error=f"Error: {str(e)}", puntos=0, km=0, completados=0, totales=0, fecha=fecha_str, recompensas=[], ranking="Sin ranking", imagen_ranking="", record_puntos=0, estadisticas={}, semanas_puntos=[], semanas_km=[], semanas_totales_completados=[])

@app.route('/resumen')
def resumen():
    try:
        fecha_str = request.args.get('fecha', date.today().strftime('%Y-%m-%d'))
        fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        puntos, km, completados, totales, recompensas, ranking, imagen_ranking, record_puntos, _ = modelo.evaluar_semana(ejercicios.get_ejercicios_dia, fecha, ejercicios.get_puntos)
        texto_resumen = modelo.generar_resumen(puntos, km, completados, totales, recompensas, ranking, imagen_ranking, record_puntos, modelo.meta_km.get(str(fecha.isocalendar()[1]), 0))
        return render_template('resumen.html', texto_resumen=texto_resumen, fecha=fecha_str, puntos=puntos, ranking=ranking, imagen_ranking=imagen_ranking, record_puntos=record_puntos, recompensas=recompensas)
    except Exception as e:
        return render_template('resumen.html', error=f"Error: {str(e)}", texto_resumen="Error al generar el resumen.", fecha=date.today().strftime('%Y-%m-%d'), puntos=0, ranking="Sin ranking", imagen_ranking="", record_puntos=0, recompensas=[])

@app.route('/anadir_ejercicio', methods=['GET', 'POST'])
def anadir_ejercicio():
    hoy = date.today()
    fecha_str = request.args.get('fecha', hoy.strftime('%Y-%m-%d'))
    try:
        fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
    except ValueError:
        fecha = hoy
        fecha_str = hoy.strftime('%Y-%m-%d')
    
    semana_ano = str(fecha.isocalendar()[1])
    inicio_semana = fecha - timedelta(days=fecha.weekday())
    fin_semana = inicio_semana + timedelta(days=6)
    semana_actual = f"Semana {semana_ano}: del {inicio_semana.strftime('%d/%m/%Y')} al {fin_semana.strftime('%d/%m/%Y')}"
    
    if request.method == 'POST':
        try:
            ejercicio = request.form['ejercicio'].strip()
            if not ejercicio:
                return render_template('anadir_ejercicio.html', fecha=fecha_str, error="El ejercicio no puede estar vacío.", semana_actual=semana_actual)
            modelo.anadir_ejercicio_personalizado(fecha, ejercicio)
            return render_template('anadir_ejercicio.html', fecha=fecha_str, mensaje="¡Ejercicio añadido correctamente!", semana_actual=semana_actual)
        except Exception as e:
            return render_template('anadir_ejercicio.html', fecha=fecha_str, error=f"Error: {str(e)}", semana_actual=semana_actual)
    
    return render_template('anadir_ejercicio.html', fecha=fecha_str, semana_actual=semana_actual)

@app.route('/informe_pdf', methods=['GET', 'POST'])
def informe_pdf():
    mensaje = None
    if request.method == 'POST':
        fecha_inicio = request.form.get('fecha_inicio')
        fecha_fin = request.form.get('fecha_fin')
        output_path = f"static/progreso_{modelo.nombre}.pdf"
        try:
            generar_pdf_progreso(modelo, fecha_inicio, fecha_fin, output_path)
            mensaje = "PDF generado correctamente."
            return send_file(output_path, as_attachment=True)
        except Exception as e:
            mensaje = f"Error al generar PDF: {e}"
    return render_template('informe_pdf.html', mensaje=mensaje)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
