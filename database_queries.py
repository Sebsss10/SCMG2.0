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
        query = "INSERT INTO citas (nombre_paciente, carnet_paciente, doctor_id, fecha, hora) VALUES (%s, %s, %s, %s, %s)"
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
            WHERE c.carnet_paciente = %s
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
        query += " WHERE carnet_paciente = %s"
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
        query = "DELETE FROM citas WHERE carnet_paciente = %s"
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