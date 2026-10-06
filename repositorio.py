"""
Repositorio: acceso a datos con SQL Server.
Usa el context manager conexion_db() para simplificar el manejo de conexiones.
"""
from database import conexion_db
from modelos import Vehiculo, Conductor, Viaje


# ── Zonas (desde Orgzone) ─────────────────────────────────────────────

def obtener_zonas():
    """Lee las zonas/rutas de la tabla Orgzone."""
    with conexion_db() as (conn, cursor):
        cursor.execute("""
            SELECT zoneid, zonename
            FROM dbo.Orgzone
            WHERE zonename IS NOT NULL AND zonename != ''
            ORDER BY zonename
        """)
        return [(r[0], r[1]) for r in cursor.fetchall()]


# ── Conductores ───────────────────────────────────────────────────────

def obtener_conductores():
    with conexion_db() as (conn, cursor):
        cursor.execute("""
            SELECT id, nombre, licencia, telefono, activo
            FROM dbo.conductores
            ORDER BY nombre
        """)
        return [
            Conductor(
                id=r[0], nombre=r[1], licencia=r[2],
                telefono=r[3] or "", activo=bool(r[4])
            )
            for r in cursor.fetchall()
        ]


def insertar_conductor(conductor):
    conductor.validar()
    with conexion_db() as (conn, cursor):
        cursor.execute("""
            INSERT INTO dbo.conductores (nombre, licencia, telefono)
            OUTPUT INSERTED.id
            VALUES (?, ?, ?)
        """, conductor.nombre, conductor.licencia, conductor.telefono)
        return cursor.fetchone()[0]


def actualizar_conductor(conductor):
    conductor.validar()
    with conexion_db() as (conn, cursor):
        cursor.execute("""
            UPDATE dbo.conductores
            SET nombre = ?, licencia = ?, telefono = ?
            WHERE id = ?
        """, conductor.nombre, conductor.licencia,
             conductor.telefono, conductor.id)


def eliminar_conductor(id_conductor):
    # Verificar que no tenga viajes asociados
    with conexion_db() as (conn, cursor):
        cursor.execute("""
            SELECT COUNT(*) FROM dbo.viajes WHERE conductor_id = ?
        """, id_conductor)
        count = cursor.fetchone()[0]
        if count > 0:
            raise ValueError(
                "No se puede eliminar un conductor con viajes registrados."
            )
        cursor.execute(
            "DELETE FROM dbo.conductores WHERE id = ?", id_conductor
        )


# ── Vehiculos ─────────────────────────────────────────────────────────

def obtener_vehiculos():
    with conexion_db() as (conn, cursor):
        cursor.execute("""
            SELECT id, nombre, placa, marca, modelo, rendimiento, precio
            FROM dbo.vehiculos
            ORDER BY nombre
        """)
        return [
            Vehiculo(
                id=r[0], nombre=r[1], placa=r[2], marca=r[3],
                modelo=r[4], rendimiento=float(r[5]), precio=float(r[6])
            )
            for r in cursor.fetchall()
        ]


def insertar_vehiculo(vehiculo):
    vehiculo.validar()
    with conexion_db() as (conn, cursor):
        cursor.execute("""
            INSERT INTO dbo.vehiculos
                (nombre, placa, marca, modelo, rendimiento, precio)
            OUTPUT INSERTED.id
            VALUES (?, ?, ?, ?, ?, ?)
        """, vehiculo.nombre, vehiculo.placa, vehiculo.marca,
             vehiculo.modelo, vehiculo.rendimiento, vehiculo.precio)
        return cursor.fetchone()[0]


def actualizar_vehiculo(vehiculo):
    vehiculo.validar()
    with conexion_db() as (conn, cursor):
        cursor.execute("""
            UPDATE dbo.vehiculos
            SET nombre=?, placa=?, marca=?, modelo=?, rendimiento=?, precio=?
            WHERE id = ?
        """, vehiculo.nombre, vehiculo.placa, vehiculo.marca,
             vehiculo.modelo, vehiculo.rendimiento, vehiculo.precio,
             vehiculo.id)


def eliminar_vehiculo(id_vehiculo):
    with conexion_db() as (conn, cursor):
        cursor.execute("""
            SELECT COUNT(*) FROM dbo.viajes WHERE vehiculo_id = ?
        """, id_vehiculo)
        count = cursor.fetchone()[0]
        if count > 0:
            raise ValueError(
                "No se puede eliminar un vehiculo con viajes registrados."
            )
        cursor.execute(
            "DELETE FROM dbo.vehiculos WHERE id = ?", id_vehiculo
        )


# ── Viajes ────────────────────────────────────────────────────────────

