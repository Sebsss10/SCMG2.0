from flask import Flask, request, jsonify, render_template
import os
import google.generativeai as genai
from bot_gestor import responder

app = Flask(__name__, template_folder='.')
app.debug = True

# --- Configuración de la API de Gemini ---
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-2.0-flash')
else:
    model = None
    print("Advertencia: La clave de API de Gemini no está configurada. La funcionalidad de Gemini no estará disponible.")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chatbot', methods=['POST'])
def chatbot_endpoint():
    try:
        data = request.get_json()
        user_message = data.get('message')
        if not user_message:
            return jsonify({'error': 'Mensaje no proporcionado'}), 400

        reply = responder(user_message)
        return jsonify({'respuesta': reply})

    except Exception as e:
        print(f"Error en el endpoint del chatbot: {e}")
        return jsonify({'error': 'Ocurrió un error interno'}), 500

if __name__ == '__main__':
    app.run(debug=True)