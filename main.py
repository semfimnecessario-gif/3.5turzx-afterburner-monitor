import json
import time
from PIL import Image, ImageDraw, ImageFont
from afterburner import AfterburnerReader
from media_info import get_current_media
from lcd_driver import TurzxDisplay

def load_config():
    with open("config.json", "r", encoding="utf-8") as f:
        return json.load(f)

def render_dashboard(config, sensor_data, media_data) -> Image.Image:
    theme = config["theme"]
    img = Image.new("RGB", (480, 320), color=theme["bg_color"])
    draw = ImageDraw.Draw(img)

    # Fontes padrão (você pode apontar para um arquivo .ttf na pasta)
    font_title = ImageFont.load_default(size=14)
    font_val = ImageFont.load_default(size=26)
    font_media = ImageFont.load_default(size=15)

    # 1. Grid de Sensores (2 linhas x 3 colunas)
    sensors = config["sensors"][:6]
    col_w, row_h = 150, 95
    for idx, item in enumerate(sensors):
        col = idx % 3
        row = idx // 3
        x = 15 + (col * col_w)
        y = 15 + (row * row_h)

        # Card de fundo
        draw.rounded_rectangle([x, y, x + 140, y + 85], radius=8, outline=theme["accent_color"], width=1)
        
        # Label do sensor
        draw.text((x + 10, y + 10), item["label"], fill=theme["muted_color"], font=font_title)
        
        # Valor lido do Afterburner
        raw_val = sensor_data.get(item["source"], "--")
        val_str = f"{raw_val}{item['unit']}" if raw_val != "--" else "N/A"
        draw.text((x + 10, y + 38), val_str, fill=theme["text_color"], font=font_val)

    # 2. Barra Inferior de Mídia (Spotify / Windows Media)
    draw.rounded_rectangle([15, 215, 465, 305], radius=8, fill="#161616", outline="#333333", width=1)
    status_icon = "▶ TOCANDO" if media_data["playing"] else "⏸ PAUSADO"
    draw.text((28, 225), status_icon, fill=theme["accent_color"], font=font_title)
    
    title = media_data["title"][:42] + ("..." if len(media_data["title"]) > 42 else "")
    artist = media_data["artist"][:48]
    draw.text((28, 248), title, fill=theme["text_color"], font=font_media)
    draw.text((28, 272), artist, fill=theme["muted_color"], font=font_title)

    return img

def main():
    config = load_config()
    ab_reader = AfterburnerReader()
    display = TurzxDisplay(port=config["com_port"])
    display.set_orientation(landscape=(config["orientation"] == "landscape"))

    print(f"Iniciando dashboard na porta {config['com_port']}... Pressione Ctrl+C para sair.")
    try:
        while True:
            sensors = ab_reader.get_sensors()
            media = get_current_media()
            frame = render_dashboard(config, sensors, media)
            display.display_image(frame)
            time.sleep(config["refresh_rate"])
    except KeyboardInterrupt:
        print("\nEncerrando...")
    finally:
        display.close()

if __name__ == "__main__":
    main()