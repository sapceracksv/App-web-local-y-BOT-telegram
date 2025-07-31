# app.py
# Este archivo contiene el servidor web Flask que actúa como backend para la interfaz de búsqueda.

import os
import logging
from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template, url_for, send_from_directory
from werkzeug.utils import secure_filename

# Importa nuestros módulos personalizados
import database
from gender_predictor import infer_gender

# --- Configuración Inicial ---
load_dotenv() 
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='static', template_folder='templates')

IMAGE_DIRECTORY = os.getenv('IMAGE_BASE_PATH')

# --- Rutas de la Aplicación ---

@app.route('/')
def index():
    """Sirve la página principal de la aplicación web (index.html)."""
    return render_template('index.html')

@app.route('/dui-images/<path:filename>')
def serve_dui_image(filename):
    """Sirve las imágenes de forma segura desde el directorio especificado en .env."""
    if not IMAGE_DIRECTORY:
        logger.error("IMAGE_BASE_PATH no está configurado en el archivo .env.")
        return "Ruta de imágenes no configurada en el servidor.", 500
    
    safe_filename = secure_filename(filename)
    if not safe_filename or safe_filename != filename:
        logger.warning(f"Intento de acceso a archivo con nombre no seguro: {filename}")
        return "Nombre de archivo no válido.", 400
        
    return send_from_directory(IMAGE_DIRECTORY, safe_filename, as_attachment=False)


@app.route('/search', methods=['POST'])
def search():
    """Endpoint de la API que recibe las búsquedas desde el frontend."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Petición JSON vacía o mal formada"}), 400
    except Exception:
        return jsonify({"error": "El cuerpo de la petición no es un JSON válido"}), 400

    search_params = {key: value.strip() for key, value in data.items() if value and isinstance(value, str)}

    try:
        results = database.search_in_db(**search_params)
        logger.info(f"Búsqueda web encontró {len(results)} resultados para los criterios: {search_params}")

        # COMENTARIO PARA EL USUARIO:
        # El bucle 'for' a continuación procesa los resultados de la base de datos.
        # Las claves que se usan aquí (ej: result.get('Dui')) DEBEN COINCIDIR
        # con los alias (AS) que definiste en la consulta SELECT de `database.py`.
        for result in results:
            dui_val = result.get('Dui')
            if IMAGE_DIRECTORY and dui_val:
                filename_base = dui_val.strip()
                for extension in ['jpg', 'jpeg', 'png']:
                    image_filename = f"{filename_base}.{extension}"
                    if os.path.exists(os.path.join(IMAGE_DIRECTORY, image_filename)):
                        result['imagen_url'] = url_for('serve_dui_image', filename=image_filename)
                        break
            
            sexo_from_db = result.get('Sexo')
            if sexo_from_db == 'F':
                result['Sexo'] = 'Femenino'
            elif sexo_from_db == 'M':
                result['Sexo'] = 'Masculino'
            else:
                result['Sexo'] = infer_gender(result.get('NombreCompleto'))

        return jsonify(results)
        
    except Exception as e:
        logger.exception("Error inesperado durante la búsqueda en la base de datos.")
        return jsonify({"error": "Ocurrió un error interno en el servidor."}), 500

if __name__ == '__main__':
    # Ejecuta el servidor en modo de depuración para desarrollo local.
    app.run(debug=True, host='0.0.0.0', port=5000)
