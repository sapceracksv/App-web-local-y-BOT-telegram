Proyecto de Búsqueda de Personas (Web y Telegram)



Esta es una aplicación completa que proporciona una interfaz web y un bot de Telegram para realizar búsquedas avanzadas en una base de datos de personas. El código está diseñado para ser genérico, seguro y fácilmente configurable para cualquier base de datos SQL Server.



Características:

Interfaz Web: Frontend moderno y responsivo para realizar búsquedas con múltiples filtros.
Bot de Telegram: Permite a usuarios autorizados realizar búsquedas directamente desde Telegram, con paginación de resultados.
Sistema de Autorización: El bot requiere que los usuarios sean aprobados por un administrador antes de poder usarlo.
Seguridad: No contiene credenciales ni datos sensibles en el código. Toda la configuración se maneja a través de variables de entorno.
Registro de Auditoría: Todas las búsquedas realizadas a través del bot se registran en una base de datos separada para mayor control.


Requisitos Previos:
Python 3.8+
SQL Server: Una instancia de base de datos accesible.
Git para clonar el repositorio.
Un Bot de Telegram creado desde BotFather.


Guía de Instalación:

1. Clonar el Repositorio:
 
git clone [https://github.com/sapceracksv/App-web-local-y-BOT-telegram.git](https://github.com/sapceracksv/App-web-local-y-BOT-telegram.git)
cd App-web-local-y-BOT-telegram


2. Organizar la Estructura de Carpetas
Para que la aplicación web funcione, los archivos deben estar en carpetas específicas. Asegúrate de que tu proyecto tenga la siguiente estructura:

tu-proyecto/
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── main.js
├── templates/
│   ├── base.html
│   └── index.html
├── app.py
├── bot.py
├── database.py
├── gender_predictor.py
├── requirements.txt
└── .env


Instrucciones:

Crea una carpeta llamada templates. Mueve los archivos index.html y base.html dentro de ella.
Crea una carpeta llamada static.
Dentro de static, crea dos carpetas más: css y js.
Mueve style.css a la carpeta css.
Mueve main.js a la carpeta js.


3. Crear un Entorno Virtual
Es una buena práctica aislar las dependencias del proyecto para evitar conflictos.

# Si se ejecuta en Windows
python3 -m venv venv
venv\Scripts\activate

# Si se ejecuta en macOS/Linux
python3 -m venv venv
source venv/bin/activate

4. Instalar las Dependencias
Crea un archivo llamado requirements.txt con el siguiente contenido:

flask
python-telegram-bot[ext]
pymssql
python-dotenv

Luego, instala todas las librerías con pip:

pip install -r requirements.txt

5. Configurar el Entorno (Paso más importante)

Busca el archivo .env en el repositorio.
Abre el archivo .env con un editor de texto y rellena todos los campos con tus propios datos (tu token del bot, tus credenciales de base de datos, la ruta a tus imágenes, etc.).


6. Adaptar el Código a tu Base de Datos
El sistema es flexible, pero necesitas decirle cómo es tu base de datos.

Abre el archivo database.py.

Sigue los comentarios ¡ATENCIÓN! PASO X: que te guiarán para:

Definir los nombres de tus tablas (TABLA_PERSONAS, TABLA_USUARIOS_BOT, etc.).

Ajustar el diccionario valid_columns para que las claves de la app coincidan con los nombres de tus columnas.

Modificar la consulta SELECT para que use los nombres de columna correctos de tu tabla. Puedes usar alias (AS) para mantener la compatibilidad con el resto del código.

7. Ejecutar la Aplicación
Necesitarás ejecutar la aplicación web y el bot de Telegram por separado, preferiblemente en dos terminales diferentes (asegúrate de que el entorno virtual esté activado en ambas).

Terminal 1: Iniciar el Servidor Web

python app.py

La interfaz web estará disponible en http://127.0.0.1:5000.

Terminal 2: Iniciar el Bot de Telegram

python bot.py

¡Y listo! Tu sistema de búsqueda debería estar completamente operativo y configurado para tu entorno específico.
