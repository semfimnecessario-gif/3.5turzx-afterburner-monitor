import mmap
import struct

class AfterburnerReader:
    def __init__(self):
        self.map_name = "MAHMSharedMemory"

    def get_sensors(self) -> dict:
        sensors = {}
        try:
            # Abre a memória compartilhada criada pelo MSI Afterburner
            shm = mmap.mmap(-1, 256 * 1024, tagname=self.map_name, access=mmap.ACCESS_READ)
            
            # Lê o cabeçalho (Signature, Version, HeaderSize, NumEntries, EntrySize, Time)
            header_data = shm.read(24)
            sig, version, header_size, num_entries, entry_size, _ = struct.unpack("<4sIIIII", header_data)
            
            if sig != b"MAHM":
                shm.close()
                return sensors

            for i in range(num_entries):
                offset = header_size + (i * entry_size)
                shm.seek(offset)
                entry_data = shm.read(entry_size)
                
                # Nome do sensor (260 bytes), Unidade (260 bytes), Valor atual (float no offset 1300)
                name = entry_data[0:260].split(b'\x00')[0].decode('latin-1', errors='ignore')
                data_val = struct.unpack("<f", entry_data[1300:1304])[0]
                
                # Filtra valores inválidos (FLT_MAX)
                if data_val < 1e10:
                    sensors[name] = round(data_val, 1)
                    
            shm.close()
        except FileNotFoundError:
            # MSI Afterburner não está rodando
            pass
        except Exception as e:
            print(f"Erro ao ler Afterburner: {e}")
            
        return sensors