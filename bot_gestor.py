import os
import google.generativeai as genai
import re
from database_queries import (
    listar_doctores,
    buscar_doctor_por_especialidad,
    guardar_cita,
    consultar_cita_por_carnet,
    buscar_doctores_por_especialidad,
    buscar_citas_por_paciente,
    actualizar_cita,
    eliminar_cita,
    buscar_citas_disponibles_por_dia_especialidad
)

# --- Configuración de la API de Gemini ---
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-2.0-flash')
else:
    model = None
    print("Advertencia: La clave de API de Gemini no está configurada.")

estado_conversacion = {}

def procesar_pregunta_general(user_message):
    """Función para procesar preguntas generales usando la API de Gemini"""
    if model is None:
        return "Lo siento, la funcionalidad de Gemini no está disponible. Por favor, verifica la configuración de la API."
    try:
        response = model.generate_content(user_message)
        return response.text
    except Exception as e:
        return f"Lo siento, hubo un error al procesar tu pregunta. Por favor intenta nuevamente. Error: {str(e)}"

def responder(user_message):
    global estado_conversacion
    chatbot_reply = ""
    user_message_lower = user_message.lower()

    # 1. Intenta entender la intención del usuario usando lógica directa (palabras clave)
    if "hola" in user_message_lower:
        return (
            "¡Hola! ¿En qué puedo ayudarte hoy? \n"
            "Puedo asistirte con lo siguiente:\n"
            "- Mostrar todos los doctores.\n"
            "- Agendar, actualizar o eliminar citas médicas.\n"
            "- Consultar información sobre tus citas existentes.\n"
            "- Buscar doctores por especialidad.\n"
            "- Ver citas disponibles por fecha y especialidad.\n"
            "- Brindarte soporte médico con la asistencia de la IA.\n"
            "Solo dime lo que necesitas y estaré encantado de ayudarte."
        )

    elif "listar doctores" in user_message_lower or "mostrar todos los doctores" in user_message_lower or "¿qué doctores hay?" in user_message_lower or "quisiera ver la lista de doctores" in user_message_lower or "nómina de doctores" in user_message_lower or "doctores disponibles" in user_message_lower:
        estado_conversacion['ultimo_intento'] = None
        doctores = listar_doctores()
        if doctores:
            chatbot_reply += "Listado de todos los doctores:\n"
            for doctor in doctores:
                chatbot_reply += f"- Nombre: {doctor['nombre']}, Especialidad: {doctor['especialidad']}\n"
        else:
            chatbot_reply = "No se encontraron doctores en la base de datos."
        return chatbot_reply
    elif "agendar cita" in user_message_lower or "quiero agendar cita" in user_message_lower:
        estado_conversacion['ultimo_intento'] = 'agendar_cita'
        estado_conversacion['cita_pendiente'] = {}
        return "Entendido. ¿Cuál es el nombre del paciente?"
    elif estado_conversacion.get('ultimo_intento') == 'agendar_cita':
        cita_pendiente = estado_conversacion.get('cita_pendiente', {})
        if not cita_pendiente.get('nombre_paciente'):
            cita_pendiente['nombre_paciente'] = user_message.strip()
            estado_conversacion['cita_pendiente'] = cita_pendiente
            return "¿Cuál es el número de carnet del paciente?"
        elif not cita_pendiente.get('carnet_paciente'):
            cita_pendiente['carnet_paciente'] = user_message.strip()
            estado_conversacion['cita_pendiente'] = cita_pendiente
            return "¿Qué especialidad de doctor necesita?"
        elif not cita_pendiente.get('especialidad'):
            cita_pendiente['especialidad'] = user_message.strip()
            doctor = buscar_doctor_por_especialidad(cita_pendiente['especialidad'])
            if doctor:
                cita_pendiente['doctor_id'] = doctor['id']
                cita_pendiente['doctor_nombre'] = doctor['nombre']
                estado_conversacion['cita_pendiente'] = cita_pendiente
                estado_conversacion['esperando_fecha'] = True
                return f"Hemos encontrado a {doctor['nombre']} ({cita_pendiente['especialidad']}). ¿Qué día desea la cita (YYYY-MM-DD)?"
            else:
                estado_conversacion['ultimo_intento'] = None
                estado_conversacion['cita_pendiente'] = {}
                return f"No hay doctores disponibles con la especialidad de '{cita_pendiente['especialidad']}' en este momento."
        elif estado_conversacion.get('esperando_fecha') and not cita_pendiente.get('fecha'):
            if re.match(r"^\d{4}-\d{2}-\d{2}$", user_message.strip()):
                cita_pendiente['fecha'] = user_message.strip()
                estado_conversacion['cita_pendiente'] = cita_pendiente
                estado_conversacion['esperando_hora'] = True
                return "¿A qué hora (HH:MM)?"
            else:
                return "Formato de fecha incorrecto. Por favor, use YYYY-MM-DD."
        elif estado_conversacion.get('esperando_hora') and not cita_pendiente.get('hora'):
            if re.match(r"^\d{2}:\d{2}$", user_message.strip()):
                cita_pendiente['hora'] = user_message.strip()
                if guardar_cita(
                    cita_pendiente['nombre_paciente'],
                    cita_pendiente['carnet_paciente'],
                    cita_pendiente['doctor_id'],
                    cita_pendiente['fecha'],
                    cita_pendiente['hora']
                ):
                    chatbot_reply = f"Cita agendada para {cita_pendiente['nombre_paciente']} (Carnet: {cita_pendiente['carnet_paciente']}) con {cita_pendiente['doctor_nombre']} el {cita_pendiente['fecha']} a las {cita_pendiente['hora']}."
                else:
                    chatbot_reply = "Error al agendar la cita."
                estado_conversacion['ultimo_intento'] = None
                estado_conversacion['cita_pendiente'] = {}
                estado_conversacion.pop('esperando_fecha', None)
                estado_conversacion.pop('esperando_hora', None)
                return chatbot_reply
            else:
                return "Formato de hora incorrecto. Por favor, use HH:MM."
    elif re.search(r"(dime mi cita|cual es mi cita)", user_message_lower):
        estado_conversacion['ultimo_intento'] = 'consultar_cita'
        return "Por favor, proporcióname tu número de carnet."
    elif estado_conversacion.get('ultimo_intento') == 'consultar_cita' and re.match(r"^\d{4,10}$", user_message.strip()):
        carnet = user_message.strip()
        cita = consultar_cita_por_carnet(carnet)
        if cita:
            chatbot_reply = f"Tu próxima cita es el {cita['fecha']} a las {cita['hora']} con {cita['doctor_nombre']} ({cita['especialidad']})."
        else:
            chatbot_reply = f"No se encontró ninguna cita registrada con el carnet: {carnet}."
        estado_conversacion['ultimo_intento'] = None
        return chatbot_reply
    elif "eliminar cita" in user_message_lower or "cancelar cita" in user_message_lower or "necesito cancelar mi cita" in user_message_lower:
        estado_conversacion['ultimo_intento'] = 'eliminar_cita'
        return "¿Cuál es el carnet del paciente de la cita que desea eliminar?"
    elif estado_conversacion.get('ultimo_intento') == 'eliminar_cita' and re.match(r"^\d{4,10}$", user_message.strip()):
        carnet_eliminar = user_message.strip()
        registros_eliminados = eliminar_cita(carnet_eliminar)
        if registros_eliminados > 0:
            chatbot_reply = f"Se eliminó la cita asociada al carnet {carnet_eliminar}."
        else:
            chatbot_reply = f"No se encontró ninguna cita con el carnet {carnet_eliminar} para eliminar."
        estado_conversacion['ultimo_intento'] = None
        return chatbot_reply
    elif re.search(r"(buscar|encontrar) doctor con especialidad en (.+)", user_message_lower):
        match = re.search(r"(buscar|encontrar) doctor con especialidad en (.+)", user_message_lower)
        if match:
            especialidad = match.group(2).strip()
            doctores = buscar_doctores_por_especialidad(especialidad)
            chatbot_reply = ""
            if doctores:
                chatbot_reply += f"Doctores encontrados con la especialidad de '{especialidad}':\n"
                for doctor in doctores:
                    chatbot_reply += f"- {doctor['nombre']}\n"
            else:
                chatbot_reply += f"No se encontraron doctores con la especialidad de '{especialidad}'.\n"
            return chatbot_reply
        else:
            return procesar_pregunta_general(user_message)
    elif "citas disponibles" in user_message_lower or "¿hay citas disponibles?" in user_message_lower:
        estado_conversacion['ultimo_intento'] = 'consultar_disponibilidad_dia'
        return "¿Para qué día le gustaría consultar la disponibilidad (YYYY-MM-DD)?"
    elif estado_conversacion.get('ultimo_intento') == 'consultar_disponibilidad_dia':
        fecha_consulta = user_message.strip()
        if re.match(r"^\d{4}-\d{2}-\d{2}$", fecha_consulta):
            estado_conversacion['fecha_consulta'] = fecha_consulta
            estado_conversacion['ultimo_intento'] = 'consultar_disponibilidad_especialidad'
            return "¿Y en qué especialidad está interesado?"
        else:
            return "Formato de fecha incorrecto. Por favor, use YYYY-MM-DD."
    elif estado_conversacion.get('ultimo_intento') == 'consultar_disponibilidad_especialidad' and 'fecha_consulta' in estado_conversacion:
        especialidad_consulta = user_message.strip()
        fecha_consulta = estado_conversacion.pop('fecha_consulta')
        estado_conversacion['ultimo_intento'] = None
        citas_disponibles = buscar_citas_disponibles_por_dia_especialidad(fecha_consulta, especialidad_consulta)
        if citas_disponibles:
            chatbot_reply += f"Citas disponibles para el {fecha_consulta} en la especialidad de '{especialidad_consulta}':\n"
            for cita in citas_disponibles:
                chatbot_reply += f"- Doctor: {cita['doctor_nombre']}, Hora: {cita['hora']}\n"
        else:
            chatbot_reply = f"No hay citas disponibles para el {fecha_consulta} en la especialidad de '{especialidad_consulta}'."
        return chatbot_reply
    elif re.search(r"(actualizar|cambiar) cita", user_message_lower):
        estado_conversacion['ultimo_intento'] = 'actualizar_cita_carnet'
        return "Por favor, proporcione el número de carnet del paciente cuya cita desea actualizar."
    elif estado_conversacion.get('ultimo_intento') == 'actualizar_cita_carnet' and re.match(r"^\d{4,10}$", user_message.strip()):
        carnet_actualizar = user_message.strip()
        estado_conversacion['carnet_actualizar'] = carnet_actualizar
        estado_conversacion['ultimo_intento'] = 'actualizar_cita_cambio_doctor'
        return f"¿Desea también cambiar de doctor para esta cita (sí/no)?"
    elif estado_conversacion.get('ultimo_intento') == 'actualizar_cita_cambio_doctor' and 'carnet_actualizar' in estado_conversacion:
        respuesta_cambio_doctor = user_message_lower.strip()
        if respuesta_cambio_doctor == 'si' or respuesta_cambio_doctor == 'sí':
            estado_conversacion['cambiar_doctor'] = True
            estado_conversacion['ultimo_intento'] = 'actualizar_cita_especialidad_nuevo_doctor'
            return "¿Qué especialidad de doctor le gustaría?"
        elif respuesta_cambio_doctor == 'no':
            estado_conversacion['cambiar_doctor'] = False
            estado_conversacion['ultimo_intento'] = 'actualizar_cita_fecha'
            return f"¿Para qué nueva fecha desea agendar la cita para el carnet {estado_conversacion['carnet_actualizar']} (YYYY-MM-DD)?"
        else:
            return "Respuesta no válida. Por favor, responda 'sí' o 'no'."
    elif estado_conversacion.get('ultimo_intento') == 'actualizar_cita_especialidad_nuevo_doctor' and 'carnet_actualizar' in estado_conversacion:
        especialidad_nuevo_doctor = user_message.strip()
        doctor = buscar_doctor_por_especialidad(especialidad_nuevo_doctor)
        if doctor:
            estado_conversacion['nuevo_doctor_id'] = doctor['id']
            estado_conversacion['nuevo_doctor_nombre'] = doctor['nombre']
            estado_conversacion['ultimo_intento'] = 'actualizar_cita_fecha'
            return f"Ha seleccionado a {doctor['nombre']} ({especialidad_nuevo_doctor}). ¿Para qué nueva fecha desea la cita (YYYY-MM-DD)?"
        else:
            return f"No se encontraron doctores con la especialidad de '{especialidad_nuevo_doctor}'. ¿Desea intentar con otra especialidad (sí/no)?"
    elif estado_conversacion.get('ultimo_intento') == 'actualizar_cita_fecha' and 'carnet_actualizar' in estado_conversacion:
        nueva_fecha = user_message.strip()
        if re.match(r"^\d{4}-\d{2}-\d{2}$", nueva_fecha):
            estado_conversacion['nueva_fecha'] = nueva_fecha
            estado_conversacion['ultimo_intento'] = 'actualizar_cita_hora'
            return "¿Y a qué nueva hora (HH:MM)?"
        else:
            return "Formato de fecha incorrecto. Por favor, use YYYY-MM-DD."
    elif estado_conversacion.get('ultimo_intento') == 'actualizar_cita_hora' and 'carnet_actualizar' in estado_conversacion and 'nueva_fecha' in estado_conversacion:
        nueva_hora = user_message.strip()
        carnet_actualizar = estado_conversacion.pop('carnet_actualizar')
        nueva_fecha = estado_conversacion.pop('nueva_fecha')
        nuevo_doctor_id = estado_conversacion.pop('nuevo_doctor_id', None)
        estado_conversacion.pop('cambiar_doctor', None)
        nuevo_doctor_nombre = estado_conversacion.pop('nuevo_doctor_nombre', None)
        estado_conversacion['ultimo_intento'] = None
        registros_actualizados = actualizar_cita(carnet_actualizar, nueva_fecha, nueva_hora, nuevo_doctor_id)
        if registros_actualizados > 0:
            mensaje_actualizacion = f"Se actualizó la cita para el carnet {carnet_actualizar} a la fecha {nueva_fecha} y hora {nueva_hora}."
            if nuevo_doctor_nombre:
                mensaje_actualizacion += f" También se cambió el doctor a {nuevo_doctor_nombre}."
            return mensaje_actualizacion
        else:
            return f"No se encontró ninguna cita para el carnet {carnet_actualizar} o hubo un error al actualizar."
    else:
        return procesar_pregunta_general(user_message)