def obtener_viajes(vehiculos_dict):
    """
    Obtiene todos los viajes. Recibe un dict {id: Vehiculo}
    para reconstruir los objetos Viaje completos.
    """
    with conexion_db() as (conn, cursor):
        cursor.execute("""
            SELECT
                t.id, t.fecha, t.vehiculo_id, t.conductor_id,
                c.nombre AS conductor_nombre,
                t.origen, t.destino,
                t.km_inicial, t.km_final,
                t.zona_id, z.zonename,
                t.observaciones
            FROM dbo.viajes t
            LEFT JOIN dbo.conductores c ON c.id = t.conductor_id
            LEFT JOIN dbo.Orgzone z ON z.zoneid = t.zona_id
            ORDER BY t.fecha DESC, t.id DESC
        """)
        viajes = []
        for r in cursor.fetchall():
            vehiculo = vehiculos_dict.get(r[2])
            if vehiculo is None:
                continue
            viajes.append(Viaje(
                id=r[0], fecha=str(r[1]), vehiculo=vehiculo,
                conductor_id=r[3], conductor_nombre=r[4] or "Desconocido",
                origen=r[5], destino=r[6],
                km_inicial=float(r[7]), km_final=float(r[8]),
                zona_id=r[9], zona_nombre=r[10] or "",
                observaciones=r[11] or ""
            ))
        return viajes


def insertar_viaje(viaje):
    viaje.validar()
    with conexion_db() as (conn, cursor):
        cursor.execute("""
            INSERT INTO dbo.viajes
                (fecha, vehiculo_id, conductor_id, origen, destino,
                 km_inicial, km_final, zona_id, observaciones)
            OUTPUT INSERTED.id
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, viaje.fecha, viaje.vehiculo.id, viaje.conductor_id,
             viaje.origen, viaje.destino,
             viaje.km_inicial, viaje.km_final,
             viaje.zona_id, viaje.observaciones)
        return cursor.fetchone()[0]


def actualizar_viaje(viaje):
    viaje.validar()
    with conexion_db() as (conn, cursor):
        cursor.execute("""
            UPDATE dbo.viajes
            SET fecha=?, vehiculo_id=?, conductor_id=?, origen=?,
                destino=?, km_inicial=?, km_final=?,
                zona_id=?, observaciones=?
            WHERE id = ?
        """, viaje.fecha, viaje.vehiculo.id, viaje.conductor_id,
             viaje.origen, viaje.destino,
             viaje.km_inicial, viaje.km_final,
             viaje.zona_id, viaje.observaciones,
             viaje.id)


def eliminar_viaje(id_viaje):
    with conexion_db() as (conn, cursor):
        cursor.execute("DELETE FROM dbo.viajes WHERE id = ?", id_viaje)


# ── Reportes ──────────────────────────────────────────────────────────

def resumen_general():
    """Resumen con totales calculados en la base de datos."""
    with conexion_db() as (conn, cursor):
        cursor.execute("""
            SELECT
                COUNT(*) AS total_viajes,
                ISNULL(SUM(km_final - km_inicial), 0) AS total_km
            FROM dbo.viajes
        """)
        row = cursor.fetchone()
        return {
            "total_viajes": row[0],
            "total_km": float(row[1])
        }


def viajes_por_vehiculo():
    """Resumen agrupado por vehiculo."""
    with conexion_db() as (conn, cursor):
        cursor.execute("""
            SELECT
                v.nombre,
                COUNT(*) AS viajes,
                SUM(t.km_final - t.km_inicial) AS km,
                v.rendimiento,
                v.precio
            FROM dbo.viajes t
            JOIN dbo.vehiculos v ON v.id = t.vehiculo_id
            GROUP BY v.nombre, v.rendimiento, v.precio
            ORDER BY km DESC
        """)
        resultados = []
        for r in cursor.fetchall():
            km = float(r[2])
            rendimiento = float(r[3])
            precio = float(r[4])
            litros = km / rendimiento if rendimiento else 0
            resultados.append({
                "vehiculo": r[0],
                "viajes": r[1],
                "km": km,
                "litros": litros,
                "gasto": litros * precio
            })
        return resultados


def viajes_por_conductor():
    """Resumen agrupado por conductor."""
    with conexion_db() as (conn, cursor):
        cursor.execute("""
            SELECT
                c.nombre,
                COUNT(*) AS viajes,
                SUM(t.km_final - t.km_inicial) AS km
            FROM dbo.viajes t
            JOIN dbo.conductores c ON c.id = t.conductor_id
            GROUP BY c.nombre
            ORDER BY km DESC
        """)
        return [
            {"conductor": r[0], "viajes": r[1], "km": float(r[2])}
            for r in cursor.fetchall()
        ]