import hashlib
import json
from time import time
from datetime import datetime
import logging

# Dificultad de la Prueba de Trabajo (Proof of Work)
# Cuanto mayor sea el número, más difícil será minar un bloque.
MINING_DIFFICULTY = 4 
BLOCKCHAIN_FILE = 'adnia_chain.json'

class Blockchain:
    def __init__(self):
        self.chain = []
        self.pending_transactions = []
        self.load_chain_from_disk()

    def load_chain_from_disk(self):
        """Carga la cadena de bloques desde un archivo JSON."""
        try:
            with open(BLOCKCHAIN_FILE, 'r') as f:
                chain_data = json.load(f)
                self.chain = chain_data
                logging.info(f"Blockchain cargada desde {BLOCKCHAIN_FILE}. {len(self.chain)} bloques.")
        except (FileNotFoundError, json.JSONDecodeError):
            # Si el archivo no existe o está dañado, crea el bloque génesis
            self.chain = [self.create_genesis_block()]
            self.save_chain_to_disk()
            logging.info("No se encontró una blockchain válida. Se ha creado una nueva con el bloque génesis.")

    def save_chain_to_disk(self):
        """Guarda la cadena de bloques completa en un archivo JSON."""
        with open(BLOCKCHAIN_FILE, 'w') as f:
            json.dump(self.chain, f, indent=4)

    def create_genesis_block(self):
        """Crea el primer bloque de la cadena (bloque génesis)."""
        genesis_block = {
            'index': 0,
            'timestamp': time(),
            'transactions': [{'action': 'Bloque Génesis Creado', 'user': 'Sistema', 'timestamp': datetime.now().isoformat()}],
            'nonce': 0,
            'previous_hash': '0'
        }
        # La prueba de trabajo también se aplica al bloque génesis
        genesis_block['hash'] = self.proof_of_work(genesis_block)
        return genesis_block

    @staticmethod
    def calculate_hash(block):
        """Calcula el hash SHA-256 de un bloque."""
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def get_latest_block(self):
        """Devuelve el último bloque de la cadena."""
        return self.chain[-1]

    def add_transaction(self, action_details, user):
        """Añade una nueva transacción a la lista de transacciones pendientes para ser minadas."""
        self.pending_transactions.append({
            'action': action_details,
            'user': user,
            'timestamp': datetime.now().isoformat()
        })
        return self.get_latest_block()['index'] + 1

    def proof_of_work(self, block):
        """
        Encuentra un hash que cumpla con la dificultad establecida (empiece con '0' * MINING_DIFFICULTY).
        """
        nonce = 0
        while True:
            block['nonce'] = nonce
            hash_attempt = self.calculate_hash(block)
            if hash_attempt.startswith('0' * MINING_DIFFICULTY):
                return hash_attempt
            nonce += 1

    def mine_block(self):
        """
        Mina un nuevo bloque: realiza la prueba de trabajo y lo añade a la cadena.
        """
        if not self.pending_transactions:
            logging.info("No hay transacciones pendientes para minar.")
            return None

        latest_block = self.get_latest_block()
        new_block_data = {
            'index': latest_block['index'] + 1,
            'timestamp': time(),
            'transactions': self.pending_transactions,
            'previous_hash': latest_block['hash']
        }

        # Realiza la prueba de trabajo para encontrar el hash válido
        new_hash = self.proof_of_work(new_block_data)
        new_block = new_block_data
        new_block['hash'] = new_hash
        
        logging.info(f"Nuevo bloque minado con éxito. Hash: {new_block['hash']}")
        
        self.chain.append(new_block)
        self.pending_transactions = []
        self.save_chain_to_disk()
        
        return new_block
