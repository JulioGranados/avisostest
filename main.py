import json
import os
from datetime import datetime
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.graphics import Color, Rectangle

COLOR_NOMBRES = {
    "blanco": (1, 1, 1, 1),
    "negro": (0, 0, 0, 1),
    "rojo": (1, 0, 0, 1),
    "verde": (0, 1, 0, 1),
    "azul": (0, 0, 1, 1),
    "celeste": (0.68, 0.85, 0.9, 1),
    "verdeclaro": (0.56, 0.93, 0.56, 1),
    "beige": (0.96, 0.96, 0.86, 1),
    "lavanda": (0.9, 0.9, 0.98, 1),
    "gris": (0.83, 0.83, 0.83, 1),
    "naranja": (1, 0.65, 0, 1),
    "amarillo": (1, 1, 0, 1)
}

COLOR_PRIORIDAD = {
    "Alta": (1, 0.30, 0, 1),
    "Media": (1, 0.65, 0, 1),
    "Baja": (0, 0.5, 0, 1),
    "Normal": (0.50, 0.50, 0.50, 0.50)
}

USUARIOS_FILE = "usuarios.json"
SESION_FILE = "sesion.json"
MAX_AVISOS_GRATIS = 6

class Aviso:
    def __init__(self, titulo, mensaje, fecha, importancia="Normal"):
        self.titulo = titulo
        self.mensaje = mensaje
        self.fecha = fecha
        self.importancia = importancia

    def to_dict(self):
        return {
            "titulo": self.titulo,
            "mensaje": self.mensaje,
            "fecha": self.fecha,
            "importancia": self.importancia
        }

    @staticmethod
    def from_dict(data):
        return Aviso(data["titulo"], data["mensaje"], data["fecha"], data.get("importancia", "Normal"))

