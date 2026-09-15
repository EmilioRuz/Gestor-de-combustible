from dataclasses import dataclass


@dataclass
class Vehiculo:
    nombre: str
    placa: str
    marca: str
    modelo: str
    cc: int
    rendimiento: float
    precio: float


@dataclass
class Viaje:
    fecha: str
    vehiculo: Vehiculo
    conductor: str
    origen: str
    destino: str
    km_inicial: float
    km_final: float
    observaciones: str = ""

    @property
    def km(self):
        return self.km_final - self.km_inicial

    @property
    def litros(self):
        return self.km / self.vehiculo.rendimiento

    @property
    def gasto(self):
        return self.litros * self.vehiculo.precio

    @property
    def costo_km(self):
        return self.gasto / self.km if self.km else 0
