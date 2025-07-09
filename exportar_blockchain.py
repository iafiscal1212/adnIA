from fpdf import FPDF
import json
import os
from datetime import datetime

ARCHIVO_BLOCKCHAIN = "blockchain.json"
ARCHIVO_PDF = "blockchain_adnia.pdf"

class PDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 14)
        self.set_text_color(0, 255, 255)
        self.cell(0, 10, "ADNIA - Blockchain Jurídica", ln=True, align="C")
        self.set_font("Arial", "", 10)
        self.set_text_color(180, 180, 180)
        self.cell(0, 10, f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", ln=True, align="C")
        self.ln(10)

    def bloque(self, index, bloque):
        self.set_font("Arial", "B", 12)
        self.set_text_color(255, 255, 255)
        self.cell(0, 10, f"Bloque #{index}", ln=True)
        self.set_font("Arial", "", 10)

        try:
            timestamp = datetime.fromtimestamp(bloque['timestamp']).strftime('%d/%m/%Y %H:%M:%S')
            datos = bloque.get('datos', '[Sin datos]')
            hash_str = bloque.get('hash', '[Sin hash]')
            hash_ant = bloque.get('hash_anterior', '[Sin hash anterior]')

            # Sanitizar por seguridad
            datos = str(datos).replace("\n", " ").strip()
            hash_str = str(hash_str).strip()
            hash_ant = str(hash_ant).strip()

            self.multi_cell(0, 8, f"Fecha: {timestamp}")
            self.multi_cell(0, 8, f"Datos: {datos[:500]}")
            self.cell(0, 8, f"Hash: {hash_str[:32]}", ln=True)
            self.cell(0, 8, f"{hash_str[32:]}", ln=True)
            self.cell(0, 8, f"Hash anterior: {hash_ant[:32]}", ln=True)
            self.cell(0, 8, f"{hash_ant[32:]}", ln=True)
            self.ln(5)

        except Exception as e:
            self.set_text_color(255, 100, 100)
            self.cell(0, 8, f"[Error en bloque {index}]", ln=True)
            msg = f"{str(e)}"[:50]
            self.cell(0, 8, f"Motivo: {msg}", ln=True)
            self.set_text_color(255, 255, 255)

def exportar_a_pdf():
    if not os.path.exists(ARCHIVO_BLOCKCHAIN):
        print("❌ No existe blockchain.json")
        return

    with open(ARCHIVO_BLOCKCHAIN, "r", encoding="utf-8") as f:
        cadena = json.load(f)

    documento = PDF()
    documento.set_auto_page_break(auto=True, margin=15)
    documento.add_page()
    documento.set_fill_color(0, 0, 0)
    documento.set_draw_color(0, 255, 255)
    documento.set_text_color(255, 255, 255)

    for i, bloque in enumerate(cadena):
        documento.bloque(i, bloque)

    documento.output(ARCHIVO_PDF)
    print(f"✅ Blockchain exportada a {ARCHIVO_PDF}")

if __name__ == "__main__":
    exportar_a_pdf()
