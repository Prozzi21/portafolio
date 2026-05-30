import asyncio
from database import (
    init_db, update_hero, create_project,
    create_skill, update_contact
)
from auth import hash_password
from config import USE_TURSO

async def seed():
    await init_db()

    await update_hero(
        name="Umberto Nieto",
        subtitle="Desarrollador Python especializado en aplicaciones de escritorio y videojuegos",
        description="Creo experiencias interactivas con Pygame y aplicaciones funcionales con Tkinter. Me apasiona transformar ideas en codigo limpio y eficiente."
    )

    projects = [
        ("Space Invaders", "Pygame",
         "Juego clasico de naves espaciales desarrollado con Pygame. Incluye niveles progresivos, sistema de puntuacion y efectos de sonido.",
         ["Niveles progresivos", "Sistema de puntuacion", "Efectos de sonido", "Sprites personalizados"], "🎮"),
        ("Plataformer 2D", "Pygame",
         "Videojuegos de plataformas sencillos, multiples niveles y un sistema de power ups.",
         ["Niveles progresivos", "Power-ups", "Plataformas variadas", "Controles simples"], "🎯"),
        ("App de Habitos", "Tkinter",
         "Permite registrar, eliminar y modificar habitos, mostrando las rachas de cada habito.",
         ["Registro de habitos", "Eliminar y modificar", "Seguimiento de rachas", "Estadisticas diarias"], "📊"),
        ("Contador de Palabras", "Tkinter",
         "Contador el cual permite contar letras, parrafos y palabras en tiempo real.",
         ["Conteo de letras", "Conteo de palabras", "Conteo de parrafos", "Actualizacion en tiempo real"], "🔤"),
    ]
    for p in projects:
        await create_project(*p)

    skills = [
        ("Python", 60, "🐍"),
        ("FastAPI", 85, "⚡"),
        ("Pygame", 40, "🎮"),
        ("Tkinter", 50, "🖥️"),
        ("Opencode", 60, "🤖"),
    ]
    for s in skills:
        await create_skill(*s)

    await update_contact(
        email="umberto.prozzi@gmail.com",
        github="prozzi21",
        linkedin=""
    )

    from database import _execute
    hashed = hash_password("admin123")
    await _execute("DELETE FROM users")
    await _execute(
        "INSERT INTO users (username, password_hash) VALUES (?, ?)",
        ("admin", hashed)
    )

    mode = "Turso" if USE_TURSO else "SQLite local"
    print(f"[OK] Base de datos inicializada con datos de ejemplo ({mode})")
    print("     Usuario: admin")
    print("     Contrasena: admin123")

if __name__ == "__main__":
    asyncio.run(seed())
