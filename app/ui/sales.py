import flet as ft
from flet import (
    Column,
    Row,
    Text,
    TextField,
    ElevatedButton,
    ListView,
    Divider,
    icons,
    Colors as colors
)
from sqlalchemy.orm import Session
from app.db import engine
from app.models import Product, Sale, SaleItem

class Sales(ft.Column):
    """UI para registrar una venta mediante escaneo de código de barras."""

    def __init__(self, page: ft.Page):
        super().__init__()
        self.main_page = page
        self.barcode_input = ft.TextField(label="Escanear código de barras", width=300, on_submit=self._add_to_cart)
        self.cart = []  # lista de dicts: {"product": Product, "qty": int}
        self.cart_view = ft.ListView(expand=True, spacing=5)
        self.total_text = ft.Text("$0.00", size=24, weight=ft.FontWeight.BOLD, color=colors.GREEN)
        
        self.controls = [self._build_content()]
        self.spacing = 12
        self.scroll = ft.ScrollMode.AUTO

    # ------------------------------------------------------------------
    # Callbacks
    # ------------------------------------------------------------------
    def _add_to_cart(self, e):
        code = self.barcode_input.value.strip()
        if not code:
            return
        with Session(engine) as db:
            product = db.query(Product).filter(Product.barcode == code).first()
            if not product:
                pass
            else:
                db.expunge(product)

        if not product:
            self.main_page.snack_bar = ft.SnackBar(ft.Text("Producto no encontrado"))
            self.main_page.snack_bar.open = True
            self.main_page.update()
            self.barcode_input.value = ""
            self.barcode_input.update()
            return

        for item in self.cart:
            if item["product"].id == product.id:
                item["qty"] += 1
                break
        else:
            self.cart.append({"product": product, "qty": 1})

        self._refresh_cart()
        self.barcode_input.value = ""
        self.barcode_input.focus()
        self.barcode_input.update()

    def _refresh_cart(self):
        self.cart_view.controls.clear()
        total = 0.0
        for item in self.cart:
            line_total = item["product"].price * item["qty"]
            total += line_total
            self.cart_view.controls.append(
                ft.Row(
                    [
                        ft.Text(item["product"].name, width=200),
                        ft.Text(f"x{item['qty']}", width=30),
                        ft.Text(f"${line_total:,.2f}", width=80),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                )
            )
        self.total_text.value = f"${total:,.2f}"
        self.update()

    def _finalize_sale(self, e):
        if not self.cart:
            self.main_page.snack_bar = ft.SnackBar(ft.Text("El carrito está vacío"))
            self.main_page.snack_bar.open = True
            self.main_page.update()
            return

        with Session(engine) as db:
            sale = Sale(
                total_amount=sum(item["product"].price * item["qty"] for item in self.cart),
            )
            db.add(sale)
            db.flush()

            for item in self.cart:
                sale_item = SaleItem(
                    sale_id=sale.id,
                    product_id=item["product"].id,
                    quantity=item["qty"],
                    line_total=item["product"].price * item["qty"],
                )
                db.add(sale_item)

            db.commit()

        self.cart.clear()
        self._refresh_cart()
        self.main_page.snack_bar = ft.SnackBar(ft.Text("Venta registrada"))
        self.main_page.snack_bar.open = True
        self.main_page.update()

    # ------------------------------------------------------------------
    # UI building
    # ------------------------------------------------------------------
    def _build_content(self):
        finalize_btn = ft.ElevatedButton("Finalizar venta", icon="check", on_click=self._finalize_sale)
        return ft.Column(
            [
                ft.Text("Ventas – Registro de ventas", size=24, weight=ft.FontWeight.BOLD),
                self.barcode_input,
                ft.Divider(),
                ft.Text("Carrito:", weight=ft.FontWeight.BOLD),
                self.cart_view,
                ft.Row([ft.Text("Total:", weight=ft.FontWeight.BOLD), self.total_text]),
                finalize_btn,
            ],
            spacing=12,
        )