class AvisosApp(App):
    def calcular_color_texto(self, rgba):
        r, g, b, a = rgba
        brillo = 0.299*r + 0.587*g + 0.114*b
        return (1, 1, 1, 1) if brillo < 0.5 else (0, 0, 0, 1)

    def build(self):
        self.avisos = []
        self.usuario_actual = None
        self.alias_actual = None
        self.color_fondo = COLOR_NOMBRES["blanco"]
        self.color_texto = self.calcular_color_texto(self.color_fondo)
        self.usuario_premium = False

        self.root = BoxLayout(orientation='vertical')
        with self.root.canvas.before:
            Color(*self.color_fondo)
            self.rect = Rectangle(size=self.root.size, pos=self.root.pos)
        self.root.bind(size=self._update_rect, pos=self._update_rect)

        self.cargar_usuarios()

        if self.cargar_sesion():
            self.mostrar_menu()
        else:
            self.mostrar_login()

        return self.root

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def cargar_usuarios(self):
        if os.path.exists(USUARIOS_FILE):
            try:
                with open(USUARIOS_FILE, "r", encoding="utf-8") as f:
                    self.usuarios = json.load(f)
            except:
                self.usuarios = []
        else:
            self.usuarios = []

    def guardar_usuarios(self):
        with open(USUARIOS_FILE, "w", encoding="utf-8") as f:
            json.dump(self.usuarios, f, indent=4)

    def obtener_archivo_avisos(self):
        return f"avisos_{self.alias_actual}.json"

    def cargar_avisos(self):
        archivo = self.obtener_archivo_avisos()
        if os.path.exists(archivo):
            try:
                with open(archivo, "r", encoding="utf-8") as f:
                    datos = json.load(f)
                    self.avisos = [Aviso.from_dict(d) for d in datos]
            except:
                self.avisos = []
        else:
            self.avisos = []

    def guardar_avisos(self):
        archivo = self.obtener_archivo_avisos()
        with open(archivo, "w", encoding="utf-8") as f:
            json.dump([aviso.to_dict() for aviso in self.avisos], f, indent=4)

    def guardar_sesion(self):
        data = {"alias": self.alias_actual}
        with open(SESION_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f)

    def cargar_sesion(self):
        if os.path.exists(SESION_FILE):
            try:
                with open(SESION_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    alias = data.get("alias", "")
                    for u in self.usuarios:
                        if u["alias"].lower() == alias.lower():
                            self.alias_actual = u["alias"]
                            self.usuario_actual = u["nombre"]
                            self.color_fondo = COLOR_NOMBRES.get(u.get("color", "blanco"), COLOR_NOMBRES["blanco"])
                            self.usuario_premium = u.get("premium", False)
                            self.color_texto = self.calcular_color_texto(self.color_fondo)

                            self.root.canvas.before.clear()
                            with self.root.canvas.before:
                                Color(*self.color_fondo)
                                self.rect = Rectangle(size=self.root.size, pos=self.root.pos)
                            self.root.bind(size=self._update_rect, pos=self._update_rect)

                            self.cargar_avisos()
                            return True
            except:
                pass
        return False

    def mostrar_login(self):
        self.root.clear_widgets()
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)

        lbl_title = Label(text="[b]🌱 Bienvenido a la app de avisos ecológicos 🌱[/b]", font_size=22, markup=True, color=(0,0.5,0,1), halign="center")
        lbl_title.bind(size=lbl_title.setter('text_size'))
        layout.add_widget(lbl_title)

        layout.add_widget(Label(text="Nombre real:", color=self.color_texto))
        self.input_nombre = TextInput(multiline=False, foreground_color=self.color_texto)
        layout.add_widget(self.input_nombre)

        layout.add_widget(Label(text="Alias (único):", color=self.color_texto))
        self.input_alias = TextInput(multiline=False, foreground_color=self.color_texto)
        layout.add_widget(self.input_alias)

        self.btn_entrar = Button(text="Entrar / Registrar", size_hint=(1, 0.3), background_color=COLOR_NOMBRES["verdeclaro"], color=(0,0,0,1))
        self.btn_entrar.bind(on_press=self.verificar_login)
        layout.add_widget(self.btn_entrar)

        self.root.add_widget(layout)

    def verificar_login(self, instance):
        nombre = self.input_nombre.text.strip()
        alias = self.input_alias.text.strip()

        if not nombre or not alias:
            self.mostrar_popup("Error", "Debes ingresar nombre y alias.")
            return

        usuario_existente = None
        for u in self.usuarios:
            if u["alias"].lower() == alias.lower():
                usuario_existente = u
                break

        if usuario_existente:
            if usuario_existente["nombre"].lower() != nombre.lower():
                self.mostrar_popup("Error", f"El alias '{alias}' ya está en uso por otro usuario.")
                return
            self.usuario_actual = usuario_existente["nombre"]
            self.alias_actual = usuario_existente["alias"]
            self.color_fondo = COLOR_NOMBRES.get(usuario_existente.get("color", "blanco"), COLOR_NOMBRES["blanco"])
            self.usuario_premium = usuario_existente.get("premium", False)

            self.guardar_sesion()
            self.color_texto = self.calcular_color_texto(self.color_fondo)

            self.root.canvas.before.clear()
            with self.root.canvas.before:
                Color(*self.color_fondo)
                self.rect = Rectangle(size=self.root.size, pos=self.root.pos)
            self.root.bind(size=self._update_rect, pos=self._update_rect)

            self.cargar_avisos()
            self.mostrar_menu()

        else:
            self.mostrar_form_registro(nombre, alias)

    def mostrar_form_registro(self, nombre, alias):
        self.root.clear_widgets()
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)

        layout.add_widget(Label(text=f"Registrando nuevo usuario: {alias}", color=self.color_texto))

        layout.add_widget(Label(text="¿Eres usuario premium? (si/no):", color=self.color_texto))
        self.input_premium = TextInput(multiline=False, foreground_color=self.color_texto)
        layout.add_widget(self.input_premium)

        layout.add_widget(Label(text="Color de fondo (ej: blanco, lavanda, beige):", color=self.color_texto))
        self.input_color = TextInput(multiline=False, foreground_color=self.color_texto)
        layout.add_widget(self.input_color)

        btn_guardar = Button(text="Guardar Registro", size_hint=(1, 0.3), background_color=COLOR_NOMBRES["verdeclaro"], color=(0,0,0,1))
        btn_guardar.bind(on_press=lambda inst: self.guardar_registro(nombre, alias))
        layout.add_widget(btn_guardar)

        btn_cancelar = Button(text="Cancelar", size_hint=(1, 0.3))
        btn_cancelar.bind(on_press=lambda inst: self.mostrar_login())
        layout.add_widget(btn_cancelar)

        self.root.add_widget(layout)

    def guardar_registro(self, nombre, alias):
        premium = self.input_premium.text.strip().lower()
        color = self.input_color.text.strip().lower()

        if premium not in ("si", "no"):
            self.mostrar_popup("Error", "Debes ingresar 'si' o 'no' en premium.")
            return
        if color not in COLOR_NOMBRES:
            color = "negro"

        self.usuario_actual = nombre
        self.alias_actual = alias
        self.color_fondo = COLOR_NOMBRES[color]
        self.usuario_premium = premium == "si"

        self.usuarios.append({
            "nombre": nombre,
            "alias": alias,
            "color": color,
            "premium": self.usuario_premium
        })
        self.guardar_usuarios()
        self.guardar_sesion()

        self.color_texto = self.calcular_color_texto(self.color_fondo)
        self.root.canvas.before.clear()
        with self.root.canvas.before:
            Color(*self.color_fondo)
            self.rect = Rectangle(size=self.root.size, pos=self.root.pos)
        self.root.bind(size=self._update_rect, pos=self._update_rect)

        self.avisos = []
        self.mostrar_menu()

    def mostrar_menu(self):
        self.root.clear_widgets()
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        lbl_user = Label(text=f"Usuario: {self.usuario_actual} (Alias: {self.alias_actual}) - Premium: {'Sí' if self.usuario_premium else 'No'}",
                         size_hint=(1,None), height=30, color=self.color_texto)
        layout.add_widget(lbl_user)

        btn_agregar = Button(text="Agregar Aviso", size_hint=(1, None), height=40)
        btn_agregar.bind(on_press=self.agregar_aviso)
        layout.add_widget(btn_agregar)

        btn_filtrar = Button(text="Filtrar Avisos", size_hint=(1, None), height=40)
        btn_filtrar.bind(on_press=self.mostrar_filtro_avisos)
        layout.add_widget(btn_filtrar)

        btn_color = Button(text="Cambiar Color Fondo", size_hint=(1, None), height=40)
        btn_color.bind(on_press=self.mostrar_selector_color)
        layout.add_widget(btn_color)

        btn_cerrar_sesion = Button(text="Cerrar Sesión", size_hint=(1, None), height=40, background_color=(0.8,0,0,1), color=(1,1,1,1))
        btn_cerrar_sesion.bind(on_press=self.cerrar_sesion)
        layout.add_widget(btn_cerrar_sesion)

        self.layout_avisos = BoxLayout(orientation='vertical', size_hint=(1,1))

        self.root.add_widget(layout)
        self.root.add_widget(self.layout_avisos)

        self.mostrar_lista_avisos(self.avisos)

    def mostrar_lista_avisos(self, avisos):
        self.layout_avisos.clear_widgets()
        scroll = ScrollView(size_hint=(1, 1))
        container = BoxLayout(orientation='vertical', size_hint_y=None, padding=10, spacing=10)
        container.bind(minimum_height=container.setter('height'))

        for idx, aviso in enumerate(avisos):
            box = BoxLayout(size_hint_y=None, height=100, padding=5, spacing=5)
            color = COLOR_PRIORIDAD.get(aviso.importancia, (0,0,0,1))
            titulo = Label(text=f"[b]{aviso.titulo}[/b]", markup=True, color=color, size_hint_x=0.4, halign="left", valign="middle")
            titulo.bind(size=titulo.setter('text_size'))
            mensaje = Label(text=aviso.mensaje, color=self.color_texto, size_hint_x=0.5, halign="left", valign="middle")
            mensaje.bind(size=mensaje.setter('text_size'))
            fecha = Label(text=aviso.fecha, color=self.color_texto, size_hint_x=0.3, halign="left", valign="middle")
            fecha.bind(size=fecha.setter('text_size'))

            box.add_widget(titulo)
            box.add_widget(mensaje)
            box.add_widget(fecha)

            btn_editar = Button(text="Editar", size_hint_x=0.15)
            btn_editar.bind(on_press=lambda inst, i=idx: self.accion_premium_o_editar(i))
            box.add_widget(btn_editar)

            btn_eliminar = Button(text="Eliminar", size_hint_x=0.15, background_color=(1,0,0,1))
            # Cambié aquí para llamar al confirm popup antes de eliminar
            btn_eliminar.bind(on_press=lambda inst, i=idx: self.confirmar_eliminar_aviso(i))
            box.add_widget(btn_eliminar)

            container.add_widget(box)

        scroll.add_widget(container)
        self.layout_avisos.add_widget(scroll)

    def accion_premium_o_editar(self, idx):
        if not self.usuario_premium:
            self.mostrar_popup("Función premium 🌟", "Esta función es solo para usuarios premium. ¡Mejora tu cuenta para desbloquearla!")
            return
        self.mostrar_editar_aviso(idx)

    def mostrar_editar_aviso(self, idx):
        aviso = self.avisos[idx]
        self.mostrar_formulario_aviso(aviso)

    # Nueva función para confirmar antes de eliminar
    def confirmar_eliminar_aviso(self, idx):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(text="¿Seguro que quieres eliminar este aviso? Esta acción no se puede deshacer.", color=(1,0,0,1)))
        btns = BoxLayout(spacing=10, size_hint=(1, 0.3))

        btn_si = Button(text="Sí", background_color=(1,0,0,1), color=(1,1,1,1))
        btn_no = Button(text="No", background_color=(0,1,0,1), color=(0,0,0,1))

        popup = Popup(title="Confirmar eliminación", content=content, size_hint=(0.8, 0.4), auto_dismiss=False)

        def eliminar_y_cerrar(instance):
            self.eliminar_aviso(idx)
            popup.dismiss()

        btn_si.bind(on_press=eliminar_y_cerrar)
        btn_no.bind(on_press=popup.dismiss)

        btns.add_widget(btn_si)
        btns.add_widget(btn_no)
        content.add_widget(btns)

        popup.open()

    def accion_premium_o_eliminar(self, idx):
        if not self.usuario_premium:
            self.mostrar_popup("Función premium 🌟", "Esta función es solo para usuarios premium. ¡Mejora tu cuenta para desbloquearla!")
            return
        self.confirmar_eliminar_aviso(idx)

    def agregar_aviso(self, instance):
        if not self.usuario_premium and len(self.avisos) >= MAX_AVISOS_GRATIS:
            self.mostrar_popup("Límite alcanzado", f"Solo puedes agregar {MAX_AVISOS_GRATIS} avisos como usuario gratuito. ¡Obtén la versión PREMIUM para más atributos!")
            return
        self.mostrar_formulario_aviso()

    def mostrar_formulario_aviso(self, aviso=None):
        self.popup_content = BoxLayout(orientation='vertical', padding=10, spacing=10)

        self.input_titulo = TextInput(hint_text="Título", multiline=False)
        self.input_mensaje = TextInput(hint_text="Mensaje", multiline=True)
        self.input_fecha = TextInput(hint_text="Fecha (YYYY-MM-DD HH:MM)", multiline=False)
        self.input_importancia = Spinner(text="Normal", values=["Alta", "Media", "Baja", "Normal"])

        if aviso:
            self.input_titulo.text = aviso.titulo
            self.input_mensaje.text = aviso.mensaje
            self.input_fecha.text = aviso.fecha
            self.input_importancia.text = aviso.importancia

        self.popup_content.add_widget(self.input_titulo)
        self.popup_content.add_widget(self.input_mensaje)
        self.popup_content.add_widget(self.input_fecha)
        self.popup_content.add_widget(self.input_importancia)

        btn_guardar = Button(text="Guardar", size_hint=(1, 0.3), background_color=COLOR_NOMBRES["verdeclaro"], color=(0,0,0,1))
        btn_guardar.bind(on_press=lambda inst: self.guardar_aviso(aviso))
        self.popup_content.add_widget(btn_guardar)

        btn_cancelar = Button(text="Cancelar", size_hint=(1, 0.3))
        btn_cancelar.bind(on_press=lambda inst: self.popup.dismiss())
        self.popup_content.add_widget(btn_cancelar)

        self.popup = Popup(title="Agregar / Editar Aviso", content=self.popup_content, size_hint=(0.8, 0.8))
        self.popup.open()

    def guardar_aviso(self, aviso=None):
        titulo = self.input_titulo.text.strip()
        mensaje = self.input_mensaje.text.strip()
        fecha = self.input_fecha.text.strip()
        importancia = self.input_importancia.text.strip()

        if not titulo or not mensaje or not fecha:
            self.mostrar_popup("Error", "Debe llenar todos los campos obligatorios")
            return

        try:
            datetime.strptime(fecha, "%Y-%m-%d %H:%M")
        except:
            self.mostrar_popup("Error", "Formato de fecha incorrecto. Use YYYY-MM-DD HH:MM")
            return

        if aviso:
            aviso.titulo = titulo
            aviso.mensaje = mensaje
            aviso.fecha = fecha
            aviso.importancia = importancia
        else:
            nuevo_aviso = Aviso(titulo, mensaje, fecha, importancia)
            self.avisos.append(nuevo_aviso)

        self.guardar_avisos()
        self.popup.dismiss()
        self.mostrar_lista_avisos(self.avisos)

    def mostrar_filtro_avisos(self, instance):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        spinner_importancia = Spinner(text="Todos", values=["Todos", "Alta", "Media", "Baja", "Normal"])
        content.add_widget(Label(text="Filtrar por importancia:"))
        content.add_widget(spinner_importancia)

        btn_filtrar = Button(text="Filtrar", size_hint=(1, 0.3))
        content.add_widget(btn_filtrar)

        popup = Popup(title="Filtrar avisos", content=content, size_hint=(0.8, 0.5))

        def aplicar_filtro(instance):
            filtro = spinner_importancia.text
            if filtro == "Todos":
                filtrados = self.avisos
            else:
                filtrados = [a for a in self.avisos if a.importancia == filtro]
            self.mostrar_lista_avisos(filtrados)
            popup.dismiss()

        btn_filtrar.bind(on_press=aplicar_filtro)
        popup.open()

    def mostrar_selector_color(self, instance):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        spinner_color = Spinner(text="blanco", values=list(COLOR_NOMBRES.keys()))
        content.add_widget(Label(text="Seleccionar color de fondo:"))
        content.add_widget(spinner_color)

        btn_aplicar = Button(text="Aplicar", size_hint=(1, 0.3))
        content.add_widget(btn_aplicar)

        popup = Popup(title="Cambiar color de fondo", content=content, size_hint=(0.8, 0.5))

        def aplicar_color(instance):
            color = spinner_color.text
            self.color_fondo = COLOR_NOMBRES[color]
            self.color_texto = self.calcular_color_texto(self.color_fondo)
            for w in self.root.walk():
                if isinstance(w, Label):
                    w.color = self.color_texto
            self.root.canvas.before.clear()
            with self.root.canvas.before:
                Color(*self.color_fondo)
                self.rect = Rectangle(size=self.root.size, pos=self.root.pos)
            self.root.bind(size=self._update_rect, pos=self._update_rect)
            # actualizar color usuario
            for u in self.usuarios:
                if u["alias"] == self.alias_actual:
                    u["color"] = color
                    break
            self.guardar_usuarios()
            popup.dismiss()

        btn_aplicar.bind(on_press=aplicar_color)
        popup.open()

    def cerrar_sesion(self, instance):
        if os.path.exists(SESION_FILE):
            os.remove(SESION_FILE)
        self.avisos = []
        self.usuario_actual = None
        self.alias_actual = None
        self.usuario_premium = False
        self.color_fondo = COLOR_NOMBRES["blanco"]
        self.color_texto = self.calcular_color_texto(self.color_fondo)
        self.root.canvas.before.clear()
        with self.root.canvas.before:
            Color(*self.color_fondo)
            self.rect = Rectangle(size=self.root.size, pos=self.root.pos)
        self.root.bind(size=self._update_rect, pos=self._update_rect)
        self.mostrar_login()

    def mostrar_popup(self, titulo, mensaje):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(text=mensaje))
        btn_cerrar = Button(text="Cerrar", size_hint=(1, 0.3))
        content.add_widget(btn_cerrar)
        popup = Popup(title=titulo, content=content, size_hint=(0.8, 0.4))
        btn_cerrar.bind(on_press=popup.dismiss)
        popup.open()

    def eliminar_aviso(self, idx):
        del self.avisos[idx]
        self.guardar_avisos()
        self.mostrar_lista_avisos(self.avisos)

if __name__ == "__main__":
    AvisosApp().run()
