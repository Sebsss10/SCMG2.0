import mysql.connector

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'agenda_medica'
}

def conectar_db():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as err:
        print(f"Error al conectar a la base de datos: {err}")
        return None

def autenticar_doctor(username):
    conn = conectar_db()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, nombre, password FROM doctores WHERE username = %s AND activo = 1", (username,))
        doctor = cursor.fetchone()
        conn.close()
        return doctor
    return None

def obtener_citas_por_doctor(doctor_id):
    conn = conectar_db()
    if conn:
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT c.id, c.nombre_paciente, c.carnet_paciente, c.fecha, TIME_FORMAT(c.hora, '%H:%i') AS hora, c.estado
            FROM citas c
            WHERE c.doctor_id = %s
            ORDER BY c.fecha ASC, c.hora ASC
        """
        cursor.execute(query, (doctor_id,))
        citas = cursor.fetchall()
        conn.close()
        return citas
    return []

def actualizar_estado_cita(cita_id, estado):
    conn = conectar_db()
    if conn:
        cursor = conn.cursor()
        query = "UPDATE citas SET estado = %s WHERE id = %s"
        try:
            cursor.execute(query, (estado, cita_id))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            conn.rollback()
            conn.close()
            print(f"Error al actualizar estado de cita: {e}")
            return False
    return False

def obtener_historial_paciente(carnet_paciente):
    conn = conectar_db()
    if conn:
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT c.fecha, TIME_FORMAT(c.hora, '%H:%i') AS hora, d.nombre AS doctor_nombre, d.especialidad, c.estado
            FROM citas c JOIN doctores d ON c.doctor_id = d.id
            WHERE c.carnet_paciente = %s
            ORDER BY c.fecha DESC, c.hora DESC
        """
        cursor.execute(query, (carnet_paciente,))
        historial = cursor.fetchall()
        conn.close()
        return historial
    return []

def listar_doctores():
    conn = conectar_db()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT nombre, especialidad FROM doctores")
        doctores = cursor.fetchall()
        conn.close()
        return doctores
    return None

def buscar_doctor_por_especialidad(especialidad):
    conn = conectar_db()
    if conn:
        cursor = conn.cursor(dictionary=True)
        query = "SELECT id, nombre FROM doctores WHERE especialidad LIKE %s LIMIT 1"
        cursor.execute(query, ('%' + especialidad + '%',))
        doctor = cursor.fetchone()
        conn.close()
        return doctor
    return None

def guardar_cita(nombre_paciente, carnet_paciente, doctor_id, fecha, hora):
    conn = conectar_db()
    if conn:
        cursor = conn.cursor()
        query = "INSERT INTO citas (nombre_paciente, carnet_paciente, doctor_id, fecha, hora, estado) VALUES (%s, %s, %s, %s, %s, 'pendiente')"
        try:
            cursor.execute(query, (nombre_paciente, carnet_paciente, doctor_id, fecha, hora))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            conn.rollback()
            conn.close()
            print(f"Error al guardar la cita: {e}")
            return False
    return False

def consultar_cita_por_carnet(carnet_paciente):
    conn = conectar_db()
    if conn:
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT c.fecha, TIME_FORMAT(c.hora, '%H:%i') AS hora, d.nombre AS doctor_nombre, d.especialidad
            FROM citas c JOIN doctores d ON c.doctor_id = d.id
            WHERE c.carnet_paciente = %s AND c.estado = 'pendiente'
            ORDER BY c.fecha ASC, c.hora ASC
            LIMIT 1
        """
        cursor.execute(query, (carnet_paciente,))
        cita = cursor.fetchone()
        conn.close()
        return cita
    return None

def buscar_doctores_por_especialidad(especialidad):
    conn = conectar_db()
    if conn:
        cursor = conn.cursor(dictionary=True)
        query = "SELECT nombre, especialidad FROM doctores WHERE especialidad LIKE %s"
        cursor.execute(query, ('%' + especialidad + '%',))
        doctores = cursor.fetchall()
        conn.close()
        return doctores
    return None

def buscar_citas_por_paciente(nombre_paciente):
    conn = conectar_db()
    if conn:
        cursor = conn.cursor(dictionary=True)
        query = "SELECT c.fecha, c.hora, d.nombre AS doctor_nombre, d.especialidad FROM citas c JOIN doctores d ON c.doctor_id = d.id WHERE c.nombre_paciente LIKE %s"
        cursor.execute(query, ('%' + nombre_paciente + '%',))
        citas = cursor.fetchall()
        conn.close()
        return citas
    return None

def actualizar_cita(carnet_paciente, nueva_fecha, nueva_hora, nuevo_doctor_id=None):
    conn = conectar_db()
    if conn:
        cursor = conn.cursor()
        query = "UPDATE citas SET fecha = %s, hora = %s"
        params = [nueva_fecha, nueva_hora]
        if nuevo_doctor_id:
            query += ", doctor_id = %s"
            params.append(nuevo_doctor_id)
        query += " WHERE carnet_paciente = %s AND estado = 'pendiente'"
        params.append(carnet_paciente)
        try:
            cursor.execute(query, params)
            conn.commit()
            conn.close()
            return cursor.rowcount
        except Exception as e:
            conn.rollback()
            conn.close()
            print(f"Error al actualizar la cita: {e}")
            return 0
    return 0

def eliminar_cita(carnet_paciente):
    conn = conectar_db()
    if conn:
        cursor = conn.cursor()
        query = "DELETE FROM citas WHERE carnet_paciente = %s AND estado = 'pendiente'"
        try:
            cursor.execute(query, (carnet_paciente,))
            conn.commit()
            conn.close()
            return cursor.rowcount
        except Exception as e:
            conn.rollback()
            conn.close()
            print(f"Error al eliminar la cita: {e}")
            return 0
    return 0

def buscar_citas_disponibles_por_dia_especialidad(fecha, especialidad):
    conn = conectar_db()
    if conn:
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT d.id, d.nombre AS doctor_nombre, d.horario_disponible
            FROM doctores d
            WHERE d.especialidad LIKE %s AND d.activo = 1
        """
        cursor.execute(query, ('%' + especialidad + '%',))
        doctores = cursor.fetchall()
        disponibles = []
        for doctor in doctores:
            import json
            horario = json.loads(doctor['horario_disponible'])
            dia_semana = fecha_to_dia_semana(fecha)
            if dia_semana in horario:
                horas = horario[dia_semana]
                for hora in horas:
                    cursor.execute(
                        "SELECT COUNT(*) as count FROM citas WHERE doctor_id = %s AND fecha = %s AND hora = %s",
                        (doctor['id'], fecha, hora)
                    )
                    if cursor.fetchone()['count'] == 0:
                        disponibles.append({
                            'doctor_nombre': doctor['doctor_nombre'],
                            'hora': hora
                        })
        conn.close()
        return disponibles
    return []

def fecha_to_dia_semana(fecha):
    from datetime import datetime
    dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    return dias[datetime.strptime(fecha, '%Y-%m-%d').weekday()]