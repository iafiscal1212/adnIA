# blockchain_adnia.py (MEJORADO CON CACHING - JULIO 2025)

import json
import hashlib
import time
import os
from functools import lru_cache

ARCHIVO_BLOCKCHAIN = "blockchain.json"

def inicializar_blockchain():
    if not os.path.exists(ARCHIVO_BLOCKCHAIN):
        bloque_genesis = crear_bloque("Bloque Génesis", "0")
        with open(ARCHIVO_BLOCKCHAIN, "w", encoding="utf-8") as f:
            json.dump([bloque_genesis], f, indent=4)

def crear_bloque(datos, hash_anterior):
    bloque = {
        "timestamp": time.time(),
        "datos": datos,
        "hash_anterior": hash_anterior,
    }
    bloque["hash"] = calcular_hash(bloque)
    return bloque

def calcular_hash(bloque):
    bloque_str = json.dumps({k: v for k, v in bloque.items() if k != "hash"}, sort_keys=True)
    return hashlib.sha256(bloque_str.encode()).hexdigest()

@lru_cache(maxsize=50)  # NUEVO: Cache para lecturas frecuentes
def load_cadena():
    with open(ARCHIVO_BLOCKCHAIN, "r", encoding="utf-8") as f:
        return json.load(f)

def guardar_en_blockchain(datos):
    inicializar_blockchain()
    cadena = load_cadena()  # Usa cache
    ultimo = cadena[-1]
    nuevo_bloque = crear_bloque(datos, ultimo["hash"])
    cadena.append(nuevo_bloque)
    with open(ARCHIVO_BLOCKCHAIN, "w", encoding="utf-8") as f:
        json.dump(cadena, f, indent=4)
    load_cadena.cache_clear()  # Invalida cache después de write
    print(f"✅ Bloque registrado: {datos}")
