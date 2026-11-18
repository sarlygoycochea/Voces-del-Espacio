from database import conectar

correo = input("Correo de la cuenta que será administradora: ").strip().lower()

conexion = conectar()

try:
    usuario = conexion.execute(
        "SELECT id, nombre FROM usuarios WHERE correo = ?",
        (correo,)
    ).fetchone()

    if usuario:
        conexion.execute(
            "UPDATE usuarios SET rol = 'administrador' WHERE id = ?",
            (usuario["id"],)
        )
        conexion.commit()
        print("Administrador creado correctamente.")
        print("Cuenta:", usuario["nombre"])
    else:
        print("No existe esa cuenta. Primero debes registrarla.")

finally:
    conexion.close()