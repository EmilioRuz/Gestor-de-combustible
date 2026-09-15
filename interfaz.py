import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date

from modelos import Vehiculo, Viaje
from gestor import GestorDatos

from repositorio import (
    obtener_vehiculos,
    insertar_vehiculo,
    actualizar_vehiculo,
    eliminar_vehiculo as eliminar_vehiculo_bd
)



class App:
    def cargar_vehiculos(self):
        try:
            registros = obtener_vehiculos()

            self.gestor.vehiculos.clear()

            for registro in registros:
                (
                    id_vehiculo,
                    nombre,
                    placa,
                    marca,
                    modelo,
                    rendimiento,
                    precio
                ) = registro

                vehiculo = Vehiculo(
                    id=id_vehiculo,
                    nombre=nombre,
                    placa=placa,
                    marca=marca,
                    modelo=modelo,
                    rendimiento=float(rendimiento),
                    precio=float(precio)
                )

                self.gestor.vehiculos.append(vehiculo)

            self.actualizar_vehiculos()
            self.actualizar_combo()

        except Exception as error:
            messagebox.showerror(
                "Error de base de datos",
                f"No se pudieron cargar los vehículos.\n\n{error}"
            )

    def __init__(self, root):
        self.root = root
        self.root.title("Gestión de vehículos y combustible")
        self.root.geometry("1100x700")

        self.gestor = GestorDatos()
        self.campos = {}
        self.editando = None
        self.editando_vehiculo = None

        self.crear_interfaz()
        self.cargar_vehiculos()

    def crear_interfaz(self):
        ttk.Label(
            self.root,
            text="Gestión de viajes y combustible",
            font=("Arial", 20, "bold")
        ).pack(pady=15)

        self.tabs = ttk.Notebook(self.root)
        self.tabs.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

        self.crear_tab_vehiculos()
        self.crear_tab_viajes()
        self.crear_tab_resumen()

    def crear_campo(
        self,
        padre,
        texto,
        nombre,
        fila,
        columna,
        combo=False
    ):
        ttk.Label(
            padre,
            text=texto
        ).grid(
            row=fila,
            column=columna * 2,
            padx=8,
            pady=7,
            sticky="e"
        )

        valor = str(date.today()) if nombre == "fecha" else ""
        valor = "40" if nombre == "rendimiento" else valor

        variable = tk.StringVar(value=valor)
        self.campos[nombre] = variable

        if combo:
            entrada = ttk.Combobox(
                padre,
                textvariable=variable,
                state="readonly",
                width=23
            )
        else:
            entrada = ttk.Entry(
                padre,
                textvariable=variable,
                width=25
            )

        entrada.grid(
            row=fila,
            column=columna * 2 + 1,
            padx=8,
            pady=7
        )

        return entrada

    def crear_tabla(self, padre, columnas):
        marco = ttk.LabelFrame(padre, text="Registros")
        marco.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

        tabla = ttk.Treeview(
            marco,
            columns=columnas,
            show="headings"
        )

        for columna in columnas:
            tabla.heading(columna, text=columna)
            tabla.column(
                columna,
                width=120,
                anchor="center"
            )

        scroll = ttk.Scrollbar(
            marco,
            orient="vertical",
            command=tabla.yview
        )

        tabla.configure(yscrollcommand=scroll.set)

        tabla.pack(
            side="left",
            fill="both",
            expand=True
        )

        scroll.pack(
            side="right",
            fill="y"
        )

        return tabla

    def llenar_tabla(self, tabla, datos):
        tabla.delete(*tabla.get_children())

        for indice, fila in enumerate(datos):
            tabla.insert(
                "",
                "end",
                iid=str(indice),
                values=fila
            )

    def crear_tab_vehiculos(self):
        tab = ttk.Frame(self.tabs)
        self.tabs.add(tab, text="Vehículos")

        formulario = ttk.LabelFrame(
            tab,
            text="Registrar vehículo"
        )

        formulario.pack(
            fill="x",
            padx=10,
            pady=10
        )

        campos = [
            ("Nombre:", "nombre"),
            ("Placa:", "placa"),
            ("Marca:", "marca"),
            ("Modelo:", "modelo"),
            ("Rendimiento km/l:", "rendimiento"),
            ("Precio litro:", "precio")
        ]

        for i, (texto, nombre) in enumerate(campos):
            self.crear_campo(
                formulario,
                texto,
                nombre,
                i // 2,
                i % 2
            )

        self.boton_vehiculo = ttk.Button(
            formulario,
            text="Registrar vehículo",
            command=self.registrar_vehiculo
        )

        self.boton_vehiculo.grid(
            row=3,
            column=3,
            padx=8,
            pady=8
        )

        self.tabla_vehiculos = self.crear_tabla(
            tab,
            (
                "Vehículo",
                "Placa",
                "Marca",
                "Modelo",
                "Rendimiento",
                "Precio"
            )
        )

        # Botones de acciones
        botones = ttk.Frame(tab)
        botones.pack(pady=8)

        ttk.Button(
            botones,
            text="Editar vehículo",
            command=self.editar_vehiculo
        ).grid(
            row=0,
            column=0,
            padx=5
        )

        ttk.Button(
            botones,
            text="Eliminar vehículo",
            command=self.eliminar_vehiculo
        ).grid(
            row=0,
            column=1,
            padx=5
        )

    def registrar_vehiculo(self):
        try:
            nombre = self.campos["nombre"].get().strip()
            placa = self.campos["placa"].get().strip()
            marca = self.campos["marca"].get().strip()
            modelo = self.campos["modelo"].get().strip()

            rendimiento = float(
                self.campos["rendimiento"].get()
            )

            precio = float(
                self.campos["precio"].get()
            )

            if not nombre:
                raise ValueError(
                    "Ingrese el nombre del vehículo."
                )

            if not placa:
                raise ValueError(
                    "Ingrese la placa del vehículo."
                )

            if rendimiento <= 0:
                raise ValueError(
                    "El rendimiento debe ser mayor que cero."
                )

            if precio <= 0:
                raise ValueError(
                    "El precio debe ser mayor que cero."
                )

            # ==================================
            # EDITAR
            # ==================================

            if self.editando_vehiculo is not None:

                print(
                    "EJECUTANDO UPDATE. ID:",
                    self.editando_vehiculo
                )

                actualizar_vehiculo(
                    self.editando_vehiculo,
                    nombre,
                    placa,
                    marca,
                    modelo,
                    rendimiento,
                    precio
                )

                # Actualizamos el objeto en memoria
                for vehiculo in self.gestor.vehiculos:

                    if vehiculo.id == self.editando_vehiculo:
                        vehiculo.nombre = nombre
                        vehiculo.placa = placa
                        vehiculo.marca = marca
                        vehiculo.modelo = modelo
                        vehiculo.rendimiento = rendimiento
                        vehiculo.precio = precio

                        break

                mensaje = "Vehículo actualizado correctamente."

            # ==================================
            # NUEVO
            # ==================================

            else:

                print("EJECUTANDO INSERT")

                id_vehiculo = insertar_vehiculo(
                    nombre,
                    placa,
                    marca,
                    modelo,
                    rendimiento,
                    precio
                )

                vehiculo = Vehiculo(
                    id=id_vehiculo,
                    nombre=nombre,
                    placa=placa,
                    marca=marca,
                    modelo=modelo,
                    rendimiento=rendimiento,
                    precio=precio
                )

                self.gestor.agregar_vehiculo(
                    vehiculo
                )

                mensaje = "Vehículo registrado correctamente."

        except ValueError as error:

            messagebox.showerror(
                "Error",
                str(error)
            )

            return

        except Exception as error:

            messagebox.showerror(
                "Error de base de datos",
                f"No se pudo guardar el vehículo.\n\n{error}"
            )

            return

        # ==================================
        # SALIR DEL MODO EDICIÓN
        # ==================================

        self.editando_vehiculo = None

        self.boton_vehiculo.config(
            text="Registrar vehículo"
        )

        self.actualizar_vehiculos()
        self.actualizar_combo()

        self.limpiar_vehiculo()

        messagebox.showinfo(
            "Resultado",
            mensaje
        )

    def eliminar_vehiculo(self):
        seleccion = self.tabla_vehiculos.selection()

        if not seleccion:
            messagebox.showwarning(
                "Aviso",
                "Seleccione un vehículo."
            )
            return

        indice = int(seleccion[0])
        vehiculo = self.gestor.vehiculos[indice]

        if not messagebox.askyesno(
                "Confirmar",
                f"¿Eliminar '{vehiculo.nombre}'?"
        ):
            return

        try:
            eliminar_vehiculo_bd(vehiculo.id)

            self.gestor.eliminar_vehiculo(
                vehiculo.nombre
            )

            self.actualizar_vehiculos()
            self.actualizar_combo()

            messagebox.showinfo(
                "Éxito",
                "Vehículo eliminado correctamente."
            )

        except ValueError as error:
            messagebox.showwarning(
                "Aviso",
                str(error)
            )

        except Exception as error:
            messagebox.showerror(
                "Error de base de datos",
                f"No se pudo eliminar el vehículo.\n\n{error}"
            )

    def editar_vehiculo(self):
        seleccion = self.tabla_vehiculos.selection()

        if not seleccion:
            messagebox.showwarning(
                "Aviso",
                "Seleccione un vehículo."
            )
            return

        indice = int(seleccion[0])

        vehiculo = self.gestor.vehiculos[indice]

        # Guardamos el ID real de SQL Server
        self.editando_vehiculo = vehiculo.id

        print(
            "EDITANDO VEHÍCULO ID:",
            self.editando_vehiculo
        )

        self.campos["nombre"].set(vehiculo.nombre)
        self.campos["placa"].set(vehiculo.placa)
        self.campos["marca"].set(vehiculo.marca)
        self.campos["modelo"].set(vehiculo.modelo)
        self.campos["rendimiento"].set(
            str(vehiculo.rendimiento)
        )
        self.campos["precio"].set(
            str(vehiculo.precio)
        )

        self.boton_vehiculo.config(
            text="Guardar cambios"
        )

    def actualizar_vehiculos(self):
        datos = [
            (
                vehiculo.nombre,
                vehiculo.placa,
                vehiculo.marca,
                vehiculo.modelo,
                f"{vehiculo.rendimiento:.2f}",
                f"${vehiculo.precio:.2f}"
            )
            for vehiculo in self.gestor.vehiculos
        ]

        self.llenar_tabla(
            self.tabla_vehiculos,
            datos
        )

    def actualizar_combo(self):
        nombres = [
            vehiculo.nombre
            for vehiculo in self.gestor.vehiculos
        ]

        self.combo_vehiculos["values"] = nombres

        if nombres:
            if self.campos["vehiculo"].get() not in nombres:
                self.combo_vehiculos.current(0)

            self.mostrar_vehiculo()
        else:
            self.campos["vehiculo"].set("")
            self.info_vehiculo.config(
                text="No hay vehículos registrados."
            )

    def limpiar_vehiculo(self):
        for nombre in (
                "nombre",
                "placa",
                "marca",
                "modelo",
                "precio"
        ):
            self.campos[nombre].set("")

        self.campos["rendimiento"].set("40")

    def crear_tab_viajes(self):
        tab = ttk.Frame(self.tabs)
        self.tabs.add(tab, text="Registrar viaje")

        formulario = ttk.LabelFrame(
            tab,
            text="Datos del viaje"
        )
        formulario.pack(
            fill="x",
            padx=10,
            pady=10
        )

        self.crear_campo(
            formulario,
            "Fecha:",
            "fecha",
            0,
            0
        )

        self.combo_vehiculos = self.crear_campo(
            formulario,
            "Vehículo:",
            "vehiculo",
            0,
            1,
            True
        )

        self.combo_vehiculos.bind(
            "<<ComboboxSelected>>",
            self.mostrar_vehiculo
        )

        campos = [
            ("Conductor:", "conductor"),
            ("Origen:", "origen"),
            ("Destino:", "destino"),
            ("Km inicial:", "km_inicial"),
            ("Km final:", "km_final"),
            ("Observaciones:", "observaciones")
        ]

        for i, (texto, nombre) in enumerate(campos):
            self.crear_campo(
                formulario,
                texto,
                nombre,
                (i + 2) // 2,
                (i + 2) % 2
            )

        self.info_vehiculo = ttk.Label(
            formulario,
            text="Seleccione un vehículo.",
            foreground="blue"
        )

        self.info_vehiculo.grid(
            row=4,
            column=0,
            columnspan=4,
            pady=8
        )

        self.boton_viaje = ttk.Button(
            formulario,
            text="Registrar viaje",
            command=self.guardar_viaje
        )

        self.boton_viaje.grid(
            row=5,
            column=3,
            pady=10
        )

        self.tabla_viajes = self.crear_tabla(
            tab,
            (
                "Fecha",
                "Vehículo",
                "Conductor",
                "Origen",
                "Destino",
                "Km",
                "Litros",
                "Gasto"
            )
        )

    def mostrar_vehiculo(self, evento=None):
        nombre = self.campos["vehiculo"].get()
        vehiculo = self.gestor.buscar_vehiculo(nombre)

        if vehiculo:
            self.info_vehiculo.config(
                text=(
                    f"{vehiculo.marca} {vehiculo.modelo} | "
                    f"{vehiculo.rendimiento:.2f} km/l | "
                    f"${vehiculo.precio:.2f}/l"
                )
            )

    def guardar_viaje(self):
        try:
            vehiculo = self.gestor.buscar_vehiculo(
                self.campos["vehiculo"].get()
            )

            if not vehiculo:
                raise ValueError(
                    "Seleccione un vehículo."
                )

            viaje = Viaje(
                fecha=self.campos["fecha"].get(),
                vehiculo=vehiculo,
                conductor=self.campos["conductor"].get(),
                origen=self.campos["origen"].get(),
                destino=self.campos["destino"].get(),
                km_inicial=float(
                    self.campos["km_inicial"].get()
                ),
                km_final=float(
                    self.campos["km_final"].get()
                ),
                observaciones=self.campos[
                    "observaciones"
                ].get()
            )

            if self.editando is None:
                self.gestor.agregar_viaje(viaje)
                mensaje = "Viaje registrado correctamente."
            else:
                self.gestor.modificar_viaje(
                    self.editando,
                    viaje
                )
                mensaje = "Viaje actualizado correctamente."

        except ValueError as error:
            messagebox.showerror("Error", str(error))
            return

        self.editando = None
        self.boton_viaje.config(
            text="Registrar viaje"
        )

        self.actualizar_viajes()
        self.actualizar_resumen()
        self.limpiar_viaje()

        messagebox.showinfo(
            "Resultado",
            (
                f"{mensaje}\n\n"
                f"Km: {viaje.km:.2f}\n"
                f"Litros: {viaje.litros:.2f}\n"
                f"Gasto: ${viaje.gasto:.2f}\n"
                f"Costo/km: ${viaje.costo_km:.2f}"
            )
        )

    def limpiar_viaje(self):
        for nombre in (
            "conductor",
            "origen",
            "destino",
            "km_inicial",
            "km_final",
            "observaciones"
        ):
            self.campos[nombre].set("")

        self.campos["fecha"].set(str(date.today()))
        self.editando = None
        self.boton_viaje.config(
            text="Registrar viaje"
        )

    def crear_tab_resumen(self):
        tab = ttk.Frame(self.tabs)
        self.tabs.add(tab, text="Resumen")

        marco = ttk.LabelFrame(
            tab,
            text="Resumen general"
        )
        marco.pack(
            fill="x",
            padx=10,
            pady=10
        )

        self.etiqueta_resumen = ttk.Label(
            marco,
            font=("Arial", 13),
            justify="left"
        )
        self.etiqueta_resumen.pack(
            padx=15,
            pady=15,
            anchor="w"
        )

        ttk.Button(
            marco,
            text="Actualizar",
            command=self.actualizar_resumen
        ).pack(pady=5)

        self.tabla_historial = self.crear_tabla(
            tab,
            (
                "Fecha",
                "Vehículo",
                "Conductor",
                "Origen",
                "Destino",
                "Km",
                "Litros",
                "Gasto"
            )
        )

        botones = ttk.Frame(tab)
        botones.pack(pady=8)

        ttk.Button(
            botones,
            text="Editar",
            command=self.editar_viaje
        ).grid(row=0, column=0, padx=5)

        ttk.Button(
            botones,
            text="Eliminar",
            command=self.eliminar_viaje
        ).grid(row=0, column=1, padx=5)

    def datos_viajes(self):
        return [
            (
                viaje.fecha,
                viaje.vehiculo.nombre,
                viaje.conductor,
                viaje.origen,
                viaje.destino,
                f"{viaje.km:.2f}",
                f"{viaje.litros:.2f}",
                f"${viaje.gasto:.2f}"
            )
            for viaje in self.gestor.viajes
        ]

    def actualizar_viajes(self):
        datos = self.datos_viajes()

        self.llenar_tabla(
            self.tabla_viajes,
            datos
        )

        self.llenar_tabla(
            self.tabla_historial,
            datos
        )

    def editar_viaje(self):
        seleccion = self.tabla_historial.selection()

        if not seleccion:
            messagebox.showwarning(
                "Aviso",
                "Seleccione un viaje."
            )
            return

        indice = int(seleccion[0])
        viaje = self.gestor.viajes[indice]

        self.editando = indice

        valores = {
            "fecha": viaje.fecha,
            "vehiculo": viaje.vehiculo.nombre,
            "conductor": viaje.conductor,
            "origen": viaje.origen,
            "destino": viaje.destino,
            "km_inicial": viaje.km_inicial,
            "km_final": viaje.km_final,
            "observaciones": viaje.observaciones
        }

        for nombre, valor in valores.items():
            self.campos[nombre].set(str(valor))

        self.mostrar_vehiculo()

        self.boton_viaje.config(
            text="Guardar cambios"
        )

        self.tabs.select(1)

    def eliminar_viaje(self):
        seleccion = self.tabla_historial.selection()

        if not seleccion:
            messagebox.showwarning(
                "Aviso",
                "Seleccione un viaje."
            )
            return

        indice = int(seleccion[0])

        if messagebox.askyesno(
            "Confirmar",
            "¿Eliminar el viaje seleccionado?"
        ):
            self.gestor.eliminar_viaje(indice)
            self.actualizar_viajes()
            self.actualizar_resumen()

    def actualizar_resumen(self):
        datos = self.gestor.resumen()

        self.etiqueta_resumen.config(
            text=(
                f"Vehículos: {len(self.gestor.vehiculos)}\n"
                f"Viajes: {len(self.gestor.viajes)}\n\n"
                f"Kilómetros: {datos['km']:.2f} km\n"
                f"Combustible: {datos['litros']:.2f} litros\n"
                f"Gasto total: ${datos['gasto']:.2f}\n"
                f"Rendimiento: {datos['rendimiento']:.2f} km/l\n"
                f"Costo por km: ${datos['costo_km']:.2f}"
            )
        )

        self.llenar_tabla(
            self.tabla_historial,
            self.datos_viajes()
        )
