from PIL import Image, ImageDraw, ImageFont
import os

def generar_imagen_recompensa(recompensa, output_path):
    try:
        img = Image.new('RGB', (200, 200), (255, 255, 255))
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("arial.ttf", 20)
        except Exception:
            font = ImageFont.load_default()
        if recompensa == "Crack":
            draw.rectangle((80, 60, 120, 100), fill=(255, 215, 0))  # Copa dorada
            draw.ellipse((70, 20, 130, 50), fill=(255, 215, 0))
            draw.text((30, 120), "¡Crack!", font=font, fill="#000000")
        elif recompensa == "Chill":
            for pos in [(60, 60), (140, 60), (100, 100)]:  # Estrellas
                draw.polygon([
                    (pos[0], pos[1]-15), (pos[0]+5, pos[1]-5),
                    (pos[0]+15, pos[1]-5), (pos[0]+5, pos[1]+5),
                    (pos[0]+10, pos[1]+15), (pos[0], pos[1]+5),
                    (pos[0]-10, pos[1]+15), (pos[0]-5, pos[1]+5),
                    (pos[0]-15, pos[1]-5), (pos[0]-5, pos[1]-5)
                ], fill=(255, 255, 0))
            draw.text((30, 140), "¡Chill!", font=font, fill="#000000")
        elif recompensa == "Looser":
            draw.ellipse((70, 70, 130, 130), fill=(255, 223, 0))  # Círculo amarillo
            draw.text((30, 140), "¡Looser!", font=font, fill="#000000")
        elif recompensa == "Noob":
            draw.ellipse((70, 50, 130, 110), fill=(220, 220, 220))  # Calavera gris
            draw.text((10, 140), "¡Noob!", font=font, fill="#555")
        elif recompensa == "Semi Dios":
            draw.ellipse((60, 40, 140, 120), fill=(138, 43, 226))  # Elipse púrpura
            draw.text((10, 140), "¡Semi Dios!", font=font, fill="#fff")
        img = img.resize((100, 100), Image.LANCZOS)
        img.save(output_path)
    except Exception as e:
        print(f"Error al generar imagen para {recompensa}: {e}")

if __name__ == "__main__":
    os.makedirs("static/recompensas", exist_ok=True)
    for recompensa in ["Crack", "Chill", "Looser", "Noob", "Semi Dios"]:
        generar_imagen_recompensa(recompensa, f"static/recompensas/{recompensa.lower().replace(' ', '_')}.png")
