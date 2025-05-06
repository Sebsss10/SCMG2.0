from flask import Flask, request, jsonify, render_template, session, redirect, url_for
import os
import google.generativeai as genai
from bot_gestor import responder
from database_queries import (
    listar_doctores,
    autenticar_doctor,
    obtener_citas_por_doctor,
    actualizar_estado_cita,
    obtener_historial_paciente
)

app = Flask(__name__, template_folder='.')
app.debug = True
app.secret_key = os.urandom(24)  # For session management

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

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        doctor = autenticar_doctor(username)
        print(f"Login attempt: username={username}, doctor={doctor}")  
        if doctor and doctor['password'] == password:
            session['doctor_id'] = doctor['id']
            session['doctor_nombre'] = doctor['nombre']
            print(f"Login successful: doctor_id={doctor['id']}")  
            return redirect(url_for('doctor_dashboard'))
        print("Login failed: Invalid credentials")  
        return render_template('login.html', error="Usuario o contraseña incorrectos")
    return render_template('login.html')

@app.route('/doctor_dashboard')
def doctor_dashboard():
    if 'doctor_id' not in session:
        print("Unauthorized access to dashboard: No doctor_id in session")  
        return redirect(url_for('login'))
    doctor_id = session['doctor_id']
    citas = obtener_citas_por_doctor(doctor_id)
    print(f"Loading dashboard for doctor_id={doctor_id}, citas={len(citas)}")  
    return render_template('doctor_dashboard.html', citas=citas, doctor_nombre=session['doctor_nombre'])

@app.route('/update_appointment_status', methods=['POST'])
def update_appointment_status():
    if 'doctor_id' not in session:
        print("Unauthorized access to update_appointment_status")
        return jsonify({'error': 'No autorizado'}), 401
    cita_id = request.form.get('cita_id')
    status = request.form.get('status')
    print(f"Updating appointment: cita_id={cita_id}, status={status}") 
    if actualizar_estado_cita(cita_id, status):
        return jsonify({'success': True})
    return jsonify({'error': 'Error al actualizar el estado'}), 500

@app.route('/patient_history', methods=['POST'])
def patient_history():
    if 'doctor_id' not in session:
        print("Unauthorized access to patient_history") 
        return jsonify({'error': 'No autorizado'}), 401
    carnet_paciente = request.form.get('carnet_paciente')
    historial = obtener_historial_paciente(carnet_paciente)
    print(f"Fetching patient history: carnet={carnet_paciente}, historial={len(historial)}") 
    return jsonify({'historial': historial})

@app.route('/logout')
def logout():
    session.pop('doctor_id', None)
    session.pop('doctor_nombre', None)
    print("User logged out")
    return redirect(url_for('login'))

@app.route('/chatbot', methods=['POST'])
def chatbot_endpoint():
    try:
        data = request.get_json()
        user_message = data.get('message')
        print(f"Chatbot received: {user_message}")
        if not user_message:
            return jsonify({'error': 'Mensaje no proporcionado'}), 400
        reply = responder(user_message)
        print(f"Chatbot response: {reply}")
        return jsonify({'respuesta': reply})
    except Exception as e:
        print(f"Error en el endpoint del chatbot: {e}") 
        return jsonify({'error': 'Ocurrió un error interno'}), 500

if __name__ == '__main__':
    print("Starting Flask application...")
    app.run(debug=True)