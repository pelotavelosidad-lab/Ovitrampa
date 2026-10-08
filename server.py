
from flask import Flask, request, render_template, jsonify, send_from_directory
from datetime import datetime
from pathlib import Path

app = Flask(__name__)

# ==========================================================
# CONFIGURACIÓN
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent
IMAGE_DIR = BASE_DIR / "images"

IMAGE_DIR.mkdir(exist_ok=True)

# Último análisis realizado por la IA
ultimo_resultado = {
    "huevos": 0,
    "confianza": 0,
    "fecha": "Sin datos",
    "estado": "Esperando primera imagen"
}


# ==========================================================
# PÁGINA PRINCIPAL
# ==========================================================

@app.route("/")
def index():

    imagenes = sorted(
        IMAGE_DIR.glob("*.jpg"),
        key=lambda x: x.stat().st_mtime,
        reverse=True
    )

    ultima_imagen = None

    if imagenes:
        ultima_imagen = imagenes[0].name

    return render_template(
        "index.html",
        ultima_imagen=ultima_imagen,
        resultado=ultimo_resultado
    )


# ==========================================================
# RECIBIR IMAGEN DEL ESP32
# ==========================================================

@app.route("/upload", methods=["POST"])
def upload():

    if not request.data:
        return jsonify({
            "ok": False,
            "error": "No se recibió ninguna imagen"
        }), 400

    # Fecha y hora
    ahora = datetime.now()

    nombre = ahora.strftime(
        "foto_%Y%m%d_%H%M%S.jpg"
    )

    ruta = IMAGE_DIR / nombre

    # Guardar imagen
    with open(ruta, "wb") as archivo:
        archivo.write(request.data)

    print()
    print("====================================")
    print("📷 NUEVA IMAGEN RECIBIDA")
    print("====================================")
    print(f"Archivo: {nombre}")
    print(f"Tamaño: {len(request.data)} bytes")
    print(f"Hora: {ahora.strftime('%d/%m/%Y %H:%M:%S')}")
    print("====================================")

    # ======================================================
    # AQUÍ CONECTAREMOS LA IA DESPUÉS
    # ======================================================

    # Por ahora solamente dejamos el resultado en 0.
    ultimo_resultado["fecha"] = ahora.strftime(
        "%d/%m/%Y %H:%M:%S"
    )

    ultimo_resultado["estado"] = "Imagen recibida"

    return jsonify({
        "ok": True,
        "mensaje": "Imagen recibida correctamente",
        "archivo": nombre
    })


# ==========================================================
# MOSTRAR IMÁGENES
# ==========================================================

@app.route("/images/<filename>")
def images(filename):

    return send_from_directory(
        IMAGE_DIR,
        filename
    )


# ==========================================================
# API PARA CONSULTAR RESULTADO
# ==========================================================

@app.route("/api/resultado")
def resultado():

    return jsonify(ultimo_resultado)


# ==========================================================
# EJECUTAR SERVIDOR
# ==========================================================

if __name__ == "__main__":

    print()
    print("======================================")
    print("       🦟 OVITRAMPA SERVER")
    print("======================================")
    print()
    print("Servidor iniciado.")
    print()
    print("Abrir en esta PC:")
    print("http://127.0.0.1:5000")
    print()
    print("Para el ESP32 usar la IP de esta PC:")
    print("http://IP_DE_TU_PC:5000/upload")
    print()
    print("======================================")

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )

