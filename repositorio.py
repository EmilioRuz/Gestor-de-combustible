from database import obtener_conexion


def obtener_vehiculos():
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT
            id,
            nombre,
            placa,
            marca,
            modelo,
            rendimiento,
            precio
        FROM dbo.vehiculos
        ORDER BY id
    """)

    registros = cursor.fetchall()

    cursor.close()
    conexion.close()

    return registros


def insertar_vehiculo(
    nombre,
    placa,
    marca,
    modelo,
    rendimiento,
    precio
):
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("""
        INSERT INTO dbo.vehiculos
            (nombre, placa, marca, modelo, rendimiento, precio)
        OUTPUT INSERTED.id
        VALUES (?, ?, ?, ?, ?, ?)
    """,
    nombre,
    placa,
    marca,
    modelo,
    rendimiento,
    precio)

    id_vehiculo = cursor.fetchone()[0]

    conexion.commit()

    cursor.close()
    conexion.close()

    return id_vehiculo


def actualizar_vehiculo(
    id_vehiculo,
    nombre,
    placa,
    marca,
    modelo,
    rendimiento,
    precio
):
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("""
        UPDATE dbo.vehiculos
        SET
            nombre = ?,
            placa = ?,
            marca = ?,
            modelo = ?,
            rendimiento = ?,
            precio = ?
        WHERE id = ?
    """,
    nombre,
    placa,
    marca,
    modelo,
    rendimiento,
    precio,
    id_vehiculo)

    conexion.commit()

    cursor.close()
    conexion.close()


def eliminar_vehiculo(id_vehiculo):
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("""
        DELETE FROM dbo.vehiculos
        WHERE id = ?
    """, id_vehiculo)

    conexion.commit()

    cursor.close()
    conexion.close()
