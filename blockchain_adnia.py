import json
import hashlib
import time
import os

ARCHIVO_BLOCKCHAIN = "blockchain.json"

# Inicializa la cadena si no existe
def inicializar_blockchain():
    if not os.path.exists(ARCHIVO_BLOCKCHAIN):
        bloque_genesis = crear_bloque("Bloque Génesis", "0")
        with open(ARCHIVO_BLOCKCHAIN, "w", encoding="utf-8") as f:
            json.dump([bloque_genesis], f, indent=4)

# Crea un nuevo bloque con contenido
def crear_bloque(datos, hash_anterior):
    bloque = {
        "timestamp": time.time(),
        "datos": datos,
        "hash_anterior": hash_anterior,
    }
    bloque["hash"] = calcular_hash(bloque)
    return bloque

# Calcula el hash del bloque (SHA-256)
def calcular_hash(bloque):
    bloque_str = json.dumps({k: v for k, v in bloque.items() if k != "hash"}, sort_keys=True)
    return hashlib.sha256(bloque_str.encode()).hexdigest()

# Guarda un nuevo bloque en la cadena
def guardar_en_blockchain(datos):
    inicializar_blockchain()
    with open(ARCHIVO_BLOCKCHAIN, "r+", encoding="utf-8") as f:
        cadena = json.load(f)
        ultimo = cadena[-1]
        nuevo_bloque = crear_bloque(datos, ultimo["hash"])
        cadena.append(nuevo_bloque)
        f.seek(0)
        json.dump(cadena, f, indent=4)
    print(f"✅ Bloque registrado: {datos}")
