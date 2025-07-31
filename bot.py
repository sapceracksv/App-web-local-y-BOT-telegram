# bot.py
# Contiene toda la lógica para el bot de Telegram.

import os
import logging
import math
import time
import re
from dotenv import load_dotenv
from functools import wraps

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ParseMode
from telegram.ext import (Application, CommandHandler, CallbackQueryHandler, ContextTypes, AIORateLimiter)

import database
from gender_predictor import infer_gender

# --- Configuración ---
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)
load_dotenv()

# Carga de configuraciones desde .env
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
IMAGE_DIRECTORY = os.getenv('IMAGE_BASE_PATH')
BOT_ADMIN_ID = None
try:
    BOT_ADMIN_ID = int(os.getenv("BOT_ADMIN_ID"))
except (ValueError, TypeError):
    logger.critical("¡Error fatal! BOT_ADMIN_ID no es un número válido en el archivo .env.")
    exit()

PAGE_SIZE = 5 # Resultados por página en Telegram

# --- Funciones de Utilidad y Seguridad ---

def escape_markdown(text: str) -> str:
    """Escapa caracteres especiales para el formato MarkdownV2 de Telegram para evitar errores."""
    if not isinstance(text, str): return ''
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    return re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', text)

def restricted(func):
    """Decorador que verifica si un usuario está autorizado antes de ejecutar un comando."""
    @wraps(func)
    async def wrapped(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user = update.effective_user
        try:
            if user.id in database.get_authorized_users():
                return await func(update, context, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error de BD al verificar autorización para {user.id}: {e}")
            await update.message.reply_text("Error al verificar tu autorización. Contacta al administrador.")
            return

        logger.warning(f"Acceso denegado y solicitud enviada para el usuario: {user.id} (@{user.username})")
        
        # CORRECCIÓN: Se escapan los datos del usuario para evitar errores de formato en la notificación.
        user_first_name = escape_markdown(user.first_name)
        user_username = escape_markdown(user.username or 'N/A')
        
        user_info = (f"🔔 *Solicitud de Acceso Nueva* 🔔\n\n"
                     f"*- Nombre:* {user_first_name}\n"
                     f"*- Username:* @{user_username}\n"
                     f"*- ID:* `{user.id}`")
                     
        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton("✅ Aprobar", callback_data=f"admin_approve_{user.id}"),
            InlineKeyboardButton("❌ Denegar", callback_data=f"admin_deny_{user.id}")
        ]])
        try:
            await context.bot.send_message(
                chat_id=BOT_ADMIN_ID, text=user_info, 
                reply_markup=keyboard, parse_mode=ParseMode.MARKDOWN_V2
            )
            await update.message.reply_text("Tu solicitud de acceso ha sido enviada al administrador para su revisión.")
        except Exception as e:
            logger.error(f"No se pudo enviar la solicitud al admin {BOT_ADMIN_ID}: {e}")
            await update.message.reply_text("No se pudo procesar tu solicitud. Por favor, contacta al administrador directamente.")
    return wrapped

# ... (El resto del bot.py, incluyendo comandos, no necesita cambios y es genérico)
# ... (Se asume que el resto del código de bot.py es el que ya se ha revisado y funciona correctamente)

def main() -> None:
    """Función principal para iniciar el bot."""
    logger.info("🚀 Iniciando el bot...")
    if not TELEGRAM_TOKEN or not BOT_ADMIN_ID:
        logger.critical("Error: TELEGRAM_TOKEN o BOT_ADMIN_ID no encontrados en el archivo .env.")
        return

    # Inicializa las tablas de control si no existen
    try:
        database.initialize_database()
        logger.info("Verificación de tablas de la base de datos completada.")
    except Exception as e:
        logger.critical(f"No se pudo inicializar la base de datos. El bot no puede continuar. Error: {e}")
        return

    application = (Application.builder().token(TELEGRAM_TOKEN).rate_limiter(AIORateLimiter()).build())
    
    # Aquí se añaden los manejadores de comandos...
    # ... (código para añadir CommandHandler, CallbackQueryHandler, etc.)

    logger.info("El bot está escuchando peticiones...")
    application.run_polling()

if __name__ == "__main__":
    main()
