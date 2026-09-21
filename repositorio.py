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

    try:
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

        return cursor.fetchall()

    finally:
        cursor.close()
        conexion.close()


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

    try:
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

        return id_vehiculo

    except Exception:
        conexion.rollback()
        raise

    finally:
        cursor.close()
        conexion.close()


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

    try:
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

    except Exception:
        conexion.rollback()
        raise

    finally:
        cursor.close()
        conexion.close()


def eliminar_vehiculo(id_vehiculo):
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    try:
        cursor.execute("""
            DELETE FROM dbo.vehiculos
            WHERE id = ?
        """, id_vehiculo)

        conexion.commit()

    except Exception:
        conexion.rollback()
        raise

    finally:
        cursor.close()
        conexion.close()


# --- Viajes -----------------------------------------------------------
# NOTA: estas funciones NO se usan por ahora (la app guarda los viajes
# solo en memoria, como en la versión original) porque requieren crear
# la tabla dbo.viajes y no hay permisos para modificar la base de datos.
# Quedan listas para cuando se pueda hacer ese cambio: ver
# migracion_viajes.sql para la tabla que necesitarían.

def obtener_viajes():
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    try:
        cursor.execute("""
            SELECT
                t.id,
                t.fecha,
                t.conductor,
                t.origen,
                t.destino,
                t.km_inicial,
                t.km_final,
                t.observaciones,
                v.id,
                v.nombre,
                v.placa,
                v.marca,
                v.modelo,
                v.rendimiento,
                v.precio
            FROM dbo.viajes t
            JOIN dbo.vehiculos v ON v.id = t.vehiculo_id
            ORDER BY t.fecha, t.id
        """)

        return cursor.fetchall()

    finally:
        cursor.close()
        conexion.close()


def insertar_viaje(
    fecha,
    vehiculo_id,
    conductor,
    origen,
    destino,
    km_inicial,
    km_final,
    observaciones
):
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    try:
        cursor.execute("""
            INSERT INTO dbo.viajes
                (fecha, vehiculo_id, conductor, origen, destino,
                 km_inicial, km_final, observaciones)
            OUTPUT INSERTED.id
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        fecha,
        vehiculo_id,
        conductor,
        origen,
        destino,
        km_inicial,
        km_final,
        observaciones)

        id_viaje = cursor.fetchone()[0]
        conexion.commit()

        return id_viaje

    except Exception:
        conexion.rollback()
        raise

    finally:
        cursor.close()
        conexion.close()


def actualizar_viaje(
    id_viaje,
    fecha,
    vehiculo_id,
    conductor,
    origen,
    destino,
    km_inicial,
    km_final,
    observaciones
):
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    try:
        cursor.execute("""
            UPDATE dbo.viajes
            SET
                fecha = ?,
                vehiculo_id = ?,
                conductor = ?,
                origen = ?,
                destino = ?,
                km_inicial = ?,
                km_final = ?,
                observaciones = ?
            WHERE id = ?
        """,
        fecha,
        vehiculo_id,
        conductor,
        origen,
        destino,
        km_inicial,
        km_final,
        observaciones,
        id_viaje)

        conexion.commit()

    except Exception:
        conexion.rollback()
        raise

    finally:
        cursor.close()
        conexion.close()


def eliminar_viaje(id_viaje):
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    try:
        cursor.execute("""
            DELETE FROM dbo.viajes
            WHERE id = ?
        """, id_viaje)

        conexion.commit()

    except Exception:
        conexion.rollback()
        raise

    finally:
        cursor.close()
        conexion.close()