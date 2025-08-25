# -*- coding: utf-8 -*-
# puente_impresora.py (CON CORRECCIÓN DE CORS)

import sys
import socket
from flask import Flask, request, jsonify
from flask_cors import CORS  # <-- 1. IMPORTAR CORS
import win32print

# --- CONFIGURACIÓN DE INSTANCIA ÚNICA ---
LOCK_SOCKET = None

def acquire_lock():
    global LOCK_SOCKET
    try:
        LOCK_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        LOCK_SOCKET.bind(('127.0.0.1', 5001))
        return True
    except socket.error:
        return False

def release_lock():
    global LOCK_SOCKET
    if LOCK_SOCKET:
        LOCK_SOCKET.close()

# ----------------------------------------

app = Flask(__name__)
CORS(app)  # <-- 2. HABILITAR CORS PARA TODA LA APLICACIÓN

@app.route('/print', methods=['POST', 'OPTIONS'])
def print_ticket():
    # El método OPTIONS se maneja automáticamente por flask-cors
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
        
    try:
        impresora_nombre = win32print.GetDefaultPrinter()
        
        data = request.json
        ticket_text = data.get('ticket_text', '')

        if not ticket_text:
            return jsonify({"status": "error", "message": "No se recibió texto"}), 400

        # Usamos 'cp850' que es común para tickets en español
        raw_data = ticket_text.encode('cp850', errors='replace')
        
        # Añadir comando de corte al final
        raw_data += b'\x1d\x56\x00'

        hPrinter = win32print.OpenPrinter(impresora_nombre)
        try:
            hJob = win32print.StartDocPrinter(hPrinter, 1, ("Ticket de Venta", None, "RAW"))
            try:
                win32print.StartPagePrinter(hPrinter)
                win32print.WritePrinter(hPrinter, raw_data)
                win32print.EndPagePrinter(hPrinter)
            finally:
                win32print.EndDocPrinter(hPrinter)
        finally:
            win32print.ClosePrinter(hPrinter)
        
        print("Ticket impreso exitosamente.")
        return jsonify({"status": "success", "message": "Ticket impreso"})

    except Exception as e:
        error_message = f"Error de Impresión: {e}"
        print(error_message)
        return jsonify({"status": "error", "message": error_message}), 500

if __name__ == '__main__':
    if not acquire_lock():
        print("Otra instancia del programa ya se está ejecutando. Terminando...")
        sys.exit(0)
    try:
        print("Servicio de impresión iniciado en http://127.0.0.1:5000")
        print("Presiona CTRL+C para detener.")
        app.run(host='127.0.0.1', port=5000)
    finally:
        release_lock()