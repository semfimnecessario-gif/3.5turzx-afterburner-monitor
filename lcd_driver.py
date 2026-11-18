import serial
import struct
from PIL import Image

class TurzxDisplay:
    def __init__(self, port: str, baudrate: int = 115200):
        self.ser = serial.Serial(port, baudrate, timeout=1, rtscts=True)
        self.width = 480
        self.height = 320

    def _send_command(self, cmd: int, x: int = 0, y: int = 0, ex: int = 0, ey: int = 0):
        # Protocolo padrão de 6 bytes do controlador USB Serial 3.5"
        byte_buffer = bytearray(6)
        byte_buffer[0] = (x >> 2)
        byte_buffer[1] = (((x & 3) << 6) + (y >> 4))
        byte_buffer[2] = (((y & 15) << 4) + (ex >> 6))
        byte_buffer[3] = (((ex & 63) << 2) + (ey >> 8))
        byte_buffer[4] = (ey & 255)
        byte_buffer[5] = cmd
        self.ser.write(byte_buffer)

    def set_orientation(self, landscape: bool = True):
        # 109 = Set Orientation (0: Portrait, 2: Landscape)
        mode = 2 if landscape else 0
        byte_buffer = bytearray(6)
        byte_buffer[5] = 109
        byte_buffer[0] = mode
        self.ser.write(byte_buffer)

    def display_image(self, img: Image.Image):
        # Redimensiona e converte RGB888 para RGB565 Little-Endian
        img = img.resize((self.width, self.height)).convert("RGB")
        pixels = img.load()
        
        rgb565_data = bytearray()
        for y in range(self.height):
            for x in range(self.width):
                r, g, b = pixels[x, y]
                rgb565 = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
                rgb565_data += struct.pack("<H", rgb565)

        # Comando 197 = Display Bitmap
        self._send_command(197, 0, 0, self.width - 1, self.height - 1)
        self.ser.write(rgb565_data)

    def close(self):
        self.ser.close()