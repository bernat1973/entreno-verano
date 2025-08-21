from fpdf import FPDF
import matplotlib.pyplot as plt
import io
import datetime

def generar_pdf_progreso(entrenos):
    # Procesar datos por semana
    semanas = {}
    total = 0
    for e in entrenos:
        fecha = datetime.datetime.strptime(e["fecha"], "%Y-%m-%d")
        semana = fecha.strftime("%Y-%U")  # Año-Semana
        semanas[semana] = semanas.get(semana, 0) + e["cantidad"]
        total += e["cantidad"]

    # Crear gráfica
    labels = list(semanas.keys())
    values = list(semanas.values())
    plt.figure(figsize=(8,4))
    plt.bar(labels, values)
    plt.xlabel('Semana')
    plt.ylabel('Cantidad')
    plt.title('Comparativa semanal')
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)

    # Generar PDF
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Página de total
    pdf.add_page()
    pdf.set_font("Arial", size=18)
    pdf.cell(200, 10, txt="Informe de Progreso", ln=True, align='C')
    pdf.set_font("Arial", size=14)
    pdf.cell(200, 10, txt=f"Total de actividad: {total}", ln=True)

    # Insertar gráfica
    pdf.image(buf, x=10, y=30, w=180)  # Ajusta posición/tamaño según prefieras

    # Listado de entrenos (fechas únicas)
    fechas_unicas = sorted(set([e["fecha"] for e in entrenos]))
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Fechas de entrenamientos realizados:", ln=True)
    for fecha in fechas_unicas:
        pdf.cell(200, 10, txt=f"- {fecha}", ln=True)

    return pdf.output(dest="S").encode("latin1")
