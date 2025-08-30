```python
from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime, date, timedelta
from modelo import Modelo
from ejercicios import Ejercicios

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
            estatura = float(request.form.get('estatura', 0)) / 100  # Convertir cm a m
            talla_sentada = float(request.form.get('talla_sentada', 0)) / 100  # Convertir cm a m
            envergadura = float(request.form.get('envergadura', 0)) / 100  # Convertir cm a m
            meta_km = float(request.form.get('meta_km', 0))
            ejercicios_type = request.form.get('ejercicios_type', 'bodyweight')
            mes_medicion = request.form.get('mes_medicion', date.today().strftime('%Y-%m'))

            if not nombre:
                return render_template('datos_personales.html', nombre=modelo.nombre, peso=modelo.peso, estatura=modelo.estatura * 100 if modelo.estatura else 0, talla_sentada=modelo.talla_sentada * 100 if modelo.talla_sentada else 0, envergadura=modelo.envergadura * 100 if modelo.envergadura else 0, meta_km=modelo.meta_km.get(semana_ano, 0), ejercicios_type=modelo.ejercicios_type, error="El nombre no puede estar vacío.", semana_actual=semana_actual, usuarios=usuarios, mes_medicion=mes_medicion)

            if any(v < 0 for v in [peso, estatura, talla_sentada, envergadura, meta_km]):
                return render_template('datos_personales.html', nombre=modelo.nombre, peso=modelo.peso, estatura=modelo.estatura * 100 if modelo.estatura else 0, talla_sentada=modelo.talla_sentada * 100 if modelo.talla_sentada else 0, envergadura=modelo.envergadura * 100 if modelo.envergadura else 0, meta_km=modelo.meta_km.get(semana_ano, 0), ejercicios_type=modelo.ejercicios_type, error="Peso, estatura, talla sentada, envergadura y meta de km deben ser positivos.", semana_actual=semana_actual, usuarios=usuarios, mes_medicion=mes_medicion)

            modelo.nombre = nombre
            modelo.peso = peso
            modelo.estatura = estatura
            modelo.talla_sentada = talla_sentada
            modelo.envergadura = envergadura
            modelo.meta_km[semana_ano] = meta_km
            modelo.ejercicios_type = ejercicios_type

            # Guardar medición mensual
            if mes_medicion not in modelo.historial_mediciones:
                modelo.historial_mediciones[mes_medicion] = {}
            modelo.historial_mediciones[mes_medicion] = {
                'estatura': estatura,
                'peso': peso,
                'talla_sentada': talla_sentada,
                'envergadura': envergadura
            }
            modelo.guardar_datos()

            # Calcular métricas
            segmento_inferior = estatura - talla_sentada if estatura and talla_sentada else 0
            imc = peso / (estatura ** 2) if estatura and peso else 0
            velocidad_crecimiento = 0
            historial_fechas = sorted(modelo.historial_mediciones.keys())
            if len(historial_fechas) >= 2:
                ultima_medicion = modelo.historial_mediciones[historial_fechas[-1]]
                penultima_medicion = modelo.historial_mediciones[historial_fechas[-2]]
                ultima_fecha = datetime.strptime(historial_fechas[-1], '%Y-%m')
                penultima_fecha = datetime.strptime(historial_fechas[-2], '%Y-%m')
                diferencia_estatura = ultima_medicion['estatura'] - penultima_medicion['estatura']
                meses = (ultima_fecha.year - penultima_fecha.year) * 12 + (ultima_fecha.month - penultima_fecha.month)
                velocidad_crecimiento = (diferencia_estatura / meses * 12) if meses > 0 else 0

            # Generar configuración del gráfico
            datos_grafica = []
            if len(historial_fechas) >= 2 and abs(diferencia_estatura) > 0.001:
                datos_grafica = [{'mes': mes, 'estatura': medicion['estatura'] * 100, 'velocidad': velocidad_crecimiento if mes == historial_fechas[-1] else 0} for mes, medicion in modelo.historial_mediciones.items()]
            chart_config = {
                "type": "line",
                "data": {
                    "labels": [item['mes'] for item in datos_grafica] if datos_grafica else [],
                    "datasets": [
                        {
                            "label": "Estatura (cm)",
                            "data": [item['estatura'] for item in datos_grafica] if datos_grafica else [],
                            "borderColor": "#36A2EB",
                            "backgroundColor": "rgba(54, 162, 235, 0.2)",
                            "fill": true
                        },
                        {
                            "label": "Velocidad de Crecimiento (cm/año)",
                            "data": [item['velocidad'] for item in datos_grafica] if datos_grafica else [],
                            "borderColor": "#FF6384",
                            "backgroundColor": "rgba(255, 99, 132, 0.2)",
                            "fill": true
                        }
                    ]
                },
                "options": {
                    "responsive": true,
                    "scales": {
                        "y": {
                            "beginAtZero": true
                        }
                    }
                }
            }
            return render_template('datos_personales.html', nombre=modelo.nombre, peso=modelo.peso, estatura=estatura * 100, talla_sentada=talla_sentada * 100 if talla_sentada else 0, envergadura=envergadura * 100 if envergadura else 0, meta_km=modelo.meta_km.get(semana_ano, 0), ejercicios_type=modelo.ejercicios_type, mensaje="¡Datos guardados correctamente!", semana_actual=semana_actual, usuarios=usuarios, segmento_inferior=segmento_inferior * 100, imc=imc, velocidad_crecimiento=velocimiento_crecimiento, mes_medicion=mes_medicion, datos_grafica=datos_grafica, chart_config=chart_config)
        except ValueError as e:
            return render_template('datos_personales.html', nombre=modelo.nombre, peso=modelo.peso, estatura=modelo.estatura * 100 if modelo.estatura else 0, talla_sentada=modelo.talla_sentada * 100 if modelo.talla_sentada else 0, envergadura=modelo.envergadura * 100 if modelo.envergadura else 0, meta_km=modelo.meta_km.get(semana_ano, 0), ejercicios_type=modelo.ejercicios_type, error=f"Error en los datos: {str(e)}", semana_actual=semana_actual, usuarios=usuarios, mes_medicion=date.today().strftime('%Y-%m'))
        except Exception as e:
            print(f"[DEBUG] Error interno en /datos_personales: {str(e)}")
            return render_template('datos_personales.html', nombre=modelo.nombre, peso=modelo.peso, estatura=modelo.estatura * 100 if modelo.estatura else 0, talla_sentada=modelo.talla_sentada * 100 if modelo.talla_sentada else 0, envergadura=modelo.envergadura * 100 if modelo.envergadura else 0, meta_km=modelo.meta_km.get(semana_ano, 0), ejercicios_type=modelo.ejercicios_type, error=f"Error interno: {str(e)}", semana_actual=semana_actual, usuarios=usuarios, mes_medicion=date.today().strftime('%Y-%m'))
    else:  # Bloque GET
        segmento_inferior = (modelo.estatura - modelo.talla_sentada) * 100 if modelo.estatura and modelo.talla_sentada else 0
        imc = modelo.peso / (modelo.estatura ** 2) if modelo.estatura and modelo.peso else 0
        velocidad_crecimiento = 0
        historial_fechas = sorted(modelo.historial_mediciones.keys())
        if len(historial_fechas) >= 2:
            ultima_medicion = modelo.historial_mediciones[historial_fechas[-1]]
            penultima_medicion = modelo.historial_mediciones[historial_fechas[-2]]
            ultima_fecha = datetime.strptime(historial_fechas[-1], '%Y-%m')
            penultima_fecha = datetime.strptime(historial_fechas[-2], '%Y-%m')
            diferencia_estatura = ultima_medicion['estatura'] - penultima_medicion['estatura']
            meses = (ultima_fecha.year - penultima_fecha.year) * 12 + (ultima_fecha.month - penultima_fecha.month)
            velocidad_crecimiento = (diferencia_estatura / meses * 12) if meses > 0 else 0

        # Generar configuración del gráfico
        datos_grafica = []
        if len(historial_fechas) >= 2 and abs(diferencia_estatura) > 0.001:
            datos_grafica = [{'mes': mes, 'estatura': medicion['estatura'] * 100, 'velocidad': velocidad_crecimiento if mes == historial_fechas[-1] else 0} for mes, medicion in modelo.historial_mediciones.items()]
        chart_config = {
            "type": "line",
            "data": {
                "labels": [item['mes'] for item in datos_grafica] if datos_grafica else [],
                "datasets": [
                    {
                        "label": "Estatura (cm)",
                        "data": [item['estatura'] for item in datos_grafica] if datos_grafica else [],
                        "borderColor": "#36A2EB",
                        "backgroundColor": "rgba(54, 162, 235, 0.2)",
                        "fill": true
                    },
                    {
                        "label": "Velocidad de Crecimiento (cm/año)",
                        "data": [item['velocidad'] for item in datos_grafica] if datos_grafica else [],
                        "borderColor": "#FF6384",
                        "backgroundColor": "rgba(255, 99, 132, 0.2)",
                        "fill": true
                    }
                ]
            },
            "options": {
                "responsive": true,
                "scales": {
                    "y": {
                        "beginAtZero": true
                    }
                }
            }
        }
        return render_template('datos_personales.html', nombre=modelo.nombre, peso=modelo.peso, estatura=modelo.estatura * 100 if modelo.estatura else 0, talla_sentada=modelo.talla_sentada * 100 if modelo.talla_sentada else 0, envergadura=modelo.envergadura * 100 if modelo.envergadura else 0, meta_km=modelo.meta_km.get(semana_ano, 0), ejercicios_type=modelo.ejercicios_type, semana_actual=semana_actual, usuarios=usuarios, segmento_inferior=segmento_inferior, imc=imc, velocidad_crecimiento=velocidad_crecimiento, mes_medicion=date.today().strftime('%Y-%m'), datos_grafica=datos_grafica, chart_config=chart_config)

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
            return render_template('datos_personales.html', nombre=modelo.nombre, peso=modelo.peso, estatura=modelo.estatura * 100 if modelo.estatura else 0, talla_sentada=modelo.talla_sentada * 100 if modelo.talla_sentada else 0, envergadura=modelo.envergadura * 100 if modelo.envergadura else 0, meta_km=modelo.meta_km.get(semana_ano, 0), ejercicios_type=modelo.ejercicios_type, error="Selecciona un usuario.", semana_actual=semana_actual, usuarios=usuarios, mes_medicion=date.today().strftime('%Y-%m'))
        if nombre_usuario not in usuarios:
            return render_template('datos_personales.html', nombre=modelo.nombre, peso=modelo.peso, estatura=modelo.estatura * 100 if modelo.estatura else 0, talla_sentada=modelo.talla_sentada * 100 if modelo.talla_sentada else 0, envergadura=modelo.envergadura * 100 if modelo.envergadura else 0, meta_km=modelo.meta_km.get(semana_ano, 0), ejercicios_type=modelo.ejercicios_type, error=f"Usuario '{nombre_usuario}' no encontrado en la lista: {usuarios}", semana_actual=semana_actual, usuarios=usuarios, mes_medicion=date.today().strftime('%Y-%m'))
        success = modelo.cambiar_usuario(nombre_usuario)
        if success:
            # Calcular métricas después de cambiar usuario
            segmento_inferior = (modelo.estatura - modelo.talla_sentada) * 100 if modelo.estatura and modelo.talla_sentada else 0
            imc = modelo.peso / (modelo.estatura ** 2) if modelo.estatura and modelo.peso else 0
            velocidad_crecimiento = 0
            historial_fechas = sorted(modelo.historial_mediciones.keys())
            if len(historial_fechas) >= 2:
                ultima_medicion = modelo.historial_mediciones[historial_fechas[-1]]
                penultima_medicion = modelo.historial_mediciones[historial_fechas[-2]]
                ultima_fecha = datetime.strptime(historial_fechas[-1], '%Y-%m')
                penultima_fecha = datetime.strptime(historial_fechas[-2], '%Y-%m')
                diferencia_estatura = ultima_medicion['estatura'] - penultima_medicion['estatura']
                meses = (ultima_fecha.year - penultima_fecha.year) * 12 + (ultima_fecha.month - penultima_fecha.month)
                velocidad_crecimiento = (diferencia_estatura / meses * 12) if meses > 0 else 0

            # Generar configuración del gráfico
            datos_grafica = []
            if len(historial_fechas) >= 2 and abs(diferencia_estatura) > 0.001:
                datos_grafica = [{'mes': mes, 'estatura': medicion['estatura'] * 100, 'velocidad': velocidad_crecimiento if mes == historial_fechas[-1] else 0} for mes, medicion in modelo.historial_mediciones.items()]
            chart_config = {
                "type": "line",
                "data": {
                    "labels": [item['mes'] for item in datos_grafica] if datos_grafica else [],
                    "datasets": [
                        {
                            "label": "Estatura (cm)",
                            "data": [item['estatura'] for item in datos_grafica] if datos_grafica else [],
                            "borderColor": "#36A2EB",
                            "backgroundColor": "rgba(54, 162, 235, 0.2)",
                            "fill": true
                        },
                        {
                            "label": "Velocidad de Crecimiento (cm/año)",
                            "data": [item['velocidad'] for item in datos_grafica] if datos_grafica else [],
                            "borderColor": "#FF6384",
                            "backgroundColor": "rgba(255, 99, 132, 0.2)",
                            "fill": true
                        }
                    ]
                },
                "options": {
                    "responsive": true,
                    "scales": {
                        "y": {
                            "beginAtZero": true
                        }
                    }
                }
            }
            return render_template('datos_personales.html', nombre=modelo.nombre, peso=modelo.peso, estatura=modelo.estatura * 100 if modelo.estatura else 0, talla_sentada=modelo.talla_sentada * 100 if modelo.talla_sentada else 0, envergadura=modelo.envergadura * 100 if modelo.envergadura else 0, meta_km=modelo.meta_km.get(semana_ano, 0), ejercicios_type=modelo.ejercicios_type, mensaje=f"¡Cambiado a usuario '{nombre_usuario}'!", semana_actual=semana_actual, usuarios=usuarios, segmento_inferior=segmento_inferior, imc=imc, velocidad_crecimiento=velocidad_crecimiento, mes_medicion=date.today().strftime('%Y-%m'), datos_grafica=datos_grafica, chart_config=chart_config)
        else:
            return render_template('datos_personales.html', nombre=modelo.nombre, peso=modelo.peso, estatura=modelo.estatura * 100 if modelo.estatura else 0, talla_sentada=modelo.talla_sentada * 100 if modelo.talla_sentada else 0, envergadura=modelo.envergadura * 100 if modelo.envergadura else 0, meta_km=modelo.meta_km.get(semana_ano, 0), ejercicios_type=modelo.ejercicios_type, error=f"Error al cambiar a usuario '{nombre_usuario}'.", semana_actual=semana_actual, usuarios=usuarios, mes_medicion=date.today().strftime('%Y-%m'))
    except Exception as e:
        print(f"[DEBUG] Error al cambiar usuario: {str(e)}")
        return render_template('datos_personales.html', nombre=modelo.nombre, peso=modelo.peso, estatura=modelo.estatura * 100 if modelo.estatura else 0, talla_sentada=modelo.talla_sentada * 100 if modelo.talla_sentada else 0, envergadura=modelo.envergadura * 100 if modelo.envergadura else 0, meta_km=modelo.meta_km.get(semana_ano, 0), ejercicios_type=modelo.ejercicios_type, error=f"Error al cambiar usuario: {str(e)}", semana_actual=semana_actual, usuarios=usuarios, mes_medicion=date.today().strftime('%Y-%m'))

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
            return render_template('datos_personales.html', nombre=modelo.nombre, peso=modelo.peso, estatura=modelo.estatura * 100 if modelo.estatura else 0, talla_sentada=modelo.talla_sentada * 100 if modelo.talla_sentada else 0, envergadura=modelo.envergadura * 100 if modelo.envergadura else 0, meta_km=modelo.meta_km.get(semana_ano, 0), ejercicios_type=modelo.ejercicios_type, error="El nombre no puede estar vacío.", semana_actual=semana_actual, usuarios=usuarios, mes_medicion=date.today().strftime('%Y-%m'))
        if nuevo_nombre in usuarios:
            return render_template('datos_personales.html', nombre=modelo.nombre, peso=modelo.peso, estatura=modelo.estatura * 100 if modelo.estatura else 0, talla_sentada=modelo.talla_sentada * 100 if modelo.talla_sentada else 0, envergadura=modelo.envergadura * 100 if modelo.envergadura else 0, meta_km=modelo.meta_km.get(semana_ano, 0), ejercicios_type=modelo.ejercicios_type, error="El usuario ya existe.", semana_actual=semana_actual, usuarios=usuarios, mes_medicion=date.today().strftime('%Y-%m'))
        modelo.nuevo_usuario(nuevo_nombre)
        return render_template('datos_personales.html', nombre=modelo.nombre, peso=modelo.peso, estatura=modelo.estatura * 100 if modelo.estatura else 0, talla_sentada=modelo.talla_sentada * 100 if modelo.talla_sentada else 0, envergadura=modelo.envergadura * 100 if modelo.envergadura else 0, meta_km=modelo.meta_km.get(semana_ano, 0), ejercicios_type=modelo.ejercicios_type, mensaje=f"¡Usuario '{nuevo_nombre}' creado correctamente!", semana_actual=semana_actual, usuarios=usuarios, mes_medicion=date.today().strftime('%Y-%m'))
    except ValueError as e:
        return render_template('datos_personales.html', nombre=modelo.nombre, peso=modelo.peso, estatura=modelo.estatura * 100 if modelo.estatura else 0, talla_sentada=modelo.talla_sentada * 100 if modelo.talla_sentada else 0, envergadura=modelo.envergadura * 100 if modelo.envergadura else 0, meta_km=modelo.meta_km.get(semana_ano, 0), ejercicios_type=modelo.ejercicios_type, error=str(e), semana_actual=semana_actual, usuarios=usuarios, mes_medicion=date.today().strftime('%Y-%m'))
    except Exception as e:
        print(f"[DEBUG] Error al crear nuevo usuario: {str(e)}")
        return render_template('datos_personales.html', nombre=modelo.nombre, peso=modelo.peso, estatura=modelo.estatura * 100 if modelo.estatura else 0, talla_sentada=modelo.talla_sentada * 100 if modelo.talla_sentada else 0, envergadura=modelo.envergadura * 100 if modelo.envergadura else 0, meta_km=modelo.meta_km.get(semana_ano, 0), ejercicios_type=modelo.ejercicios_type, error=f"Error interno: {str(e)}", semana_actual=semana_actual, usuarios=usuarios, mes_medicion=date.today().strftime('%Y-%m'))

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
                print(f"[DEBUG] Advertencia: No se encontraron ejercicios para la fecha {fecha_str}. Usando lista vacía.")
                ejercicios_dia = []
            ejercicios_dict = {ejercicios.get_base_exercise_name(ej): (ej in ejercicios_seleccionados) for ej in ejercicios_dia}
            modelo.registrar_ejercicios(fecha, ejercicios_dict)
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
                print(f"[DEBUG] Advertencia: No se encontraron ejercicios para la fecha {fecha_str}. Usando lista vacía.")
                ejercicios_dia = []
            puntos_totales = sum(ejercicios.get_puntos(ejercicios.get_base_exercise_name(ejercicio)) for ejercicio in ejercicios_dia if modelo.ejercicios_completados.get(fecha_str, {}).get(ejercicios.get_base_exercise_name(ejercicio), False))
            fecha_anterior = (fecha - timedelta(days=1)).strftime('%Y-%m-%d')
            fecha_siguiente = (fecha + timedelta(days=1)).strftime('%Y-%m-%d')
            return render_template('entreno.html', fecha=fecha_str, ejercicios=ejercicios_dia, puntos_totales=puntos_totales, modelo=modelo, ejercicios_obj=ejercicios, fecha_anterior=fecha_anterior, fecha_siguiente=fecha_siguiente, ejercicios_type=modelo.ejercicios_type)
    except Exception as e:
        print(f"[DEBUG] Error en /entreno: {str(e)}")
        return render_template('error.html', error=f"Error al cargar entreno: {str(e)}"), 500

@app.route('/anadir_ejercicio', methods=['GET', 'POST'])
def anadir_ejercicio():
    try:
        fecha_str = request.args.get('fecha', date.today().strftime('%Y-%m-%d'))
        fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        if request.method == 'POST':
            nuevo_ejercicio = request.form.get('nuevo_ejercicio').strip()
            if nuevo_ejercicio:
                modelo.anadir_ejercicio_personalizado(fecha, nuevo_ejercicio)
                return redirect(url_for('entreno', fecha=fecha_str))
            return render_template('anadir_ejercicio.html', error="El ejercicio no puede estar vacío.", fecha=fecha_str)
        return render_template('anadir_ejercicio.html', fecha=fecha_str)
    except Exception as e:
        print(f"[DEBUG] Error en /anadir_ejercicio: {str(e)}")
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
                    return render_template('correr.html', error="Los kilómetros deben ser positivos.", fecha=fecha_str, km_semanal=km_semanal, tiempo_semanal=tiempo_semanal, meta_km=meta_km, semanas=semanas, km_por_dia=km_por_dia, tiempo_por_dia=tiempo_por_dia, km_dia=km_dia, tiempo_dia=tiempo_dia)
                modelo.registrar_km(fecha_str, modelo.km_corridos.get(fecha_str, 0.0) + km)
                modelo.registrar_tiempo(fecha_str, modelo.tiempo_corridos.get(fecha_str, 0.0) + tiempo_segundos)
                km_dia = modelo.km_corridos.get(fecha_str, 0.0)
                tiempo_dia = modelo.tiempo_corridos.get(fecha_str, 0.0)
                km_por_dia = modelo.km_corridos
                tiempo_por_dia = modelo.tiempo_corridos
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
                return render_template('correr.html', mensaje="¡Kilómetros y tiempo registrados!", fecha=fecha_str, km_semanal=km_semanal, tiempo_semanal=tiempo_semanal, meta_km=meta_km, semanas=semanas, km_por_dia=km_por_dia, tiempo_por_dia=tiempo_por_dia, km_dia=km_dia, tiempo_dia=tiempo_dia)
            elif accion == 'eliminar':
                if fecha_str in modelo.km_corridos:
                    del modelo.km_corridos[fecha_str]
                    del modelo.tiempo_corridos[fecha_str]
                    modelo.guardar_datos()
                    km_dia = 0.0
                    tiempo_dia = 0.0
                    km_por_dia = modelo.km_corridos
                    tiempo_por_dia = modelo.tiempo_corridos
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
                    return render_template('correr.html', mensaje="¡Kilómetros y tiempo eliminados!", fecha=fecha_str, km_semanal=km_semanal, tiempo_semanal=tiempo_semanal, meta_km=meta_km, semanas=semanas, km_por_dia=km_por_dia, tiempo_por_dia=tiempo_por_dia, km_dia=km_dia, tiempo_dia=tiempo_dia)
        return render_template('correr.html', fecha=fecha_str, km_semanal=km_semanal, tiempo_semanal=tiempo_semanal, meta_km=meta_km, semanas=semanas, km_por_dia=km_por_dia, tiempo_por_dia=tiempo_por_dia, km_dia=km_dia, tiempo_dia=tiempo_dia)
    except Exception as e:
        print(f"[DEBUG] Error en /correr: {str(e)}")
        return render_template('correr.html', error=f"Error: {str(e)}", fecha=date.today().strftime('%Y-%m-%d'), km_semanal=0.0, tiempo_semanal=0.0, meta_km=0.0, semanas=[], km_por_dia={}, tiempo_por_dia={}, km_dia=0.0, tiempo_dia=0.0)

@app.route('/progreso', methods=['GET'])
def progreso():
    try:
        hoy = date.today()
        puntos, km, completados, totales, recompensas, ranking, imagen_ranking, record_puntos, estadisticas = modelo.evaluar_semana(ejercicios.get_ejercicios_dia, hoy, ejercicios.get_puntos)

        semanas_puntos = []
        for i in range(-3, 1):  # Últimas 3 semanas + actual
            semana_inicio = hoy - timedelta(days=(hoy.weekday() + 7 * (i + 1)))
            semana_fin = semana_inicio + timedelta(days=6)
            p, k, _, _, _, _, _, _, _ = modelo.evaluar_semana(ejercicios.get_ejercicios_dia, semana_inicio, ejercicios.get_puntos)
            semanas_puntos.append({
                'inicio_semana': semana_inicio,
                'fin_semana': semana_fin,
                'puntos': p,
                'km': k
            })

        return render_template('progreso.html', puntos=puntos, km=km, completados=completados, totales=totales, ranking=ranking, imagen_ranking=imagen_ranking, record_puntos=record_puntos, estadisticas=estadisticas, fecha=hoy.strftime('%d/%m/%Y'), semanas_puntos=semanas_puntos)
    except Exception as e:
        print(f"[DEBUG] Error en /progreso: {str(e)}")
        return render_template('error.html', error=f"Error al cargar progreso: {str(e)}"), 500

@app.route('/resumen', methods=['GET'])
def resumen():
    try:
        hoy = date.today()
        resultado_semana = modelo.evaluar_semana(ejercicios.get_ejercicios_dia, hoy, ejercicios.get_puntos)
        if len(resultado_semana) != 9:
            raise ValueError(f"Esperados 9 valores de evaluar_semana, recibidos: {len(resultado_semana)}")
        puntos, km, completados, totales, recompensas, ranking, imagen_ranking, record_puntos, estadisticas = resultado_semana
        if not isinstance(puntos, (int, float)):
            raise ValueError(f"Esperado un número para puntos, recibido: {type(puntos)}")
        resumen = modelo.generar_resumen(puntos, km, completados, totales, recompensas, ranking, imagen_ranking, record_puntos, modelo.meta_km.get(str(hoy.isocalendar()[1]), 0.0))

        inicio_semana = hoy - timedelta(days=hoy.weekday())
        semanas_puntos = [{'inicio_semana': inicio_semana + timedelta(days=i*7), 'fin_semana': inicio_semana + timedelta(days=i*7 + 6), 'puntos': p} for i, (p, _, _, _, _, _, _, _, _) in enumerate([modelo.evaluar_semana(ejercicios.get_ejercicios_dia, inicio_semana + timedelta(days=i*7), ejercicios.get_puntos) for i in range(-3, 1)])]
        semanas_km = [{'inicio_semana': inicio_semana + timedelta(days=i*7), 'fin_semana': inicio_semana + timedelta(days=i*7 + 6), 'km': sum(float(km) for fecha_key, km in modelo.km_corridos.items() if (inicio_semana + timedelta(days=i*7)).strftime('%Y-%m-%d') <= fecha_key <= (inicio_semana + timedelta(days=i*7 + 6)).strftime('%Y-%m-%d'))} for i in range(-3, 1)]

        return render_template('resumen.html', resumen=resumen, imagen_ranking=imagen_ranking, estadisticas=estadisticas, fecha=hoy.strftime('%d/%m/%Y'), puntos=puntos, record_puntos=record_puntos, recompensas=recompensas, ranking=ranking, semanas_puntos=semanas_puntos, semanas_km=semanas_km, modelo=modelo)
    except Exception as e:
        print(f"[DEBUG] Error en /resumen: {str(e)}")
        return render_template('error.html', error=f"Error al generar resumen: {str(e)}"), 500

@app.route('/recompensas', methods=['GET'])
def redirigir_recompensas():
    return redirect(url_for('resumen'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=10000)
```
