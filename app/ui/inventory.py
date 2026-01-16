import flet as ft
from flet import (
    Column,
    Row,
    Text,
    TextField,
    ElevatedButton,
    Image,
    FilePicker,
    Dropdown,
    dropdown,
    icons,
    Container,
    alignment,
    padding,
    Colors as colors
)
from sqlalchemy.orm import Session
from app.db import engine
from app.models import Product

class Inventory(ft.Column):
    """UI para registrar productos en el inventario."""

    def __init__(self, page: ft.Page):
        super().__init__()
        self.main_page = page
        self.barcode = ft.TextField(label="Código de barras", width=300)
        self.name = ft.TextField(label="Nombre", width=300)
        self.description = ft.TextField(label="Descripción", width=300, multiline=True)
        self.price = ft.TextField(label="Precio", width=300, keyboard_type=ft.KeyboardType.NUMBER)
        self.image_path = ""
        self.image_preview = ft.Image(src="https://placehold.co/200", width=200, height=200, fit="contain", visible=False)
        self.file_picker = ft.FilePicker()
        self.file_picker.on_result = self._on_file_selected
        
        form_content = self._build_content()
        self.controls = [form_content]
        self.spacing = 12
        self.scroll = ft.ScrollMode.AUTO

    def did_mount(self):
        # self.main_page.overlay.append(self.file_picker)
        # self.main_page.update()
        pass

    def _on_file_selected(self, e):
        # ... logic disabled ...
        if e.files:
            self.image_path = e.files[0].path
            self.image_preview.src = self.image_path
            self.image_preview.visible = True
            self.image_preview.update()

    def _build_content(self):
        add_btn = ft.ElevatedButton("Agregar producto", on_click=self._add_product)

        return ft.Column(
            [
                ft.Text("Inventario – Registro de productos", size=24, weight=ft.FontWeight.BOLD),
                ft.Row([self.barcode, self.name]),
                self.description,
                ft.Row([self.price, ft.ElevatedButton("Subir Foto", icon="add_a_photo", on_click=lambda _: self.page.snack_bar.open or print("Picker disabled"))]),
                self.image_preview,
                add_btn,
                ft.Divider(),
                ft.Text("Productos registrados:", weight=ft.FontWeight.BOLD),
                self._product_list(),
            ],
            spacing=12,
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _product_list(self):
        """Muestra una lista simple de los productos ya guardados."""
        with Session(engine) as db:
            products = db.query(Product).order_by(Product.id.desc()).limit(10).all()
        rows = []
        for p in products:
            rows.append(
                ft.Row(
                    [
                        ft.Text(p.barcode, width=120),
                        ft.Text(p.name, width=200),
                        ft.Text(f"${p.price:,.2f}", width=80),
                        ft.Image(src=p.image_path or "", width=60, height=60, fit="contain"),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                )
            )
        return ft.Column(rows, spacing=5)

    def _add_product(self, e):
        """Guarda el producto en la base de datos."""
        # Validación básica
        if not (self.barcode.value and self.name.value and self.price.value):
            self.main_page.snack_bar = ft.SnackBar(ft.Text("Faltan campos obligatorios"))
            self.main_page.snack_bar.open = True
            self.main_page.update()
            return

        try:
            price_val = float(self.price.value)
        except ValueError:
            self.main_page.snack_bar = ft.SnackBar(ft.Text("Precio debe ser numérico"))
            self.main_page.snack_bar.open = True
            self.main_page.update()
            return

        with Session(engine) as db:
            # Evitar duplicados de código de barras
            if db.query(Product).filter(Product.barcode == self.barcode.value).first():
                self.main_page.snack_bar = ft.SnackBar(ft.Text("Código de barras ya registrado"))
                self.main_page.snack_bar.open = True
                self.main_page.update()
                return

            new_product = Product(
                barcode=self.barcode.value,
                name=self.name.value,
                description=self.description.value,
                price=price_val,
                image_path=self.image_path,
            )
            db.add(new_product)
            db.commit()

        # Limpiar formulario
        self.barcode.value = ""
        self.name.value = ""
        self.description.value = ""
        self.price.value = ""
        self.image_path = ""
        self.image_preview.src = ""
        self.update()
        self.main_page.snack_bar = ft.SnackBar(ft.Text("Producto guardado"))
        self.main_page.snack_bar.open = True
        self.main_page.update()
