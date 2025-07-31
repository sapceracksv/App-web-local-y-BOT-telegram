# database.py
# Módulo para gestionar todas las interacciones con las bases de datos SQL Server.

import os
import pymssql
import logging
from contextlib import contextmanager
from dotenv import load_dotenv

# --- Configuración Inicial ---
load_dotenv()
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Conexión Segura desde .env ---
# Se leen todas las credenciales desde el archivo .env para no exponerlas en el código.
try:
    DB_MAIN_CONFIG = {
        'server': os.getenv("DB_SERVER"), 'user': os.getenv("DB_USER"),
        'password': os.getenv("DB_PASSWORD"), 'database': os.getenv("DB_NAME"),
        'port': int(os.getenv("DB_PORT", 1433))
    }
    DB_AUDIT_CONFIG = {
        'server': os.getenv("AUDIT_DB_SERVER"), 'user': os.getenv("AUDIT_DB_USER"),
        'password': os.getenv("AUDIT_DB_PASSWORD"), 'database': os.getenv("AUDIT_DB_NAME"),
        'port': int(os.getenv("AUDIT_DB_PORT", 1433))
    }
except (ValueError, TypeError) as e:
    logger.critical(f"Error en la configuración de base de datos en .env: {e}. Asegúrate de que los puertos sean números.")
    exit()

# Verificación para asegurar que las variables esenciales están definidas.
if not all(DB_MAIN_CONFIG.values()) or not all(DB_AUDIT_CONFIG.values()):
    logger.critical("Faltan credenciales para la base de datos en el archivo .env. Por favor, completa el archivo.")
    exit()

# --- Context Manager para Conexiones ---
@contextmanager
def get_db_connection(db_type: str = 'main'):
    """Gestiona las conexiones a la BD de forma segura, asegurando que se cierren siempre."""
    conn = None
    config = DB_AUDIT_CONFIG if db_type == 'audit' else DB_MAIN_CONFIG
    try:
        conn = pymssql.connect(**config, as_dict=True)
        yield conn
    except pymssql.Error as e:
        logger.error(f"Error de base de datos SQL Server (tipo: {db_type}): {e}")
        raise
    finally:
        if conn:
            conn.close()

# --- Búsqueda Principal ---
def search_in_db(**kwargs) -> list:
    """
    COMENTARIO PARA EL USUARIO:
    Esta es la función de búsqueda principal. ¡DEBES ADAPTARLA A TU BASE DE DATOS!
    """
    # ¡ATENCIÓN! PASO 1: Define aquí el nombre de TU tabla principal de personas.
    TABLA_PERSONAS = 'dbo.Tu_Tabla_Principal'

    with get_db_connection(db_type='main') as conn:
        # ¡ATENCIÓN! PASO 2: Mapea los argumentos de búsqueda a los NOMBRES REALES DE LAS COLUMNAS en tu tabla.
        # La 'clave' (ej: 'nombres') es lo que usa la app. El 'valor' (ej: 'ColumnaNombreCompleto') es el nombre de tu columna.
        valid_columns = {
            'nombres': 'ColumnaNombreCompleto', 'apellidos': 'ColumnaNombreCompleto',
            'dui': 'ColumnaDUI', 'telefono': 'ColumnaTelefono', 'correo': 'ColumnaCorreo',
            'direccion': 'ColumnaDireccion', 'placa': 'ColumnaPlacaVehiculo', 'nombre_empresa': 'ColumnaNombreEmpresa',
            'calle': 'ColumnaCalle', 'ciudad': 'ColumnaCiudad', 'sexo': 'ColumnaSexo', 
            'edad': 'ColumnaFechaNacimiento' # 'edad' usa la columna de fecha de nacimiento para calcular.
        }
        
        conditions, params = [], []
        for key, value in kwargs.items():
            if key in valid_columns and value:
                column_name = valid_columns[key]
                if key == 'edad':
                    try:
                        conditions.append(f"DATEDIFF(year, {column_name}, GETDATE()) = %s")
                        params.append(int(value))
                    except (ValueError, TypeError):
                        logger.warning(f"Valor de edad no numérico ignorado: {value}")
                elif key == 'sexo':
                    conditions.append(f"{column_name} = %s")
                    params.append(str(value).upper())
                else:
                    conditions.append(f"LOWER({column_name}) LIKE %s")
                    params.append(f"%{str(value).lower()}%")

        if not conditions:
            return []
            
        # ¡ATENCIÓN! PASO 3: Escribe tu consulta SELECT.
        # Asegúrate de que los nombres de las columnas aquí (ColumnaDUI, ColumnaNombreCompleto, etc.)
        # existan en tu tabla. Usa alias (AS) para mantener la compatibilidad con el resto del código.
        # Ejemplo: 'SELECT ColumnaDocumento AS Dui, ...'
        query = f"""
            SELECT
                ColumnaDUI AS Dui,
                ColumnaNombreCompleto AS NombreCompleto,
                ColumnaSexo AS Sexo,
                ColumnaProfesion AS Profesion,
                ColumnaTelefono AS Telefono,
                ColumnaCorreo AS Correo,
                ColumnaDireccion AS Direccion,
                ColumnaCalle AS Calle,
                ColumnaCiudad AS Ciudad,
                ColumnaNombrePadre AS NombrePadre,
                ColumnaNombreMadre AS NombreMadre,
                ColumnaNombreConyuge AS NombreConyugue,
                ColumnaPlacaVehiculo AS Placa,
                ColumnaMarcaVehiculo AS Marca,
                ColumnaModeloVehiculo AS Modelo,
                ColumnaAnioVehiculo AS Año,
                ColumnaNombreEmpresa AS NombreEmpresa,
                ColumnaSalario AS Salario,
                ColumnaDireccionLaboral AS DireccionEmpleadoISSS,
                DATEDIFF(year, ColumnaFechaNacimiento, GETDATE()) AS Edad
            FROM {TABLA_PERSONAS}
            WHERE {' AND '.join(conditions)}
            ORDER BY NombreCompleto ASC
        """
        
        cursor = conn.cursor()
        cursor.execute(query, tuple(params))
        return cursor.fetchall()

