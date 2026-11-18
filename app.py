from flask import (
    Flask, render_template, request, redirect,
    url_for, session, flash, send_file, abort
)
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from pathlib import Path
import os

from database import conectar, crear_tablas

app = Flask(__name__)
app.secret_key = os.environ.get(
    "SECRET_KEY", "clave-desarrollo-voces-espacio"
)

BASE_DIR = Path(__file__).resolve().parent
INDEX_FILE = BASE_DIR / "templates" / "index.html"

crear_tablas()


# CONTROL DE ACCESO
def requiere_login(funcion):
    @wraps(funcion)
    def decorada(*args, **kwargs):
        if "usuario_id" not in session:
            flash("Debes iniciar sesión.")
            return redirect(url_for("login"))
        return funcion(*args, **kwargs)
    return decorada


def requiere_admin(funcion):
    @wraps(funcion)
    def decorada(*args, **kwargs):
        if "usuario_id" not in session:
            flash("Debes iniciar sesión.")
            return redirect(url_for("login"))

        if session.get("rol") != "administrador":
            abort(403)

        return funcion(*args, **kwargs)
    return decorada


# PÁGINA ORIGINAL
@app.route("/")
def inicio():
    return send_file(INDEX_FILE, mimetype="text/html")


# REGISTRO
@app.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        correo = request.form.get("correo", "").strip().lower()
        password = request.form.get("password", "")

        if not nombre or not correo or len(password) < 8:
            flash("Completa los campos. La contraseña requiere 8 caracteres.")
            return render_template("registro.html")

        conexion = conectar()
        try:
            existe = conexion.execute(
                "SELECT id FROM usuarios WHERE correo = ?", (correo,)
            ).fetchone()

            if existe:
                flash("El correo ya está registrado.")
                return render_template("registro.html")

            conexion.execute("""
                INSERT INTO usuarios (nombre, correo, password_hash, rol)
                VALUES (?, ?, ?, 'visitante')
            """, (nombre, correo, generate_password_hash(password)))

            conexion.commit()
            flash("Cuenta creada correctamente.")
            return redirect(url_for("login"))
        finally:
            conexion.close()

    return render_template("registro.html")


# INICIO DE SESIÓN
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        correo = request.form.get("correo", "").strip().lower()
        password = request.form.get("password", "")

        conexion = conectar()
        try:
            usuario = conexion.execute(
                "SELECT * FROM usuarios WHERE correo = ?", (correo,)
            ).fetchone()
        finally:
            conexion.close()

        if usuario and check_password_hash(usuario["password_hash"], password):
            session.clear()
            session["usuario_id"] = usuario["id"]
            session["nombre"] = usuario["nombre"]
            session["rol"] = usuario["rol"]

            if usuario["rol"] == "administrador":
                return redirect(url_for("admin_historias"))

            return redirect(url_for("cuenta"))

        flash("Correo o contraseña incorrectos.")

    return render_template("login.html")


# CUENTA DEL USUARIO
@app.route("/cuenta")
@requiere_login
def cuenta():
    return render_template("cuenta.html")


# CERRAR SESIÓN
@app.route("/logout", methods=["POST"])
@requiere_login
def logout():
    session.clear()
    flash("Sesión cerrada correctamente.")
    return redirect(url_for("login"))


# PANEL ADMINISTRATIVO: CONSULTAR HISTORIAS
@app.route("/admin")
@requiere_admin
def admin_historias():
    conexion = conectar()
    try:
        historias = conexion.execute(
            "SELECT * FROM historias ORDER BY id DESC"
        ).fetchall()
    finally:
        conexion.close()

    return render_template("admin.html", historias=historias)


# CREAR HISTORIA
@app.route("/admin/crear", methods=["POST"])
@requiere_admin
def crear_historia():
    titulo = request.form.get("titulo", "").strip()
    explorador = request.form.get("explorador", "").strip()
    planeta = request.form.get("planeta", "").strip()
    resumen = request.form.get("resumen", "").strip()
    contenido = request.form.get("contenido", "").strip()
    idioma = request.form.get("idioma", "español").strip()
    audio_url = request.form.get("audio_url", "").strip()

    if not titulo or not explorador or not planeta or not contenido:
        flash("Completa los campos obligatorios.")
        return redirect(url_for("admin_historias"))

    conexion = conectar()
    try:
        conexion.execute("""
            INSERT INTO historias
            (titulo, explorador, planeta, resumen, contenido, idioma, audio_url)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (titulo, explorador, planeta, resumen, contenido, idioma, audio_url))
        conexion.commit()
        flash("Historia creada correctamente.")
    finally:
        conexion.close()

    return redirect(url_for("admin_historias"))


# EDITAR HISTORIA
@app.route("/admin/editar/<int:id>", methods=["GET", "POST"])
@requiere_admin
def editar_historia(id):
    conexion = conectar()

    try:
        historia = conexion.execute(
            "SELECT * FROM historias WHERE id = ?", (id,)
        ).fetchone()

        if historia is None:
            abort(404)

        if request.method == "POST":
            titulo = request.form.get("titulo", "").strip()
            explorador = request.form.get("explorador", "").strip()
            planeta = request.form.get("planeta", "").strip()
            resumen = request.form.get("resumen", "").strip()
            contenido = request.form.get("contenido", "").strip()
            idioma = request.form.get("idioma", "español").strip()
            audio_url = request.form.get("audio_url", "").strip()

            if not titulo or not explorador or not planeta or not contenido:
                flash("Completa los campos obligatorios.")
                return render_template("editar.html", historia=historia)

            conexion.execute("""
                UPDATE historias
                SET titulo=?, explorador=?, planeta=?, resumen=?,
                    contenido=?, idioma=?, audio_url=?
                WHERE id=?
            """, (
                titulo, explorador, planeta, resumen,
                contenido, idioma, audio_url, id
            ))
            conexion.commit()
            flash("Historia actualizada correctamente.")
            return redirect(url_for("admin_historias"))

    finally:
        conexion.close()

    return render_template("editar.html", historia=historia)


# ELIMINAR HISTORIA
@app.route("/admin/eliminar/<int:id>", methods=["POST"])
@requiere_admin
def eliminar_historia(id):
    conexion = conectar()
    try:
        conexion.execute(
            "DELETE FROM historias WHERE id = ?", (id,)
        )
        conexion.commit()
        flash("Historia eliminada.")
    finally:
        conexion.close()

    return redirect(url_for("admin_historias"))


if __name__ == "__main__":
    app.run(debug=True)