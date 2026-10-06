"""
Interfaz grafica con Tkinter.
Separada en pestanias independientes para mejor mantenimiento.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date

from modelos import Vehiculo, Conductor, Viaje
from repositorio import (
    obtener_vehiculos, insertar_vehiculo, actualizar_vehiculo,
    eliminar_vehiculo as repo_eliminar_vehiculo,
    obtener_conductores, insertar_conductor, actualizar_conductor,
    eliminar_conductor as repo_eliminar_conductor,
    obtener_viajes, insertar_viaje, actualizar_viaje,
    eliminar_viaje as repo_eliminar_viaje,
    viajes_por_vehiculo, viajes_por_conductor,
    obtener_zonas,
)



# ── Utilidades comunes ────────────────────────────────────────────────

def crear_campo(padre, campos_dict, nombre, texto, fila, col,
                combo=False, valor_defecto=""):
    """Crea un label + entry/combobox y lo registra en campos_dict."""
    ttk.Label(padre, text=texto).grid(
        row=fila, column=col * 2, padx=5, pady=5, sticky="e"
    )
    campos_dict[nombre] = tk.StringVar(value=valor_defecto)

    if combo:
        widget = ttk.Combobox(
            padre, textvariable=campos_dict[nombre],
            state="readonly", width=22
        )
    else:
        widget = ttk.Entry(
            padre, textvariable=campos_dict[nombre], width=24
        )

    widget.grid(row=fila, column=col * 2 + 1, padx=5, pady=5)
    return widget


def crear_tabla(padre, columnas, titulo="Registros"):
    """Crea un Treeview con scrollbar dentro de un LabelFrame."""
    marco = ttk.LabelFrame(padre, text=titulo)
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


def llenar_tabla(tabla, datos):
    """Limpia y llena una tabla con nuevos datos."""
    tabla.delete(*tabla.get_children())
    for i, dato in enumerate(datos):
        tabla.insert("", "end", iid=i, values=dato)


# ── Pestania Vehiculos ────────────────────────────────────────────────

class VehiculosTab:
    def __init__(self, notebook, app):
        self.app = app
        self.tab = ttk.Frame(notebook)
        notebook.add(self.tab, text="Vehiculos")

        self.campos = {}
        self.editando = None
        self.vehiculos = []

        self._crear_formulario()
        self._crear_tabla()
        self.cargar()

    def _crear_formulario(self):
        marco = ttk.LabelFrame(self.tab, text="Vehiculo")
        marco.pack(fill="x", padx=10, pady=10)

        campos_def = [
            ("nombre", "Nombre", 0, 0),
            ("placa", "Placa", 0, 1),
            ("marca", "Marca", 1, 0),
            ("modelo", "Modelo", 1, 1),
            ("rendimiento", "Rendimiento (km/l)", 2, 0),
            ("precio", "Precio por litro", 2, 1),
        ]
        for nombre, texto, fila, col in campos_def:
            defecto = "40" if nombre == "rendimiento" else ""
            crear_campo(marco, self.campos, nombre, texto, fila, col,
                        valor_defecto=defecto)

        btn_frame = ttk.Frame(marco)
        btn_frame.grid(row=3, column=0, columnspan=4, pady=5)

        self.btn_guardar = ttk.Button(
            btn_frame, text="Registrar", command=self.guardar
        )
        self.btn_guardar.pack(side="left", padx=5)

        self.btn_cancelar = ttk.Button(
            btn_frame, text="Cancelar", command=self.cancelar,
            state="disabled"
        )
        self.btn_cancelar.pack(side="left", padx=5)

    def _crear_tabla(self):
        self.tabla = crear_tabla(
            self.tab,
            ("Vehiculo", "Placa", "Marca", "Modelo", "Rendimiento", "Precio")
        )
        frame = ttk.Frame(self.tab)
        frame.pack(pady=5)
        ttk.Button(frame, text="Editar", command=self.editar).pack(
            side="left", padx=5
        )
        ttk.Button(frame, text="Eliminar", command=self.eliminar).pack(
            side="left", padx=5
        )

    def cargar(self):
        try:
            self.vehiculos = obtener_vehiculos()
            self._mostrar()
        except Exception as e:
            print(f"Error cargando vehiculos: {e}")
            messagebox.showerror("Error", str(e))

    def _mostrar(self):
        llenar_tabla(self.tabla, [
            (v.nombre, v.placa, v.marca, v.modelo,
             f"{v.rendimiento:.2f}", f"${v.precio:.2f}")
            for v in self.vehiculos
        ])

    def guardar(self):
        try:
            vehiculo = Vehiculo(
                id=self.editando,
                nombre=self.campos["nombre"].get().strip(),
                placa=self.campos["placa"].get().strip(),
                marca=self.campos["marca"].get().strip(),
                modelo=self.campos["modelo"].get().strip(),
                rendimiento=float(self.campos["rendimiento"].get() or 0),
                precio=float(self.campos["precio"].get() or 0),
            )
            vehiculo.validar()

            if self.editando is None:
                vehiculo.id = insertar_vehiculo(vehiculo)
                mensaje = "Vehiculo registrado."
            else:
                actualizar_vehiculo(vehiculo)
                mensaje = "Vehiculo actualizado."

            self.cancelar()
            self.cargar()
            self.app.on_vehiculos_changed()
            messagebox.showinfo("Correcto", mensaje)

        except ValueError as e:
            messagebox.showerror("Error de validacion", str(e))
        except Exception as e:
            print(f"Error guardando vehiculo: {e}")
            messagebox.showerror("Error", str(e))

    def editar(self):
        sel = self.tabla.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Seleccione un vehiculo.")
            return

        v = self.vehiculos[int(sel[0])]
        self.editando = v.id

        for campo, valor in {
            "nombre": v.nombre, "placa": v.placa,
            "marca": v.marca, "modelo": v.modelo,
            "rendimiento": v.rendimiento, "precio": v.precio
        }.items():
            self.campos[campo].set(valor)

        self.btn_guardar.config(text="Guardar cambios")
        self.btn_cancelar.config(state="normal")

    def eliminar(self):
        sel = self.tabla.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Seleccione un vehiculo.")
            return

        v = self.vehiculos[int(sel[0])]
        if messagebox.askyesno("Confirmar", f"Eliminar {v.nombre}?"):
            try:
                repo_eliminar_vehiculo(v.id)
                self.cargar()
                self.app.on_vehiculos_changed()
            except Exception as e:
                print(f"Error eliminando vehiculo: {e}")
                messagebox.showerror("Error", str(e))

    def cancelar(self):
        self.editando = None
        self.btn_guardar.config(text="Registrar")
        self.btn_cancelar.config(state="disabled")
        for key in self.campos:
            self.campos[key].set(
                "40" if key == "rendimiento" else ""
            )


# ── Pestania Conductores ──────────────────────────────────────────────

class ConductoresTab:
    def __init__(self, notebook, app):
        self.app = app
        self.tab = ttk.Frame(notebook)
        notebook.add(self.tab, text="Conductores")

        self.campos = {}
        self.editando = None
        self.conductores = []

        self._crear_formulario()
        self._crear_tabla()
        self.cargar()

    def _crear_formulario(self):
        marco = ttk.LabelFrame(self.tab, text="Conductor")
        marco.pack(fill="x", padx=10, pady=10)

        crear_campo(marco, self.campos, "nombre_c", "Nombre", 0, 0)
        crear_campo(marco, self.campos, "licencia", "Licencia", 0, 1)
        crear_campo(marco, self.campos, "telefono", "Telefono", 1, 0)

        btn_frame = ttk.Frame(marco)
        btn_frame.grid(row=1, column=2, columnspan=2, pady=5)

        self.btn_guardar = ttk.Button(
            btn_frame, text="Registrar", command=self.guardar
        )
        self.btn_guardar.pack(side="left", padx=5)

        self.btn_cancelar = ttk.Button(
            btn_frame, text="Cancelar", command=self.cancelar,
            state="disabled"
        )
        self.btn_cancelar.pack(side="left", padx=5)

    def _crear_tabla(self):
        self.tabla = crear_tabla(
            self.tab, ("Nombre", "Licencia", "Telefono", "Estado")
        )
        frame = ttk.Frame(self.tab)
        frame.pack(pady=5)
        ttk.Button(frame, text="Editar", command=self.editar).pack(
            side="left", padx=5
        )
        ttk.Button(frame, text="Eliminar", command=self.eliminar).pack(
            side="left", padx=5
        )

    def cargar(self):
        try:
            self.conductores = obtener_conductores()
            self._mostrar()
        except Exception as e:
            print(f"Error cargando conductores: {e}")
            messagebox.showerror("Error", str(e))

    def _mostrar(self):
        llenar_tabla(self.tabla, [
            (c.nombre, c.licencia, c.telefono,
             "Activo" if c.activo else "Inactivo")
            for c in self.conductores
        ])

    def guardar(self):
        try:
            conductor = Conductor(
                id=self.editando,
                nombre=self.campos["nombre_c"].get().strip(),
                licencia=self.campos["licencia"].get().strip(),
                telefono=self.campos["telefono"].get().strip(),
            )
            conductor.validar()

            if self.editando is None:
                conductor.id = insertar_conductor(conductor)
                mensaje = "Conductor registrado."
            else:
                actualizar_conductor(conductor)
                mensaje = "Conductor actualizado."

            self.cancelar()
            self.cargar()
            self.app.on_conductores_changed()
            messagebox.showinfo("Correcto", mensaje)

        except ValueError as e:
            messagebox.showerror("Error de validacion", str(e))
        except Exception as e:
            print(f"Error guardando conductor: {e}")
            messagebox.showerror("Error", str(e))

    def editar(self):
        sel = self.tabla.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Seleccione un conductor.")
            return

        c = self.conductores[int(sel[0])]
        self.editando = c.id

        self.campos["nombre_c"].set(c.nombre)
        self.campos["licencia"].set(c.licencia)
        self.campos["telefono"].set(c.telefono)

        self.btn_guardar.config(text="Guardar cambios")
        self.btn_cancelar.config(state="normal")

    def eliminar(self):
        sel = self.tabla.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Seleccione un conductor.")
            return

        c = self.conductores[int(sel[0])]
        if messagebox.askyesno("Confirmar", f"Eliminar a {c.nombre}?"):
            try:
                repo_eliminar_conductor(c.id)
                self.cargar()
                self.app.on_conductores_changed()
            except Exception as e:
                print(f"Error eliminando conductor: {e}")
                messagebox.showerror("Error", str(e))

    def cancelar(self):
        self.editando = None
        self.btn_guardar.config(text="Registrar")
        self.btn_cancelar.config(state="disabled")
        for key in self.campos:
            self.campos[key].set("")

    def activos(self):
        return [c for c in self.conductores if c.activo]


# ── Pestania Viajes ───────────────────────────────────────────────────

class ViajesTab:
    def __init__(self, notebook, app):
        self.app = app
        self.tab = ttk.Frame(notebook)
        notebook.add(self.tab, text="Registrar viaje")

        self.campos = {}
        self.editando = None

        self._crear_formulario()
        self._crear_tabla()

    def _crear_formulario(self):
        marco = ttk.LabelFrame(self.tab, text="Viaje")
        marco.pack(fill="x", padx=10, pady=10)

        self.combo_vehiculo = crear_campo(
            marco, self.campos, "vehiculo", "Vehiculo", 0, 0, combo=True
        )
        self.combo_vehiculo.bind("<<ComboboxSelected>>", self._mostrar_info)

        crear_campo(marco, self.campos, "fecha", "Fecha (AAAA-MM-DD)",
                    0, 1, valor_defecto=date.today().isoformat())

        self.combo_conductor = crear_campo(
            marco, self.campos, "conductor", "Conductor", 1, 0, combo=True
        )
        crear_campo(marco, self.campos, "origen", "Origen", 1, 1)
        crear_campo(marco, self.campos, "destino", "Destino", 2, 0)
        crear_campo(marco, self.campos, "km_inicial", "Km inicial", 2, 1)
        crear_campo(marco, self.campos, "km_final", "Km final", 3, 0)
        self.combo_zona = crear_campo(
            marco, self.campos, "zona", "Zona/Ruta", 3, 1, combo=True
        )
        crear_campo(marco, self.campos, "observaciones", "Observaciones", 4, 0)

        self.info_label = ttk.Label(marco, foreground="blue")
        self.info_label.grid(row=5, column=0, columnspan=4)

        btn_frame = ttk.Frame(marco)
        btn_frame.grid(row=6, column=0, columnspan=4, pady=5)

        self.btn_guardar = ttk.Button(
            btn_frame, text="Registrar", command=self.guardar
        )
        self.btn_guardar.pack(side="left", padx=5)

        self.btn_cancelar = ttk.Button(
            btn_frame, text="Cancelar", command=self.cancelar,
            state="disabled"
        )
        self.btn_cancelar.pack(side="left", padx=5)

    def _crear_tabla(self):
        self.tabla = crear_tabla(
            self.tab,
            ("Fecha", "Vehiculo", "Conductor", "Zona",
             "Origen", "Destino", "Km", "Litros", "Gasto")
        )

    def actualizar_combos(self):
        vehiculos = self.app.vehiculos_tab.vehiculos
        nombres_v = [v.nombre for v in vehiculos]
        self.combo_vehiculo["values"] = nombres_v
        if nombres_v:
            self.combo_vehiculo.current(0)
            self._mostrar_info()

        conductores = self.app.conductores_tab.activos()
        nombres_c = [c.nombre for c in conductores]
        self.combo_conductor["values"] = nombres_c
        if nombres_c:
            self.combo_conductor.current(0)

        # Cargar zonas desde Orgzone
        try:
            self.zonas = obtener_zonas()
            nombres_z = [z[1] for z in self.zonas]
            self.combo_zona["values"] = nombres_z
            if nombres_z:
                self.combo_zona.current(0)
        except Exception as e:
            print(f"Error cargando zonas: {e}")
            self.zonas = []

    def _mostrar_info(self, event=None):
        nombre = self.campos["vehiculo"].get()
        vehiculos = self.app.vehiculos_tab.vehiculos
        v = next((x for x in vehiculos if x.nombre == nombre), None)
        if v:
            self.info_label.config(
                text=f"{v.marca} {v.modelo} | "
                     f"{v.rendimiento:.2f} km/l | ${v.precio:.2f}/l"
            )

    def guardar(self):
        try:
            nombre_v = self.campos["vehiculo"].get()
            nombre_c = self.campos["conductor"].get()

            vehiculos = self.app.vehiculos_tab.vehiculos
            v = next((x for x in vehiculos if x.nombre == nombre_v), None)
            if not v:
                raise ValueError("Seleccione un vehiculo.")

            conductores = self.app.conductores_tab.conductores
            c = next((x for x in conductores if x.nombre == nombre_c), None)
            if not c:
                raise ValueError("Seleccione un conductor.")

            # Obtener zona seleccionada
            nombre_zona = self.campos["zona"].get()
            zona_sel = next(
                (z for z in self.zonas if z[1] == nombre_zona), None
            )
            zona_id = zona_sel[0] if zona_sel else None

            viaje = Viaje(
                id=self.editando,
                fecha=self.campos["fecha"].get().strip(),
                vehiculo=v,
                conductor_id=c.id,
                conductor_nombre=c.nombre,
                origen=self.campos["origen"].get().strip(),
                destino=self.campos["destino"].get().strip(),
                km_inicial=float(self.campos["km_inicial"].get() or 0),
                km_final=float(self.campos["km_final"].get() or 0),
                zona_id=zona_id,
                zona_nombre=nombre_zona or "",
                observaciones=self.campos["observaciones"].get().strip(),
            )
            viaje.validar()

            if self.editando is None:
                viaje.id = insertar_viaje(viaje)
                mensaje = "Viaje registrado."
            else:
                actualizar_viaje(viaje)
                mensaje = "Viaje actualizado."

            self.cancelar()
            self.app.cargar_viajes()

            messagebox.showinfo(
                "Correcto",
                f"{mensaje}\n\n"
                f"Km: {viaje.km:.2f}\n"
                f"Litros: {viaje.litros:.2f}\n"
                f"Gasto: ${viaje.gasto:.2f}"
            )

        except ValueError as e:
            messagebox.showerror("Error de validacion", str(e))
        except Exception as e:
            print(f"Error guardando viaje: {e}")
            messagebox.showerror("Error", str(e))

    def editar_viaje(self, viaje):
        """Llamado desde ResumenTab para editar un viaje."""
        self.editando = viaje.id

        self.campos["fecha"].set(viaje.fecha)
        self.campos["vehiculo"].set(viaje.vehiculo.nombre)
        self.campos["conductor"].set(viaje.conductor_nombre)
        self.campos["origen"].set(viaje.origen)
        self.campos["destino"].set(viaje.destino)
        self.campos["km_inicial"].set(viaje.km_inicial)
        self.campos["km_final"].set(viaje.km_final)
        self.campos["zona"].set(viaje.zona_nombre)
        self.campos["observaciones"].set(viaje.observaciones)

        self._mostrar_info()
        self.btn_guardar.config(text="Guardar cambios")
        self.btn_cancelar.config(state="normal")

    def mostrar_viajes(self, viajes):
        llenar_tabla(self.tabla, [
            (v.fecha, v.vehiculo.nombre, v.conductor_nombre,
             v.zona_nombre, v.origen, v.destino, f"{v.km:.2f}",
             f"{v.litros:.2f}", f"${v.gasto:.2f}")
            for v in viajes
        ])

    def cancelar(self):
        self.editando = None
        self.btn_guardar.config(text="Registrar")
        self.btn_cancelar.config(state="disabled")
        for key in ("origen", "destino", "km_inicial",
                     "km_final", "observaciones"):
            self.campos[key].set("")
        self.campos["fecha"].set(date.today().isoformat())


# ── Pestania Resumen ──────────────────────────────────────────────────

class ResumenTab:
    def __init__(self, notebook, app):
        self.app = app
        self.tab = ttk.Frame(notebook)
        notebook.add(self.tab, text="Resumen")

        self.resumen_label = ttk.Label(self.tab, font=("Arial", 13))
        self.resumen_label.pack(pady=15)

        # Filtros
        filtro_frame = ttk.LabelFrame(self.tab, text="Filtros")
        filtro_frame.pack(fill="x", padx=10, pady=5)

        self.filtros = {}
        crear_campo(filtro_frame, self.filtros, "filtro_vehiculo",
                    "Vehiculo", 0, 0, combo=True)
        crear_campo(filtro_frame, self.filtros, "filtro_conductor",
                    "Conductor", 0, 1, combo=True)
        crear_campo(filtro_frame, self.filtros, "fecha_desde",
                    "Desde", 1, 0)
        crear_campo(filtro_frame, self.filtros, "fecha_hasta",
                    "Hasta", 1, 1)

        btn_frame = ttk.Frame(filtro_frame)
        btn_frame.grid(row=2, column=0, columnspan=4, pady=5)
        ttk.Button(btn_frame, text="Filtrar",
                   command=self._aplicar_filtros).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Limpiar filtros",
                   command=self._limpiar_filtros).pack(side="left", padx=5)

        self.tabla = crear_tabla(
            self.tab,
            ("Fecha", "Vehiculo", "Conductor", "Zona",
             "Origen", "Destino", "Km", "Litros", "Gasto")
        )

        frame = ttk.Frame(self.tab)
        frame.pack(pady=5)
        ttk.Button(frame, text="Editar", command=self._editar).pack(
            side="left", padx=5
        )
        ttk.Button(frame, text="Eliminar", command=self._eliminar).pack(
            side="left", padx=5
        )

        self.viajes_mostrados = []

    def actualizar(self, viajes):
        self.todos_los_viajes = viajes
        self._aplicar_filtros()

    def actualizar_combos_filtro(self):
        vehiculos = self.app.vehiculos_tab.vehiculos
        self.filtros["filtro_vehiculo"].set("")
        # acceder al widget combobox
        for widget in self.tab.winfo_children():
            if isinstance(widget, ttk.LabelFrame):
                for child in widget.winfo_children():
                    pass

        # Buscar los combos por nombre de variable
        nombres_v = [""] + [v.nombre for v in vehiculos]
        conductores = self.app.conductores_tab.conductores
        nombres_c = [""] + [c.nombre for c in conductores]

        # Actualizar combos de filtro
        self._combo_filtro_vehiculo["values"] = nombres_v
        self._combo_filtro_conductor["values"] = nombres_c

    @property
    def _combo_filtro_vehiculo(self):
        """Obtiene el widget combobox de filtro vehiculo."""
        # Buscar en el frame de filtros
        for widget in self.tab.winfo_children():
            if isinstance(widget, ttk.LabelFrame) and widget.cget("text") == "Filtros":
                for child in widget.winfo_children():
                    if isinstance(child, ttk.Combobox):
                        var = str(child.cget("textvariable"))
                        actual_var = str(self.filtros["filtro_vehiculo"])
                        if var == actual_var:
                            return child
        return ttk.Combobox()

    @property
    def _combo_filtro_conductor(self):
        """Obtiene el widget combobox de filtro conductor."""
        for widget in self.tab.winfo_children():
            if isinstance(widget, ttk.LabelFrame) and widget.cget("text") == "Filtros":
                for child in widget.winfo_children():
                    if isinstance(child, ttk.Combobox):
                        var = str(child.cget("textvariable"))
                        actual_var = str(self.filtros["filtro_conductor"])
                        if var == actual_var:
                            return child
        return ttk.Combobox()

    def _aplicar_filtros(self):
        viajes = getattr(self, "todos_los_viajes", [])
        f_vehiculo = self.filtros.get("filtro_vehiculo",
                                       tk.StringVar()).get()
        f_conductor = self.filtros.get("filtro_conductor",
                                        tk.StringVar()).get()
        f_desde = self.filtros.get("fecha_desde", tk.StringVar()).get()
        f_hasta = self.filtros.get("fecha_hasta", tk.StringVar()).get()

        filtrados = viajes
        if f_vehiculo:
            filtrados = [v for v in filtrados
                         if v.vehiculo.nombre == f_vehiculo]
        if f_conductor:
            filtrados = [v for v in filtrados
                         if v.conductor_nombre == f_conductor]
        if f_desde:
            filtrados = [v for v in filtrados if v.fecha >= f_desde]
        if f_hasta:
            filtrados = [v for v in filtrados if v.fecha <= f_hasta]

        self.viajes_mostrados = filtrados
        self._mostrar(filtrados)

    def _limpiar_filtros(self):
        for key in self.filtros:
            self.filtros[key].set("")
        self._aplicar_filtros()

    def _mostrar(self, viajes):
        llenar_tabla(self.tabla, [
            (v.fecha, v.vehiculo.nombre, v.conductor_nombre,
             v.zona_nombre, v.origen, v.destino, f"{v.km:.2f}",
             f"{v.litros:.2f}", f"${v.gasto:.2f}")
            for v in viajes
        ])

        km = sum(v.km for v in viajes)
        litros = sum(v.litros for v in viajes)
        gasto = sum(v.gasto for v in viajes)

        total_vehiculos = len(self.app.vehiculos_tab.vehiculos)
        total_conductores = len(self.app.conductores_tab.conductores)

        self.resumen_label.config(text=(
            f"Vehiculos: {total_vehiculos}   "
            f"Conductores: {total_conductores}   "
            f"Viajes: {len(viajes)}\n"
            f"Km: {km:.2f}   "
            f"Litros: {litros:.2f}   "
            f"Gasto: ${gasto:.2f}\n"
            f"Rendimiento: {km / litros if litros else 0:.2f} km/l   "
            f"Costo/km: ${gasto / km if km else 0:.2f}"
        ))

    def _editar(self):
        sel = self.tabla.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Seleccione un viaje.")
            return

        viaje = self.viajes_mostrados[int(sel[0])]
        self.app.viajes_tab.editar_viaje(viaje)
        self.app.tabs.select(2)

    def _eliminar(self):
        sel = self.tabla.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Seleccione un viaje.")
            return

        viaje = self.viajes_mostrados[int(sel[0])]
        if messagebox.askyesno("Confirmar", "Eliminar este viaje?"):
            try:
                repo_eliminar_viaje(viaje.id)
                self.app.cargar_viajes()
            except Exception as e:
                print(f"Error eliminando viaje: {e}")
                messagebox.showerror("Error", str(e))


# ── Pestania Reportes ─────────────────────────────────────────────────

class ReportesTab:
    def __init__(self, notebook, app):
        self.app = app
        self.tab = ttk.Frame(notebook)
        notebook.add(self.tab, text="Reportes")

        ttk.Button(
            self.tab, text="Actualizar reportes",
            command=self.actualizar
        ).pack(pady=10)

        # Reporte por vehiculo
        self.tabla_vehiculos = crear_tabla(
            self.tab,
            ("Vehiculo", "Viajes", "Km", "Litros", "Gasto"),
            titulo="Por vehiculo"
        )

        # Reporte por conductor
        self.tabla_conductores = crear_tabla(
            self.tab,
            ("Conductor", "Viajes", "Km"),
            titulo="Por conductor"
        )

    def actualizar(self):
        try:
            datos_v = viajes_por_vehiculo()
            llenar_tabla(self.tabla_vehiculos, [
                (d["vehiculo"], d["viajes"], f"{d['km']:.2f}",
                 f"{d['litros']:.2f}", f"${d['gasto']:.2f}")
                for d in datos_v
            ])

            datos_c = viajes_por_conductor()
            llenar_tabla(self.tabla_conductores, [
                (d["conductor"], d["viajes"], f"{d['km']:.2f}")
                for d in datos_c
            ])

        except Exception as e:
            print(f"Error en reportes: {e}")
            messagebox.showerror("Error", str(e))


# ── Aplicacion principal ──────────────────────────────────────────────

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestion de vehiculos y combustible")
        self.root.geometry("1200x800")

        ttk.Label(
            self.root, text="Gestion de viajes y combustible",
            font=("Arial", 20, "bold")
        ).pack(pady=15)

        self.tabs = ttk.Notebook(self.root)
        self.tabs.pack(fill="both", expand=True, padx=10, pady=10)

        # Crear pestanias
        self.vehiculos_tab = VehiculosTab(self.tabs, self)
        self.conductores_tab = ConductoresTab(self.tabs, self)
        self.viajes_tab = ViajesTab(self.tabs, self)
        self.resumen_tab = ResumenTab(self.tabs, self)
        self.reportes_tab = ReportesTab(self.tabs, self)

        # Actualizar combos iniciales
        self.viajes_tab.actualizar_combos()
        self.cargar_viajes()

        # Actualizar resumen al cambiar de pestania
        self.tabs.bind("<<NotebookTabChanged>>", self._on_tab_changed)

    def on_vehiculos_changed(self):
        self.viajes_tab.actualizar_combos()

    def on_conductores_changed(self):
        self.viajes_tab.actualizar_combos()

    def cargar_viajes(self):
        try:
            vehiculos_dict = {
                v.id: v for v in self.vehiculos_tab.vehiculos
            }
            viajes = obtener_viajes(vehiculos_dict)
            self.viajes_tab.mostrar_viajes(viajes)
            self.resumen_tab.actualizar(viajes)
        except Exception as e:
            print(f"Error cargando viajes: {e}")
            messagebox.showerror("Error", str(e))

    def _on_tab_changed(self, event=None):
        """Actualiza datos al cambiar de pestania."""
        tab_index = self.tabs.index(self.tabs.select())
        if tab_index == 3:  # Resumen
            self.cargar_viajes()
        elif tab_index == 4:  # Reportes
            self.reportes_tab.actualizar()