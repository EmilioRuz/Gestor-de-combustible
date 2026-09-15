from repositorio import insertar_vehiculo


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
