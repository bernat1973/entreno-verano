from fpdf import FPDF
from datetime import datetime, timedelta

class InformePDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'Informe de Progreso', 0, 1, 'C')
        self.ln(5)

    def add_resumen(self, nombre, fecha_inicio, fecha_fin, porcentaje, puntos_totales, ejercicios_totales, completados_totales):
        self.set_font('Arial', '', 12)
        self.cell(0, 10, f'Usuario: {nombre}', 0, 1)
        self.cell(0, 10, f'Rango: {fecha_inicio} al {fecha_fin}', 0, 1)
        self.cell(0, 10, f'Porcentaje de ejercicios completados: {porcentaje:.1f}%', 0, 1)
        self.cell(0, 10, f'Puntos totales: {puntos_totales}', 0, 1)
        self.cell(0, 10, f'Ejercicios completados: {completados_totales} de {ejercicios_totales}', 0, 1)
        self.ln(10)

    def add_semana(self, semana, puntos, completados, totales):
        self.set_font('Arial', 'B', 11)
        self.cell(0, 8, f'Semana: {semana}', 0, 1)
        self.set_font('Arial', '', 10)
        self.cell(0, 6, f'Puntos: {puntos} | Ejercicios completados: {completados}/{totales}', 0, 1)
        self.ln(2)

def generar_pdf_progreso(modelo, fecha_inicio, fecha_fin, output_path):
    pdf = InformePDF()
    pdf.add_page()

    # Calcular resumen global
    fecha_ini = datetime.strptime(fecha_inicio, "%Y-%m-%d").date()
    fecha_fin = datetime.strptime(fecha_fin, "%Y-%m-%d").date()
    semanas = []
    completados_totales = 0
    ejercicios_totales = 0
    puntos_totales = 0

    for semana_dict in modelo.historial_semanal:
        semana_fecha = datetime.strptime(semana_dict['semana'], "%Y-%m-%d").date()
        if fecha_ini <= semana_fecha <= fecha_fin:
            semanas.append(semana_dict)
            completados_totales += semana_dict.get('completados', 0)
            ejercicios_totales += semana_dict.get('totales', 0)
            puntos_totales += semana_dict.get('puntos', 0)

    porcentaje = (completados_totales / ejercicios_totales * 100) if ejercicios_totales > 0 else 0

    pdf.add_resumen(modelo.nombre, fecha_inicio, fecha_fin, porcentaje, puntos_totales, ejercicios_totales, completados_totales)

    # Detalle por semana
    for semana_dict in semanas:
        pdf.add_semana(
            semana=semana_dict.get('semana', ''),
            puntos=semana_dict.get('puntos', 0),
            completados=semana_dict.get('completados', 0),
            totales=semana_dict.get('totales', 0)
        )

    pdf.output(output_path)
