"""
Modelos de datos del sistema.
"""
from dataclasses import dataclass, field
from datetime import date


@dataclass
class Vehiculo:
    id: int | None
    nombre: str
    placa: str
    marca: str
    modelo: str
    rendimiento: float
    precio: float

    def validar(self):
        if not self.nombre or not self.nombre.strip():
            raise ValueError("El nombre del vehiculo es obligatorio.")
        if not self.placa or not self.placa.strip():
            raise ValueError("La placa es obligatoria.")
        if self.rendimiento <= 0:
            raise ValueError("El rendimiento debe ser mayor que cero.")
        if self.precio <= 0:
            raise ValueError("El precio debe ser mayor que cero.")


@dataclass
class Conductor:
    id: int | None
    nombre: str
    licencia: str
    telefono: str = ""
    activo: bool = True

    def validar(self):
        if not self.nombre or not self.nombre.strip():
            raise ValueError("El nombre del conductor es obligatorio.")
        if not self.licencia or not self.licencia.strip():
            raise ValueError("La licencia es obligatoria.")


@dataclass
class Viaje:
    id: int | None
    fecha: str
    vehiculo: Vehiculo
    conductor_id: int
    conductor_nombre: str
    origen: str
    destino: str
    km_inicial: float
    km_final: float
    zona_id: int | None = None
    zona_nombre: str = ""
    observaciones: str = ""

    @property
    def km(self):
        return self.km_final - self.km_inicial

    @property
    def litros(self):
        return self.km / self.vehiculo.rendimiento if self.vehiculo.rendimiento else 0

    @property
    def gasto(self):
        return self.litros * self.vehiculo.precio

    @property
    def costo_km(self):
        return self.gasto / self.km if self.km else 0

    def validar(self):
        if self.km_final <= self.km_inicial:
            raise ValueError("El km final debe ser mayor que el km inicial.")
        if not self.fecha:
            raise ValueError("La fecha es obligatoria.")
        # Validar formato de fecha
        try:
            partes = self.fecha.split("-")
            if len(partes) != 3:
                raise ValueError()
            date(int(partes[0]), int(partes[1]), int(partes[2]))
        except (ValueError, IndexError):
            raise ValueError("Formato de fecha invalido. Use AAAA-MM-DD.")
        if not self.origen or not self.origen.strip():
            raise ValueError("El origen es obligatorio.")
        if not self.destino or not self.destino.strip():
            raise ValueError("El destino es obligatorio.")