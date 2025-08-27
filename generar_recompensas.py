from PIL import Image
import os

def generar_imagen_recompensa(nombre_recompensa, ruta_origen, ruta_destino):
    try:
        if os.path.exists(ruta_origen):
            img = Image.open(ruta_origen)
        else:
            # Imagen de fallback si no encuentra la original
            img = Image.new("RGB", (200, 200), (200, 200, 200))

        # Redimensionar para mantener consistencia
        img = img.resize((100, 100), Image.LANCZOS)
        img.save(ruta_destino)

    except Exception as e:
        print(f"Error al generar imagen para {nombre_recompensa}: {e}")


if __name__ == "__main__":
    carpeta_origen = "static/mis_imagenes"
    carpeta_destino = "static/recompensas"

    os.makedirs(carpeta_destino, exist_ok=True)

    # Lista fija de recompensas actuales
    recompensas = ["Crack", "Chill", "Looser", "Noob", "Semidios"]

    for recompensa in recompensas:
        archivo = f"{recompensa.lower()}.png"
        ruta_origen = os.path.join(carpeta_origen, archivo)
        ruta_destino = os.path.join(carpeta_destino, archivo)

        generar_imagen_recompensa(recompensa, ruta_origen, ruta_destino)

    print("✅ Imágenes de recompensas generadas en:", carpeta_destino)
