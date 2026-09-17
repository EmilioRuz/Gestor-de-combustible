from database import obtener_conexion


from database import obtener_conexion


def obtener_conductores():
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    try:
        cursor.execute("""
            SELECT
                id,
                nombre,
                licencia,
                telefono,
                activo
            FROM dbo.conductores
            ORDER BY nombre
        """)

        return cursor.fetchall()

    finally:
        cursor.close()
        conexion.close()


def insertar_conductor(nombre, licencia, telefono):
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    try:
        cursor.execute("""
            INSERT INTO dbo.conductores
                (nombre, licencia, telefono)
            OUTPUT INSERTED.id
            VALUES (?, ?, ?)
        """, nombre, licencia, telefono)

        id_conductor = cursor.fetchone()[0]
        conexion.commit()

        return id_conductor

    except Exception:
        conexion.rollback()
        raise

    finally:
        cursor.close()
        conexion.close()


def actualizar_conductor(id_conductor, nombre, licencia, telefono):
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    try:
        cursor.execute("""
            UPDATE dbo.conductores
            SET
                nombre = ?,
                licencia = ?,
                telefono = ?
            WHERE id = ?
        """, nombre, licencia, telefono, id_conductor)

        conexion.commit()

    except Exception:
        conexion.rollback()
        raise

    finally:
        cursor.close()
        conexion.close()


def eliminar_conductor(id_conductor):
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    try:
        cursor.execute("""
            DELETE FROM dbo.conductores
            WHERE id = ?
        """, id_conductor)

        conexion.commit()

    except Exception:
        conexion.rollback()
        raise

    finally:
        cursor.close()
        conexion.close()

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
