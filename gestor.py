class GestorDatos:
    def __init__(self):
        self.vehiculos = []
        self.conductores = []
        self.viajes = []

    # ================= VEHÍCULOS =================

    def agregar_vehiculo(self, vehiculo):
        if any(
            x.nombre.lower() == vehiculo.nombre.lower()
            for x in self.vehiculos
        ):
            raise ValueError("Ese vehículo ya existe.")

        self.vehiculos.append(vehiculo)

    def eliminar_vehiculo(self, nombre):
        if any(
            viaje.vehiculo.nombre == nombre
            for viaje in self.viajes
        ):
            raise ValueError(
                "No se puede eliminar un vehículo con viajes registrados."
            )

        self.vehiculos = [
            vehiculo
            for vehiculo in self.vehiculos
            if vehiculo.nombre != nombre
        ]

    def buscar_vehiculo(self, nombre):
        return next(
            (
                vehiculo
                for vehiculo in self.vehiculos
                if vehiculo.nombre == nombre
            ),
            None
        )

    # ================= CONDUCTORES =================

    def agregar_conductor(self, conductor):
        if any(
            c.licencia.lower() == conductor.licencia.lower()
            for c in self.conductores
        ):
            raise ValueError("Esa licencia ya está registrada.")

        self.conductores.append(conductor)

    def eliminar_conductor(self, id_conductor):
        self.conductores = [
            conductor
            for conductor in self.conductores
            if conductor.id != id_conductor
        ]

    def buscar_conductor(self, nombre):
        return next(
            (
                conductor
                for conductor in self.conductores
                if conductor.nombre == nombre
            ),
            None
        )

    # ================= VIAJES =================

    def agregar_viaje(self, viaje):
        if viaje.km_final <= viaje.km_inicial:
            raise ValueError(
                "El km final debe ser mayor que el km inicial."
            )

        self.viajes.append(viaje)

    def modificar_viaje(self, indice, viaje):
        if viaje.km_final <= viaje.km_inicial:
            raise ValueError(
                "El km final debe ser mayor que el km inicial."
            )

        self.viajes[indice] = viaje

    def eliminar_viaje(self, indice):
        del self.viajes[indice]

    def resumen(self):
        km = sum(viaje.km for viaje in self.viajes)
        litros = sum(viaje.litros for viaje in self.viajes)
        gasto = sum(viaje.gasto for viaje in self.viajes)

        return {
            "km": km,
            "litros": litros,
            "gasto": gasto,
            "rendimiento": km / litros if litros else 0,
            "costo_km": gasto / km if km else 0
        }
