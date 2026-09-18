import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date

from modelos import Vehiculo, Conductor, Viaje
from gestor import GestorDatos
from repositorio import *


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestión de vehículos y combustible")
        self.root.geometry("1150x750")

        self.gestor = GestorDatos()
        self.campos = {}
        self.editando = self.editando_vehiculo = self.editando_conductor = None

        self.interfaz()
        self.cargar_vehiculos()
        self.cargar_conductores()

    # ==================== GENERAL ====================

    def interfaz(self):
        ttk.Label(
            self.root, text="Gestión de viajes y combustible",
            font=("Arial", 20, "bold")
        ).pack(pady=15)

        self.tabs = ttk.Notebook(self.root)
        self.tabs.pack(fill="both", expand=True, padx=10, pady=10)

        self.vehiculos_tab()
        self.conductores_tab()
        self.viajes_tab()
        self.resumen_tab()

    def campo(self, padre, nombre, texto, fila, col, combo=False):
        ttk.Label(padre, text=texto).grid(
            row=fila, column=col * 2, padx=5, pady=5, sticky="e"
        )

        valor = (
            date.today().isoformat() if nombre == "fecha"
            else "40" if nombre == "rendimiento"
            else ""
        )

        self.campos[nombre] = tk.StringVar(value=valor)

        widget = (
            ttk.Combobox(
                padre, textvariable=self.campos[nombre],
                state="readonly", width=22
            )
            if combo else
            ttk.Entry(
                padre, textvariable=self.campos[nombre],
                width=24
            )
        )

        widget.grid(row=fila, column=col * 2 + 1, padx=5, pady=5)
        return widget

    def tabla(self, padre, columnas):
        marco = ttk.LabelFrame(padre, text="Registros")
        marco.pack(fill="both", expand=True, padx=10, pady=10)

        tabla = ttk.Treeview(marco, columns=columnas, show="headings")

        for c in columnas:
            tabla.heading(c, text=c)
            tabla.column(c, width=120, anchor="center")

        tabla.pack(side="left", fill="both", expand=True)

        scroll = ttk.Scrollbar(marco, command=tabla.yview)
        scroll.pack(side="right", fill="y")
        tabla.config(yscrollcommand=scroll.set)

        return tabla

    def llenar(self, tabla, datos):
        tabla.delete(*tabla.get_children())
        for i, dato in enumerate(datos):
            tabla.insert("", "end", iid=i, values=dato)

    def botones(self, padre, editar, eliminar):
        frame = ttk.Frame(padre)
        frame.pack(pady=5)

        ttk.Button(frame, text="Editar", command=editar).pack(
            side="left", padx=5
        )
        ttk.Button(frame, text="Eliminar", command=eliminar).pack(
            side="left", padx=5
        )

    # ==================== VEHÍCULOS ====================

    def vehiculos_tab(self):
        tab = ttk.Frame(self.tabs)
        self.tabs.add(tab, text="Vehículos")

        marco = ttk.LabelFrame(tab, text="Vehículo")
        marco.pack(fill="x", padx=10, pady=10)

        campos = [
            ("Nombre", "nombre"), ("Placa", "placa"),
            ("Marca", "marca"), ("Modelo", "modelo"),
            ("Rendimiento", "rendimiento"), ("Precio litro", "precio")
        ]

        for i, (texto, nombre) in enumerate(campos):
            self.campo(marco, nombre, texto, i // 2, i % 2)

        self.btn_v = ttk.Button(
            marco, text="Registrar", command=self.guardar_vehiculo
        )
        self.btn_v.grid(row=3, column=3, padx=5, pady=5)

        self.tv = self.tabla(
            tab,
            ("Vehículo", "Placa", "Marca", "Modelo", "Rendimiento", "Precio")
        )

        self.botones(tab, self.editar_vehiculo, self.eliminar_vehiculo)

    def cargar_vehiculos(self):
        try:
            self.gestor.vehiculos.clear()

            for r in obtener_vehiculos():
                self.gestor.vehiculos.append(
                    Vehiculo(
                        id=r[0], nombre=r[1], placa=r[2],
                        marca=r[3], modelo=r[4],
                        rendimiento=float(r[5]), precio=float(r[6])
                    )
                )

            self.mostrar_vehiculos()
            self.actualizar_combo_vehiculos()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def guardar_vehiculo(self):
        try:
            datos = (
                self.campos["nombre"].get().strip(),
                self.campos["placa"].get().strip(),
                self.campos["marca"].get().strip(),
                self.campos["modelo"].get().strip(),
                float(self.campos["rendimiento"].get()),
                float(self.campos["precio"].get())
            )

            nombre, placa, marca, modelo, rendimiento, precio = datos

            if not nombre or not placa:
                raise ValueError("Nombre y placa son obligatorios.")

            if rendimiento <= 0 or precio <= 0:
                raise ValueError("Rendimiento y precio deben ser mayores que cero.")

            if self.editando_vehiculo is None:
                id_ = insertar_vehiculo(*datos)

                self.gestor.agregar_vehiculo(
                    Vehiculo(id_, nombre, placa, marca, modelo, rendimiento, precio)
                )

                mensaje = "Vehículo registrado."
            else:
                actualizar_vehiculo(self.editando_vehiculo, *datos)

                v = next(
                    v for v in self.gestor.vehiculos
                    if v.id == self.editando_vehiculo
                )

                v.nombre, v.placa, v.marca, v.modelo, v.rendimiento, v.precio = datos
                mensaje = "Vehículo actualizado."

            self.editando_vehiculo = None
            self.btn_v.config(text="Registrar")
            self.mostrar_vehiculos()
            self.actualizar_combo_vehiculos()
            self.limpiar_vehiculo()

            messagebox.showinfo("Correcto", mensaje)

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def editar_vehiculo(self):
        sel = self.tv.selection()

        if not sel:
            messagebox.showwarning("Aviso", "Seleccione un vehículo.")
            return

        v = self.gestor.vehiculos[int(sel[0])]
        self.editando_vehiculo = v.id

        for campo, valor in {
            "nombre": v.nombre, "placa": v.placa,
            "marca": v.marca, "modelo": v.modelo,
            "rendimiento": v.rendimiento, "precio": v.precio
        }.items():
            self.campos[campo].set(valor)

        self.btn_v.config(text="Guardar cambios")

    def eliminar_vehiculo(self):
        sel = self.tv.selection()

        if not sel:
            messagebox.showwarning("Aviso", "Seleccione un vehículo.")
            return

        v = self.gestor.vehiculos[int(sel[0])]

        if messagebox.askyesno("Confirmar", f"¿Eliminar {v.nombre}?"):
            try:
                eliminar_vehiculo(v.id)
                self.gestor.eliminar_vehiculo(v.nombre)
                self.mostrar_vehiculos()
                self.actualizar_combo_vehiculos()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def mostrar_vehiculos(self):
        self.llenar(self.tv, [
            (
                v.nombre, v.placa, v.marca, v.modelo,
                f"{v.rendimiento:.2f}", f"${v.precio:.2f}"
            )
            for v in self.gestor.vehiculos
        ])

    def limpiar_vehiculo(self):
        for x in ("nombre", "placa", "marca", "modelo", "precio"):
            self.campos[x].set("")
        self.campos["rendimiento"].set("40")

    def actualizar_combo_vehiculos(self):
        nombres = [v.nombre for v in self.gestor.vehiculos]
        self.cveh["values"] = nombres

        if nombres:
            self.cveh.current(0)
            self.mostrar_info()

    # ==================== CONDUCTORES ====================

    def conductores_tab(self):
        tab = ttk.Frame(self.tabs)
        self.tabs.add(tab, text="Conductores")

        marco = ttk.LabelFrame(tab, text="Conductor")
        marco.pack(fill="x", padx=10, pady=10)

        self.campo(marco, "nombre_conductor", "Nombre", 0, 0)
        self.campo(marco, "licencia", "Licencia", 0, 1)
        self.campo(marco, "telefono", "Teléfono", 1, 0)

        self.btn_c = ttk.Button(
            marco, text="Registrar", command=self.guardar_conductor
        )
        self.btn_c.grid(row=1, column=3, padx=5, pady=5)

        self.tc = self.tabla(
            tab, ("Nombre", "Licencia", "Teléfono", "Estado")
        )

        self.botones(tab, self.editar_conductor, self.eliminar_conductor)

    def cargar_conductores(self):
        try:
            self.gestor.conductores.clear()

            for r in obtener_conductores():
                self.gestor.conductores.append(
                    Conductor(
                        id=r[0], nombre=r[1],
                        licencia=r[2], telefono=r[3] or "",
                        activo=bool(r[4])
                    )
                )

            self.mostrar_conductores()
            self.actualizar_combo_conductores()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def mostrar_conductores(self):
        self.llenar(self.tc, [
            (
                c.nombre, c.licencia, c.telefono,
                "Activo" if c.activo else "Inactivo"
            )
            for c in self.gestor.conductores
        ])

    def guardar_conductor(self):
        try:
            datos = (
                self.campos["nombre_conductor"].get().strip(),
                self.campos["licencia"].get().strip(),
                self.campos["telefono"].get().strip()
            )

            if not datos[0]:
                raise ValueError("El nombre del conductor es obligatorio.")

            if not datos[1]:
                raise ValueError("La licencia es obligatoria.")

            if self.editando_conductor is None:
                id_ = insertar_conductor(*datos)
                self.gestor.agregar_conductor(
                    Conductor(id=id_, nombre=datos[0],
                              licencia=datos[1], telefono=datos[2])
                )
                mensaje = "Conductor registrado."
            else:
                actualizar_conductor(self.editando_conductor, *datos)

                c = next(
                    c for c in self.gestor.conductores
                    if c.id == self.editando_conductor
                )

                c.nombre, c.licencia, c.telefono = datos
                mensaje = "Conductor actualizado."

            self.editando_conductor = None
            self.btn_c.config(text="Registrar")
            self.mostrar_conductores()
            self.actualizar_combo_conductores()
            self.limpiar_conductor()

            messagebox.showinfo("Correcto", mensaje)

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def editar_conductor(self):
        sel = self.tc.selection()

        if not sel:
            messagebox.showwarning("Aviso", "Seleccione un conductor.")
            return

        c = self.gestor.conductores[int(sel[0])]
        self.editando_conductor = c.id

        for campo, valor in {
            "nombre_conductor": c.nombre,
            "licencia": c.licencia,
            "telefono": c.telefono
        }.items():
            self.campos[campo].set(valor)

        self.btn_c.config(text="Guardar cambios")

    def eliminar_conductor(self):
        sel = self.tc.selection()

        if not sel:
            messagebox.showwarning("Aviso", "Seleccione un conductor.")
            return

        c = self.gestor.conductores[int(sel[0])]

        if any(v.conductor == c.nombre for v in self.gestor.viajes):
            messagebox.showerror(
                "Error",
                "No se puede eliminar un conductor con viajes registrados."
            )
            return

        if messagebox.askyesno("Confirmar", f"¿Eliminar a {c.nombre}?"):
            try:
                eliminar_conductor(c.id)
                self.gestor.eliminar_conductor(c.id)
                self.mostrar_conductores()
                self.actualizar_combo_conductores()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def limpiar_conductor(self):
        for x in ("nombre_conductor", "licencia", "telefono"):
            self.campos[x].set("")

    def actualizar_combo_conductores(self):
        nombres = [
            c.nombre for c in self.gestor.conductores if c.activo
        ]
        self.cconductor["values"] = nombres

        if nombres:
            self.cconductor.current(0)

    # ==================== VIAJES ====================

    def viajes_tab(self):
        tab = ttk.Frame(self.tabs)
        self.tabs.add(tab, text="Registrar viaje")

        marco = ttk.LabelFrame(tab, text="Viaje")
        marco.pack(fill="x", padx=10, pady=10)

        self.cveh = self.campo(marco, "vehiculo", "Vehículo", 0, 0, True)
        self.cveh.bind("<<ComboboxSelected>>", self.mostrar_info)

        self.campo(marco, "fecha", "Fecha", 0, 1)
        self.cconductor = self.campo(
            marco, "conductor", "Conductor", 1, 0, True
        )
        self.campo(marco, "origen", "Origen", 1, 1)
        self.campo(marco, "destino", "Destino", 2, 0)
        self.campo(marco, "km_inicial", "Km inicial", 2, 1)
        self.campo(marco, "km_final", "Km final", 3, 0)
        self.campo(marco, "observaciones", "Observaciones", 3, 1)

        self.info = ttk.Label(marco, foreground="blue")
        self.info.grid(row=4, column=0, columnspan=4)

        self.btn_t = ttk.Button(
            marco, text="Registrar", command=self.guardar_viaje
        )
        self.btn_t.grid(row=5, column=3, padx=5, pady=5)

        self.tt = self.tabla(
            tab,
            ("Fecha", "Vehículo", "Conductor", "Origen",
             "Destino", "Km", "Litros", "Gasto")
        )

    def mostrar_info(self, event=None):
        v = self.gestor.buscar_vehiculo(self.cveh.get())

        if v:
            self.info.config(
                text=f"{v.marca} {v.modelo} | "
                     f"{v.rendimiento:.2f} km/l | ${v.precio:.2f}/l"
            )

    def guardar_viaje(self):
        try:
            v = self.gestor.buscar_vehiculo(self.cveh.get())

            if not v:
                raise ValueError("Seleccione un vehículo.")

            if not self.cconductor.get():
                raise ValueError("Seleccione un conductor.")

            viaje = Viaje(
                fecha=self.campos["fecha"].get(),
                vehiculo=v,
                conductor=self.cconductor.get(),
                origen=self.campos["origen"].get(),
                destino=self.campos["destino"].get(),
                km_inicial=float(self.campos["km_inicial"].get()),
                km_final=float(self.campos["km_final"].get()),
                observaciones=self.campos["observaciones"].get()
            )

            if self.editando is None:
                self.gestor.agregar_viaje(viaje)
                mensaje = "Viaje registrado."
            else:
                self.gestor.modificar_viaje(self.editando, viaje)
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

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def actualizar_viajes(self):
        datos = [
            (
                v.fecha, v.vehiculo.nombre, v.conductor,
                v.origen, v.destino, f"{v.km:.2f}",
                f"{v.litros:.2f}", f"${v.gasto:.2f}"
            )
            for v in self.gestor.viajes
        ]

        self.llenar(self.tt, datos)
        self.llenar(self.th, datos)

    # ==================== RESUMEN ====================

    def resumen_tab(self):
        tab = ttk.Frame(self.tabs)
        self.tabs.add(tab, text="Resumen")

        self.resumen = ttk.Label(tab, font=("Arial", 13))
        self.resumen.pack(pady=15)

        self.th = self.tabla(
            tab,
            ("Fecha", "Vehículo", "Conductor", "Origen",
             "Destino", "Km", "Litros", "Gasto")
        )

        self.botones(tab, self.editar_viaje, self.eliminar_viaje)

    def editar_viaje(self):
        sel = self.th.selection()

        if not sel:
            messagebox.showwarning("Aviso", "Seleccione un viaje.")
            return

        i = int(sel[0])
        v = self.gestor.viajes[i]
        self.editando = i

        datos = {
            "fecha": v.fecha,
            "vehiculo": v.vehiculo.nombre,
            "conductor": v.conductor,
            "origen": v.origen,
            "destino": v.destino,
            "km_inicial": v.km_inicial,
            "km_final": v.km_final,
            "observaciones": v.observaciones
        }

        for campo, valor in datos.items():
            self.campos[campo].set(valor)

        self.mostrar_info()
        self.btn_t.config(text="Guardar cambios")
        self.tabs.select(2)

    def eliminar_viaje(self):
        sel = self.th.selection()

        if not sel:
            messagebox.showwarning("Aviso", "Seleccione un viaje.")
            return

        if messagebox.askyesno("Confirmar", "¿Eliminar viaje?"):
            self.gestor.eliminar_viaje(int(sel[0]))
            self.actualizar_viajes()
            self.actualizar_resumen()

    def actualizar_resumen(self):
        r = self.gestor.resumen()

        self.resumen.config(
            text=(
                f"Vehículos: {len(self.gestor.vehiculos)}   "
                f"Conductores: {len(self.gestor.conductores)}   "
                f"Viajes: {len(self.gestor.viajes)}\n"
                f"Km: {r['km']:.2f}   "
                f"Litros: {r['litros']:.2f}   "
                f"Gasto: ${r['gasto']:.2f}\n"
                f"Rendimiento: {r['rendimiento']:.2f} km/l   "
                f"Costo/km: ${r['costo_km']:.2f}"
            )
        )
