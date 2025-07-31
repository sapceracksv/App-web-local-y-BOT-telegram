# gender_predictor.py
"""
COMENTARIO:
Este es un módulo de utilidad simple para inferir el género de una persona
basado en la terminación de su primer nombre. Es un método heurístico y
no siempre será preciso, pero sirve como un buen ejemplo.

Lógica:
- Nombres que terminan en 'a' se asumen como femeninos.
- Nombres que terminan en 'o' se asumen como masculinos.
- Cualquier otro caso se marca como 'desconocido'.
"""
import logging

# Configura un logger básico para este módulo.
logger = logging.getLogger(__name__)

def infer_gender(name: str) -> str:
    """
    Infiere el género basado en el primer nombre de una cadena de texto.

    Args:
        name: El nombre completo o el primer nombre de la persona.

    Returns:
        Una cadena: 'femenino', 'masculino' o 'desconocido'.
    """
    # Validación de entrada: asegura que el input sea una cadena.
    if not isinstance(name, str):
        logger.warning(f"Se recibió un valor que no es una cadena: {name!r}")
        return "desconocido"

    # Limpia el nombre (quita espacios, convierte a minúsculas) y toma la primera palabra.
    cleaned_name = name.strip().lower()
    if not cleaned_name:
        return "desconocido"
    
    first_name = cleaned_name.split()[0]

    # Aplica la lógica de inferencia basada en la última letra.
    if first_name.endswith("a"):
        return "femenino"
    if first_name.endswith("o"):
        return "masculino"
    
    return "desconocido"
