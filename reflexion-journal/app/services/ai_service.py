import os
from anthropic import Anthropic

MODEL = "claude-sonnet-4-6"


def _get_client():
    api_key = os.environ.get('ANTHROPIC_API_KEY', '')
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY no está configurada en el archivo .env")
    return Anthropic(api_key=api_key)


def generate_daily_ai_reflection(entry):
    """Genera una reflexión IA para una entrada diaria. Retorna texto."""
    client = _get_client()

    context = f"""
Estado de ánimo: {entry.user_mood}
Reflexión principal: {entry.reflection_text}
Interacciones: {entry.interactions or 'No especificado'}
Recuerdos/Flashbacks: {entry.flashbacks or 'No especificado'}
Emociones: {entry.emotions or 'No especificado'}
Conversaciones con seres queridos: {entry.friendship_talk or 'No especificado'}
Experimentos / cosas nuevas: {entry.experiments or 'No especificado'}
Eventos del día: {entry.events or 'No especificado'}
Notas rápidas: {entry.rapid_notes or 'No especificado'}
""".strip()

    message = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": (
                    "Eres un coach de vida y psicólogo compasivo. Analiza esta reflexión diaria "
                    "y proporciona una respuesta profunda, empática y útil en español.\n\n"
                    "Tu respuesta debe:\n"
                    "1. Reconocer y validar las emociones expresadas\n"
                    "2. Identificar patrones o temas importantes del día\n"
                    "3. Ofrecer una perspectiva reflexiva y constructiva\n"
                    "4. Hacer 1-2 preguntas que inviten a una mayor autoexploración\n"
                    "5. Ser cálida, personal y no genérica\n\n"
                    f"Reflexión del día:\n{context}\n\n"
                    "Responde en 3-4 párrafos en español, con un tono cercano y compasivo."
                )
            }
        ]
    )
    return message.content[0].text


def generate_final_ai_reflection(user, all_entries, day_zero_date, total_days):
    """Genera la reflexión final completa del journey. Retorna texto."""
    client = _get_client()

    entries_parts = []
    for entry in all_entries:
        day_num = (entry.created_at.date() - day_zero_date).days + 1
        text_preview = entry.reflection_text[:400]
        if len(entry.reflection_text) > 400:
            text_preview += "..."
        entries_parts.append(
            f"--- Día {day_num} ({entry.created_at.strftime('%d/%m/%Y')}) ---\n"
            f"Ánimo: {entry.user_mood}\n"
            f"Reflexión: {text_preview}\n"
            f"Emociones: {entry.emotions or 'N/D'}\n"
            f"Experimentos: {entry.experiments or 'N/D'}\n"
            f"Eventos: {entry.events or 'N/D'}\n"
        )

    total_reflections = len(all_entries)
    completion_rate = int((total_reflections / total_days) * 100) if total_days > 0 else 0
    entries_text = "\n".join(entries_parts)

    message = client.messages.create(
        model=MODEL,
        max_tokens=4096,
        messages=[
            {
                "role": "user",
                "content": (
                    f"Eres un coach de vida y psicólogo especializado en análisis de diarios personales.\n\n"
                    f"{user.first_name} {user.last_name} ha completado su journey de reflexión de {total_days} días. "
                    f"Escribió {total_reflections} reflexiones ({completion_rate}% de completitud).\n\n"
                    f"Analiza TODAS sus reflexiones y genera una REFLEXIÓN FINAL PROFUNDA Y DETALLADA en español que incluya:\n\n"
                    f"1. **Resumen del Journey**: Visión general de cómo fue la experiencia\n"
                    f"2. **Evolución Emocional**: Cómo evolucionaron sus emociones a lo largo del tiempo\n"
                    f"3. **Patrones y Temas Recurrentes**: Temas, preocupaciones o alegrías que aparecieron repetidamente\n"
                    f"4. **Logros y Crecimiento**: Experimentos, aprendizajes y crecimiento personal\n"
                    f"5. **Momentos Clave**: Los días o momentos que parecen más significativos\n"
                    f"6. **Insights Profundos**: Observaciones sobre su carácter, fortalezas y áreas de crecimiento\n"
                    f"7. **Carta Personal**: Carta emotiva dirigida a {user.first_name} celebrando su journey\n"
                    f"8. **Próximos Pasos**: Recomendaciones personalizadas para continuar creciendo\n\n"
                    f"Reflexiones del journey:\n{entries_text}\n\n"
                    f"Genera una reflexión PROFUNDA, DETALLADA y PERSONAL. "
                    f"Usa detalles reales de sus reflexiones. Habla directamente a {user.first_name} en segunda persona."
                )
            }
        ]
    )
    return message.content[0].text
