import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date

from modelos import Vehiculo, Viaje
from gestor import GestorDatos
from repositorio import (
    obtener_vehiculos, insertar_vehiculo,
    actualizar_vehiculo, eliminar_vehiculo
)


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestión de vehículos y combustible")
        self.root.geometry("1100x700")

        self.gestor = GestorDatos()
        self.campos = {}
        self.editando = self.editando_vehiculo = None

        self.interfaz()
        self.cargar_vehiculos()

    def interfaz(self):
        ttk.Label(
            self.root, text="Gestión de viajes y combustible",
            font=("Arial", 20, "bold")
        ).pack(pady=15)

        self.tabs = ttk.Notebook(self.root)
        self.tabs.pack(fill="both", expand=True, padx=10, pady=10)

        self.vehiculos_tab()
        self.viajes_tab()
        self.resumen_tab()

    def campo(self, padre, nombre, texto, fila, col, combo=False):
        ttk.Label(padre, text=texto).grid(
            row=fila, column=col * 2, padx=5, pady=5
        )

        valor = date.today().isoformat() if nombre == "fecha" else ""
        if nombre == "rendimiento":
            valor = "40"

        self.campos[nombre] = tk.StringVar(value=valor)

        w = ttk.Combobox(
            padre, textvariable=self.campos[nombre],
            state="readonly", width=22
        ) if combo else ttk.Entry(
            padre, textvariable=self.campos[nombre], width=24
        )

        w.grid(row=fila, column=col * 2 + 1, padx=5, pady=5)
        return w

    def tabla(self, padre, columnas):
        f = ttk.LabelFrame(padre, text="Registros")
        f.pack(fill="both", expand=True, padx=10, pady=10)

        t = ttk.Treeview(f, columns=columnas, show="headings")

        for c in columnas:
            t.heading(c, text=c)
            t.column(c, width=120, anchor="center")

        t.pack(side="left", fill="both", expand=True)

        sb = ttk.Scrollbar(f, command=t.yview)
        sb.pack(side="right", fill="y")
        t.config(yscrollcommand=sb.set)

        return t

    def llenar(self, tabla, datos):
        tabla.delete(*tabla.get_children())
        for i, dato in enumerate(datos):
            tabla.insert("", "end", iid=i, values=dato)

    # ================= VEHÍCULOS =================

    def vehiculos_tab(self):
        tab = ttk.Frame(self.tabs)
        self.tabs.add(tab, text="Vehículos")

        f = ttk.LabelFrame(tab, text="Vehículo")
        f.pack(fill="x", padx=10, pady=10)

        nombres = [
            ("Nombre", "nombre"), ("Placa", "placa"),
            ("Marca", "marca"), ("Modelo", "modelo"),
            ("Rendimiento", "rendimiento"), ("Precio litro", "precio")
        ]

        for i, (texto, nombre) in enumerate(nombres):
            self.campo(f, nombre, texto, i // 2, i % 2)

        self.btn_v = ttk.Button(
            f, text="Registrar", command=self.guardar_vehiculo
        )
        self.btn_v.grid(row=3, column=3)

        self.tv = self.tabla(
            tab, ("Vehículo", "Placa", "Marca",
                  "Modelo", "Rendimiento", "Precio")
        )

        b = ttk.Frame(tab)
        b.pack(pady=5)

        ttk.Button(
            b, text="Editar", command=self.editar_vehiculo
        ).pack(side="left", padx=5)

        ttk.Button(
            b, text="Eliminar", command=self.eliminar_vehiculo
        ).pack(side="left", padx=5)

    def cargar_vehiculos(self):
        try:
            self.gestor.vehiculos.clear()

            for r in obtener_vehiculos():
                self.gestor.vehiculos.append(
                    Vehiculo(
                        id=r[0], nombre=r[1], placa=r[2],
                        marca=r[3], modelo=r[4],
                        rendimiento=float(r[5]),
                        precio=float(r[6])
                    )
                )

            self.mostrar_vehiculos()
            self.actualizar_combo()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def datos_v(self):
        c = self.campos
        return (
            c["nombre"].get().strip(),
            c["placa"].get().strip(),
            c["marca"].get().strip(),
            c["modelo"].get().strip(),
            float(c["rendimiento"].get()),
            float(c["precio"].get())
        )

    def guardar_vehiculo(self):
        try:
            n, p, m, mo, r, precio = self.datos_v()

            if not n or not p:
                raise ValueError("Nombre y placa son obligatorios.")
            if r <= 0 or precio <= 0:
                raise ValueError("Rendimiento y precio deben ser mayores que 0.")

            if self.editando_vehiculo:
                actualizar_vehiculo(
                    self.editando_vehiculo,
                    n, p, m, mo, r, precio
                )

                for v in self.gestor.vehiculos:
                    if v.id == self.editando_vehiculo:
                        v.nombre, v.placa = n, p
                        v.marca, v.modelo = m, mo
                        v.rendimiento, v.precio = r, precio
                        break

                mensaje = "Vehículo actualizado."

            else:
                id_v = insertar_vehiculo(n, p, m, mo, r, precio)
                self.gestor.agregar_vehiculo(
                    Vehiculo(id_v, n, p, m, mo, r, precio)
                )
                mensaje = "Vehículo registrado."

            self.editando_vehiculo = None
            self.btn_v.config(text="Registrar")
            self.mostrar_vehiculos()
            self.actualizar_combo()
            self.limpiar_v()

            messagebox.showinfo("Correcto", mensaje)

        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def editar_vehiculo(self):
        s = self.tv.selection()

        if not s:
            messagebox.showwarning("Aviso", "Seleccione un vehículo.")
            return

        v = self.gestor.vehiculos[int(s[0])]
        self.editando_vehiculo = v.id

        for x in ("nombre", "placa", "marca", "modelo"):
            self.campos[x].set(getattr(v, x))

        self.campos["rendimiento"].set(v.rendimiento)
        self.campos["precio"].set(v.precio)
        self.btn_v.config(text="Guardar cambios")

    def eliminar_vehiculo(self):
        s = self.tv.selection()

        if not s:
            messagebox.showwarning("Aviso", "Seleccione un vehículo.")
            return

        v = self.gestor.vehiculos[int(s[0])]

        if messagebox.askyesno("Confirmar", f"¿Eliminar {v.nombre}?"):
            try:
                eliminar_vehiculo(v.id)
                self.gestor.eliminar_vehiculo(v.nombre)
                self.mostrar_vehiculos()
                self.actualizar_combo()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def mostrar_vehiculos(self):
        self.llenar(self.tv, [
            (
                v.nombre, v.placa, v.marca, v.modelo,
                f"{v.rendimiento:.2f}",
                f"${v.precio:.2f}"
            )
            for v in self.gestor.vehiculos
        ])

    def limpiar_v(self):
        for x in ("nombre", "placa", "marca", "modelo", "precio"):
            self.campos[x].set("")
        self.campos["rendimiento"].set("40")

    # ================= VIAJES =================

    def viajes_tab(self):
        tab = ttk.Frame(self.tabs)
        self.tabs.add(tab, text="Registrar viaje")

        f = ttk.LabelFrame(tab, text="Viaje")
        f.pack(fill="x", padx=10, pady=10)

        self.cveh = self.campo(f, "vehiculo", "Vehículo", 0, 0, True)
        self.cveh.bind("<<ComboboxSelected>>", self.mostrar_info)

        self.campo(f, "fecha", "Fecha", 0, 1)

        nombres = [
            ("Conductor", "conductor"),
            ("Origen", "origen"),
            ("Destino", "destino"),
            ("Km inicial", "km_inicial"),
            ("Km final", "km_final"),
            ("Observaciones", "observaciones")
        ]

        for i, (texto, nombre) in enumerate(nombres):
            self.campo(f, nombre, texto, i // 2 + 1, i % 2)

        self.info = ttk.Label(f, foreground="blue")
        self.info.grid(row=4, column=0, columnspan=4)

        self.btn_t = ttk.Button(
            f, text="Registrar", command=self.guardar_viaje
        )
        self.btn_t.grid(row=5, column=3)

        self.tt = self.tabla(
            tab,
            ("Fecha", "Vehículo", "Conductor", "Origen",
             "Destino", "Km", "Litros", "Gasto")
        )

    def actualizar_combo(self):
        nombres = [v.nombre for v in self.gestor.vehiculos]
        self.cveh["values"] = nombres

        if nombres:
            self.cveh.current(0)
            self.mostrar_info()

    def mostrar_info(self, event=None):
        v = self.gestor.buscar_vehiculo(self.cveh.get())

        if v:
            self.info.config(
                text=f"{v.marca} {v.modelo} | "
                     f"{v.rendimiento:.2f} km/l | "
                     f"${v.precio:.2f}/l"
            )

    def guardar_viaje(self):
        try:
            v = self.gestor.buscar_vehiculo(self.cveh.get())

            if not v:
                raise ValueError("Seleccione un vehículo.")

            c = self.campos

            viaje = Viaje(
                fecha=c["fecha"].get(),
                vehiculo=v,
                conductor=c["conductor"].get(),
                origen=c["origen"].get(),
                destino=c["destino"].get(),
                km_inicial=float(c["km_inicial"].get()),
                km_final=float(c["km_final"].get()),
                observaciones=c["observaciones"].get()
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

        except ValueError as e:
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

    # ================= RESUMEN =================

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

        b = ttk.Frame(tab)
        b.pack(pady=5)

        ttk.Button(
            b, text="Editar", command=self.editar_viaje
        ).pack(side="left", padx=5)

        ttk.Button(
            b, text="Eliminar", command=self.eliminar_viaje
        ).pack(side="left", padx=5)

    def editar_viaje(self):
        s = self.th.selection()

        if not s:
            return messagebox.showwarning("Aviso", "Seleccione un viaje.")

        i = int(s[0])
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

        for x, valor in datos.items():
            self.campos[x].set(valor)

        self.mostrar_info()
        self.btn_t.config(text="Guardar cambios")
        self.tabs.select(1)

    def eliminar_viaje(self):
        s = self.th.selection()

        if s and messagebox.askyesno("Confirmar", "¿Eliminar viaje?"):
            self.gestor.eliminar_viaje(int(s[0]))
            self.actualizar_viajes()
            self.actualizar_resumen()

    def actualizar_resumen(self):
        r = self.gestor.resumen()

        self.resumen.config(
            text=(
                f"Vehículos: {len(self.gestor.vehiculos)}   "
                f"Viajes: {len(self.gestor.viajes)}\n"
                f"Km: {r['km']:.2f}   "
                f"Litros: {r['litros']:.2f}   "
                f"Gasto: ${r['gasto']:.2f}\n"
                f"Rendimiento: {r['rendimiento']:.2f} km/l   "
                f"Costo/km: ${r['costo_km']:.2f}"
            )
        )
