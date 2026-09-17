import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date

from modelos import Vehiculo, Conductor, Viaje
from gestor import GestorDatos

from repositorio import (
    obtener_vehiculos,
    insertar_vehiculo,
    actualizar_vehiculo,
    eliminar_vehiculo,
    obtener_conductores,
    insertar_conductor,
    actualizar_conductor,
    eliminar_conductor
)


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestión de vehículos y combustible")
        self.root.geometry("1150x750")

        self.gestor = GestorDatos()
        self.campos = {}

        self.editando = None
        self.editando_vehiculo = None
        self.editando_conductor = None

        self.interfaz()

        self.cargar_vehiculos()
        self.cargar_conductores()

    # =====================================================
    # ELEMENTOS GENERALES
    # =====================================================

    def interfaz(self):
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

        self.vehiculos_tab()
        self.conductores_tab()
        self.viajes_tab()
        self.resumen_tab()

    def campo(
        self,
        padre,
        nombre,
        texto,
        fila,
        col,
        combo=False
    ):
        ttk.Label(
            padre,
            text=texto
        ).grid(
            row=fila,
            column=col * 2,
            padx=5,
            pady=5,
            sticky="e"
        )

        if nombre == "fecha":
            valor = date.today().isoformat()
        elif nombre == "rendimiento":
            valor = "40"
        else:
            valor = ""

        self.campos[nombre] = tk.StringVar(value=valor)

        if combo:
            widget = ttk.Combobox(
                padre,
                textvariable=self.campos[nombre],
                state="readonly",
                width=22
            )
        else:
            widget = ttk.Entry(
                padre,
                textvariable=self.campos[nombre],
                width=24
            )

        widget.grid(
            row=fila,
            column=col * 2 + 1,
            padx=5,
            pady=5
        )

        return widget

    def tabla(self, padre, columnas):
        marco = ttk.LabelFrame(
            padre,
            text="Registros"
        )

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
            tabla.heading(
                columna,
                text=columna
            )

            tabla.column(
                columna,
                width=120,
                anchor="center"
            )

        tabla.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar = ttk.Scrollbar(
            marco,
            command=tabla.yview
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

        tabla.config(
            yscrollcommand=scrollbar.set
        )

        return tabla

    def llenar(self, tabla, datos):
        tabla.delete(*tabla.get_children())

        for i, dato in enumerate(datos):
            tabla.insert(
                "",
                "end",
                iid=i,
                values=dato
            )

    # =====================================================
    # VEHÍCULOS
    # =====================================================

    def vehiculos_tab(self):
        tab = ttk.Frame(self.tabs)
        self.tabs.add(tab, text="Vehículos")

        marco = ttk.LabelFrame(
            tab,
            text="Vehículo"
        )

        marco.pack(
            fill="x",
            padx=10,
            pady=10
        )

        nombres = [
            ("Nombre", "nombre"),
            ("Placa", "placa"),
            ("Marca", "marca"),
            ("Modelo", "modelo"),
            ("Rendimiento", "rendimiento"),
            ("Precio litro", "precio")
        ]

        for i, (texto, nombre) in enumerate(nombres):
            self.campo(
                marco,
                nombre,
                texto,
                i // 2,
                i % 2
            )

        self.btn_v = ttk.Button(
            marco,
            text="Registrar",
            command=self.guardar_vehiculo
        )

        self.btn_v.grid(
            row=3,
            column=3,
            padx=5,
            pady=5
        )

        self.tv = self.tabla(
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

        botones = ttk.Frame(tab)
        botones.pack(pady=5)

        ttk.Button(
            botones,
            text="Editar",
            command=self.editar_vehiculo
        ).pack(side="left", padx=5)

        ttk.Button(
            botones,
            text="Eliminar",
            command=self.eliminar_vehiculo
        ).pack(side="left", padx=5)

    def cargar_vehiculos(self):
        try:
            self.gestor.vehiculos.clear()

            for r in obtener_vehiculos():
                self.gestor.vehiculos.append(
                    Vehiculo(
                        id=r[0],
                        nombre=r[1],
                        placa=r[2],
                        marca=r[3],
                        modelo=r[4],
                        rendimiento=float(r[5]),
                        precio=float(r[6])
                    )
                )

            self.mostrar_vehiculos()
            self.actualizar_combo_vehiculos()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def datos_vehiculo(self):
        return (
            self.campos["nombre"].get().strip(),
            self.campos["placa"].get().strip(),
            self.campos["marca"].get().strip(),
            self.campos["modelo"].get().strip(),
            float(self.campos["rendimiento"].get()),
            float(self.campos["precio"].get())
        )

    def guardar_vehiculo(self):
        try:
            nombre, placa, marca, modelo, rendimiento, precio = (
                self.datos_vehiculo()
            )

            if not nombre or not placa:
                raise ValueError(
                    "Nombre y placa son obligatorios."
                )

            if rendimiento <= 0 or precio <= 0:
                raise ValueError(
                    "Rendimiento y precio deben ser mayores que cero."
                )

            if self.editando_vehiculo is None:
                id_vehiculo = insertar_vehiculo(
                    nombre,
                    placa,
                    marca,
                    modelo,
                    rendimiento,
                    precio
                )

                self.gestor.agregar_vehiculo(
                    Vehiculo(
                        id=id_vehiculo,
                        nombre=nombre,
                        placa=placa,
                        marca=marca,
                        modelo=modelo,
                        rendimiento=rendimiento,
                        precio=precio
                    )
                )

                mensaje = "Vehículo registrado."

            else:
                actualizar_vehiculo(
                    self.editando_vehiculo,
                    nombre,
                    placa,
                    marca,
                    modelo,
                    rendimiento,
                    precio
                )

                for vehiculo in self.gestor.vehiculos:
                    if vehiculo.id == self.editando_vehiculo:
                        vehiculo.nombre = nombre
                        vehiculo.placa = placa
                        vehiculo.marca = marca
                        vehiculo.modelo = modelo
                        vehiculo.rendimiento = rendimiento
                        vehiculo.precio = precio
                        break

                mensaje = "Vehículo actualizado."

            self.editando_vehiculo = None
            self.btn_v.config(text="Registrar")

            self.mostrar_vehiculos()
            self.actualizar_combo_vehiculos()
            self.limpiar_vehiculo()

            messagebox.showinfo("Correcto", mensaje)

        except ValueError as e:
            messagebox.showerror("Error", str(e))

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def editar_vehiculo(self):
        seleccion = self.tv.selection()

        if not seleccion:
            messagebox.showwarning(
                "Aviso",
                "Seleccione un vehículo."
            )
            return

        vehiculo = self.gestor.vehiculos[
            int(seleccion[0])
        ]

        self.editando_vehiculo = vehiculo.id

        self.campos["nombre"].set(vehiculo.nombre)
        self.campos["placa"].set(vehiculo.placa)
        self.campos["marca"].set(vehiculo.marca)
        self.campos["modelo"].set(vehiculo.modelo)
        self.campos["rendimiento"].set(vehiculo.rendimiento)
        self.campos["precio"].set(vehiculo.precio)

        self.btn_v.config(text="Guardar cambios")

    def eliminar_vehiculo(self):
        seleccion = self.tv.selection()

        if not seleccion:
            messagebox.showwarning(
                "Aviso",
                "Seleccione un vehículo."
            )
            return

        vehiculo = self.gestor.vehiculos[
            int(seleccion[0])
        ]

        if messagebox.askyesno(
            "Confirmar",
            f"¿Eliminar {vehiculo.nombre}?"
        ):
            try:
                eliminar_vehiculo(vehiculo.id)
                self.gestor.eliminar_vehiculo(vehiculo.nombre)

                self.mostrar_vehiculos()
                self.actualizar_combo_vehiculos()

            except Exception as e:
                messagebox.showerror("Error", str(e))

    def mostrar_vehiculos(self):
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

        self.llenar(self.tv, datos)

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

    def actualizar_combo_vehiculos(self):
        nombres = [
            vehiculo.nombre
            for vehiculo in self.gestor.vehiculos
        ]

        self.cveh["values"] = nombres

        if nombres:
            self.cveh.current(0)
            self.mostrar_info()

    # =====================================================
    # CONDUCTORES
    # =====================================================

    def conductores_tab(self):
        tab = ttk.Frame(self.tabs)
        self.tabs.add(tab, text="Conductores")

        marco = ttk.LabelFrame(
            tab,
            text="Conductor"
        )

        marco.pack(
            fill="x",
            padx=10,
            pady=10
        )

        self.campo(
            marco,
            "nombre_conductor",
            "Nombre",
            0,
            0
        )

        self.campo(
            marco,
            "licencia",
            "Licencia",
            0,
            1
        )

        self.campo(
            marco,
            "telefono",
            "Teléfono",
            1,
            0
        )

        self.btn_c = ttk.Button(
            marco,
            text="Registrar",
            command=self.guardar_conductor
        )

        self.btn_c.grid(
            row=1,
            column=3,
            padx=5,
            pady=5
        )

        self.tc = self.tabla(
            tab,
            (
                "Nombre",
                "Licencia",
                "Teléfono",
                "Estado"
            )
        )

        botones = ttk.Frame(tab)
        botones.pack(pady=5)

        ttk.Button(
            botones,
            text="Editar",
            command=self.editar_conductor
        ).pack(side="left", padx=5)

        ttk.Button(
            botones,
            text="Eliminar",
            command=self.eliminar_conductor
        ).pack(side="left", padx=5)

    def cargar_conductores(self):
        try:
            self.gestor.conductores.clear()

            for r in obtener_conductores():
                self.gestor.conductores.append(
                    Conductor(
                        id=r[0],
                        nombre=r[1],
                        licencia=r[2],
                        telefono=r[3] or "",
                        activo=bool(r[4])
                    )
                )

            self.mostrar_conductores()
            self.actualizar_combo_conductores()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def mostrar_conductores(self):
        datos = [
            (
                conductor.nombre,
                conductor.licencia,
                conductor.telefono,
                "Activo" if conductor.activo else "Inactivo"
            )
            for conductor in self.gestor.conductores
        ]

        self.llenar(self.tc, datos)

    def guardar_conductor(self):
        try:
            nombre = self.campos[
                "nombre_conductor"
            ].get().strip()

            licencia = self.campos[
                "licencia"
            ].get().strip()

            telefono = self.campos[
                "telefono"
            ].get().strip()

            if not nombre:
                raise ValueError(
                    "El nombre del conductor es obligatorio."
                )

            if not licencia:
                raise ValueError(
                    "La licencia es obligatoria."
                )

            if self.editando_conductor is None:
                id_conductor = insertar_conductor(
                    nombre,
                    licencia,
                    telefono
                )

                self.gestor.agregar_conductor(
                    Conductor(
                        id=id_conductor,
                        nombre=nombre,
                        licencia=licencia,
                        telefono=telefono
                    )
                )

                mensaje = "Conductor registrado."

            else:
                actualizar_conductor(
                    self.editando_conductor,
                    nombre,
                    licencia,
                    telefono
                )

                for conductor in self.gestor.conductores:
                    if conductor.id == self.editando_conductor:
                        conductor.nombre = nombre
                        conductor.licencia = licencia
                        conductor.telefono = telefono
                        break

                mensaje = "Conductor actualizado."

            self.editando_conductor = None
            self.btn_c.config(text="Registrar")

            self.mostrar_conductores()
            self.actualizar_combo_conductores()
            self.limpiar_conductor()

            messagebox.showinfo("Correcto", mensaje)

        except ValueError as e:
            messagebox.showerror("Error", str(e))

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def editar_conductor(self):
        seleccion = self.tc.selection()

        if not seleccion:
            messagebox.showwarning(
                "Aviso",
                "Seleccione un conductor."
            )
            return

        conductor = self.gestor.conductores[
            int(seleccion[0])
        ]

        self.editando_conductor = conductor.id

        self.campos["nombre_conductor"].set(
            conductor.nombre
        )

        self.campos["licencia"].set(
            conductor.licencia
        )

        self.campos["telefono"].set(
            conductor.telefono
        )

        self.btn_c.config(text="Guardar cambios")

    def eliminar_conductor(self):
        seleccion = self.tc.selection()

        if not seleccion:
            messagebox.showwarning(
                "Aviso",
                "Seleccione un conductor."
            )
            return

        conductor = self.gestor.conductores[
            int(seleccion[0])
        ]

        existe_en_viaje = any(
            viaje.conductor == conductor.nombre
            for viaje in self.gestor.viajes
        )

        if existe_en_viaje:
            messagebox.showerror(
                "Error",
                "No se puede eliminar un conductor "
                "con viajes registrados."
            )
            return

        confirmar = messagebox.askyesno(
            "Confirmar",
            f"¿Eliminar a {conductor.nombre}?"
        )

        if confirmar:
            try:
                eliminar_conductor(conductor.id)
                self.gestor.eliminar_conductor(conductor.id)

                self.mostrar_conductores()
                self.actualizar_combo_conductores()

            except Exception as e:
                messagebox.showerror("Error", str(e))

    def limpiar_conductor(self):
        self.campos["nombre_conductor"].set("")
        self.campos["licencia"].set("")
        self.campos["telefono"].set("")

    def actualizar_combo_conductores(self):
        nombres = [
            conductor.nombre
            for conductor in self.gestor.conductores
            if conductor.activo
        ]

        self.cconductor["values"] = nombres

        if nombres:
            self.cconductor.current(0)

    # =====================================================
    # VIAJES
    # =====================================================

    def viajes_tab(self):
        tab = ttk.Frame(self.tabs)
        self.tabs.add(tab, text="Registrar viaje")

        marco = ttk.LabelFrame(
            tab,
            text="Viaje"
        )

        marco.pack(
            fill="x",
            padx=10,
            pady=10
        )

        self.cveh = self.campo(
            marco,
            "vehiculo",
            "Vehículo",
            0,
            0,
            True
        )

        self.cveh.bind(
            "<<ComboboxSelected>>",
            self.mostrar_info
        )

        self.campo(
            marco,
            "fecha",
            "Fecha",
            0,
            1
        )

        self.cconductor = self.campo(
            marco,
            "conductor",
            "Conductor",
            1,
            0,
            True
        )

        self.campo(
            marco,
            "origen",
            "Origen",
            1,
            1
        )

        self.campo(
            marco,
            "destino",
            "Destino",
            2,
            0
        )

        self.campo(
            marco,
            "km_inicial",
            "Km inicial",
            2,
            1
        )

        self.campo(
            marco,
            "km_final",
            "Km final",
            3,
            0
        )

        self.campo(
            marco,
            "observaciones",
            "Observaciones",
            3,
            1
        )

        self.info = ttk.Label(
            marco,
            foreground="blue"
        )

        self.info.grid(
            row=4,
            column=0,
            columnspan=4
        )

        self.btn_t = ttk.Button(
            marco,
            text="Registrar",
            command=self.guardar_viaje
        )

        self.btn_t.grid(
            row=5,
            column=3,
            padx=5,
            pady=5
        )

        self.tt = self.tabla(
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

    def mostrar_info(self, event=None):
        vehiculo = self.gestor.buscar_vehiculo(
            self.cveh.get()
        )

        if vehiculo:
            self.info.config(
                text=(
                    f"{vehiculo.marca} {vehiculo.modelo} | "
                    f"{vehiculo.rendimiento:.2f} km/l | "
                    f"${vehiculo.precio:.2f}/l"
                )
            )

    def guardar_viaje(self):
        try:
            vehiculo = self.gestor.buscar_vehiculo(
                self.cveh.get()
            )

            if not vehiculo:
                raise ValueError(
                    "Seleccione un vehículo."
                )

            if not self.cconductor.get():
                raise ValueError(
                    "Seleccione un conductor."
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
                mensaje = "Viaje registrado."

            else:
                self.gestor.modificar_viaje(
                    self.editando,
                    viaje
                )
                mensaje = "Viaje actualizado."

            self.editando = None
            self.btn_t.config(text="Registrar")

            self.actualizar_viajes()
            self.actualizar_resumen()

            messagebox.showinfo(
                "Correcto",
                f"{mensaje}\n\n"
                f"Km: {viaje.km:.2f}\n"
                f"Litros: {viaje.litros:.2f}\n"
                f"Gasto: ${viaje.gasto:.2f}"
            )

        except ValueError as e:
            messagebox.showerror("Error", str(e))

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def actualizar_viajes(self):
        datos = [
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

        self.llenar(self.tt, datos)
        self.llenar(self.th, datos)

    # =====================================================
    # RESUMEN
    # =====================================================

    def resumen_tab(self):
        tab = ttk.Frame(self.tabs)
        self.tabs.add(tab, text="Resumen")

        self.resumen = ttk.Label(
            tab,
            font=("Arial", 13)
        )

        self.resumen.pack(pady=15)

        self.th = self.tabla(
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
        botones.pack(pady=5)

        ttk.Button(
            botones,
            text="Editar",
            command=self.editar_viaje
        ).pack(side="left", padx=5)

        ttk.Button(
            botones,
            text="Eliminar",
            command=self.eliminar_viaje
        ).pack(side="left", padx=5)

    def editar_viaje(self):
        seleccion = self.th.selection()

        if not seleccion:
            messagebox.showwarning(
                "Aviso",
                "Seleccione un viaje."
            )
            return

        indice = int(seleccion[0])
        viaje = self.gestor.viajes[indice]

        self.editando = indice

        self.campos["fecha"].set(viaje.fecha)
        self.campos["vehiculo"].set(
            viaje.vehiculo.nombre
        )
        self.campos["conductor"].set(
            viaje.conductor
        )
        self.campos["origen"].set(viaje.origen)
        self.campos["destino"].set(viaje.destino)
        self.campos["km_inicial"].set(
            viaje.km_inicial
        )
        self.campos["km_final"].set(
            viaje.km_final
        )
        self.campos["observaciones"].set(
            viaje.observaciones
        )

        self.mostrar_info()
        self.btn_t.config(text="Guardar cambios")
        self.tabs.select(2)

    def eliminar_viaje(self):
        seleccion = self.th.selection()

        if not seleccion:
            messagebox.showwarning(
                "Aviso",
                "Seleccione un viaje."
            )
            return

        if messagebox.askyesno(
            "Confirmar",
            "¿Eliminar viaje?"
        ):
            self.gestor.eliminar_viaje(
                int(seleccion[0])
            )

            self.actualizar_viajes()
            self.actualizar_resumen()

    def actualizar_resumen(self):
        resumen = self.gestor.resumen()

        self.resumen.config(
            text=(
                f"Vehículos: "
                f"{len(self.gestor.vehiculos)}   "
                f"Conductores: "
                f"{len(self.gestor.conductores)}   "
                f"Viajes: "
                f"{len(self.gestor.viajes)}\n"
                f"Km: {resumen['km']:.2f}   "
                f"Litros: {resumen['litros']:.2f}   "
                f"Gasto: ${resumen['gasto']:.2f}\n"
                f"Rendimiento: "
                f"{resumen['rendimiento']:.2f} km/l   "
                f"Costo/km: "
                f"${resumen['costo_km']:.2f}"
            )
        )
