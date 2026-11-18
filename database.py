import sqlite3
from pathlib import Path

# Ubicación de la base de datos
BASE_DIR = Path(__file__).resolve().parent
DATABASE = BASE_DIR / "database" / "voces.db"


def conectar():
    DATABASE.parent.mkdir(parents=True, exist_ok=True)

    conexion = sqlite3.connect(DATABASE)
    conexion.row_factory = sqlite3.Row
    conexion.execute("PRAGMA foreign_keys = ON")

    return conexion


def crear_tablas():
    conexion = conectar()

    try:
        # Tabla de usuarios
        conexion.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                correo TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                rol TEXT NOT NULL DEFAULT 'visitante'
                    CHECK (rol IN ('administrador', 'visitante')),
                fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Tabla de historias espaciales
        conexion.execute("""
            CREATE TABLE IF NOT EXISTS historias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT NOT NULL,
                explorador TEXT NOT NULL,
                planeta TEXT NOT NULL,
                resumen TEXT,
                contenido TEXT NOT NULL,
                idioma TEXT NOT NULL DEFAULT 'español',
                audio_url TEXT,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conexion.commit()
        print("Base de datos creada correctamente.")
        print("Tablas: usuarios e historias.")

    finally:
        conexion.close()


if __name__ == "__main__":
    crear_tablas()