# --- Gestión de Usuarios y Logs ---
# ¡ATENCIÓN! PASO 4: Define los nombres para las tablas de control del bot.
TABLA_USUARIOS_BOT = 'dbo.BotAuthorizedUsers'
TABLA_LOGS_BOT = 'dbo.BotSearchLog'

def initialize_database():
    """Crea las tablas de control del bot si no existen."""
    try:
        with get_db_connection(db_type='main') as conn:
            cursor = conn.cursor()
            cursor.execute(f"""
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='{TABLA_USUARIOS_BOT.split('.')[-1]}' and xtype='U')
                CREATE TABLE {TABLA_USUARIOS_BOT} (ChatID BIGINT PRIMARY KEY, AddedBy BIGINT, AddedDate DATETIME DEFAULT GETDATE())
            """)
            conn.commit()
        with get_db_connection(db_type='audit') as conn:
            cursor = conn.cursor()
            cursor.execute(f"""
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='{TABLA_LOGS_BOT.split('.')[-1]}' and xtype='U')
                CREATE TABLE {TABLA_LOGS_BOT} (LogID INT PRIMARY KEY IDENTITY(1,1), ChatID BIGINT, Username NVARCHAR(255), SearchType NVARCHAR(50), SearchQuery NVARCHAR(MAX), ResultsFound INT, SearchTimestamp DATETIME DEFAULT GETDATE())
            """)
            conn.commit()
    except pymssql.Error as e:
        logger.error(f"Error al inicializar las tablas de control: {e}")

def get_authorized_users() -> set:
    """Obtiene los IDs de los usuarios autorizados para usar el bot."""
    with get_db_connection(db_type='main') as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT ChatID FROM {TABLA_USUARIOS_BOT}")
        return {row['ChatID'] for row in cursor}

def add_authorized_user(user_id, admin_id):
    """Añade un nuevo usuario a la tabla de autorizados."""
    try:
        with get_db_connection(db_type='main') as conn:
            cursor = conn.cursor()
            cursor.execute(f"INSERT INTO {TABLA_USUARIOS_BOT} (ChatID, AddedBy) VALUES (%s, %s)", (user_id, admin_id))
            conn.commit()
            return True
    except pymssql.IntegrityError:
        return False

def remove_authorized_user(user_id):
    """Elimina un usuario de la tabla de autorizados."""
    with get_db_connection(db_type='main') as conn:
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM {TABLA_USUARIOS_BOT} WHERE ChatID = %s", (user_id,))
        conn.commit()
        return cursor.rowcount > 0

def log_search(chat_id, username, search_type, search_query, results_found):
    """Registra una búsqueda en la tabla de logs."""
    with get_db_connection(db_type='audit') as conn:
        cursor = conn.cursor()
        cursor.execute(
            f"INSERT INTO {TABLA_LOGS_BOT} (ChatID, Username, SearchType, SearchQuery, ResultsFound) VALUES (%s, %s, %s, %s, %s)",
            (chat_id, username, search_type, search_query, results_found)
        )
        conn.commit()
