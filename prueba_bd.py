from repositorio import (
    insertar_vehiculo,
    insertar_conductor
)


print("Insertando vehículo...")

id_vehiculo = insertar_vehiculo(
    "Vehículo prueba 2",
    "XYZ-456",
    "Ford",
    "Ranger",
    11.8,
    25.00
)

print("Vehículo insertado.")
print("ID generado:", id_vehiculo)


print()
print("Insertando conductor...")

id_conductor = insertar_conductor(
    "Juan Pérez",
    "LIC-001",
    "555-123456"
)

print("Conductor insertado.")
print("ID generado:", id_conductor)
