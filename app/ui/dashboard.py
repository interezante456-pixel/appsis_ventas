import flet as ft
from flet import Column, Row, Text, Container, alignment, Colors as colors
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..db import engine
from ..models import Product, Sale

class Dashboard(ft.Column):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.main_page = page
        self.total_sales = ft.Text("0", size=32, weight=ft.FontWeight.BOLD, color=colors.WHITE)
        self.total_products = ft.Text("0", size=32, weight=ft.FontWeight.BOLD, color=colors.WHITE)
        self.recent_sales = ft.ListView(expand=True, spacing=5)
        
        self.controls = [self._build_content()]
        self.spacing = 20
        self.alignment = ft.MainAxisAlignment.START
        self.controls = [self._build_content()]
        self.spacing = 20
        self.alignment = ft.MainAxisAlignment.START

    def did_mount(self):
        self.load_data()

    def _build_content(self):
        # Card style with gradient background
        card_style = {
            "bgcolor": ft.LinearGradient(
                begin=ft.Alignment(-1, -1),
                end=ft.Alignment(1, 1),
                colors=["#4A90E2", "#9013FE"],
            ),
            "border_radius": 12,
            "padding": 16,
            "margin": 8,
        }
        sales_card = Container(
            content=Column([
                Text("Ventas Totales", size=20, color=colors.WHITE),
                self.total_sales,
            ]),
            **card_style,
        )
        products_card = Container(
            content=Column([
                Text("Productos Registrados", size=20, color=colors.WHITE),
                self.total_products,
            ]),
            **card_style,
        )
        recent_card = Container(
            content=Column([
                Text("Ventas Recientes", size=20, color=colors.WHITE),
                self.recent_sales,
            ]),
            **card_style,
            height=300,
        )
        return Column([
            Row([sales_card, products_card], alignment=ft.MainAxisAlignment.SPACE_EVENLY),
            recent_card,
        ], spacing=20, alignment=ft.MainAxisAlignment.START)

    def load_data(self):
        with Session(engine) as db:
            total = db.query(func.sum(Sale.total_amount)).scalar() or 0
            self.total_sales.value = f"${total:,.2f}"
            prod_count = db.query(Product).count()
            self.total_products.value = str(prod_count)
            recent = db.query(Sale).order_by(Sale.timestamp.desc()).limit(5).all()
            self.recent_sales.controls.clear()
            for s in recent:
                self.recent_sales.controls.append(
                    Row([
                        Text(f"#{s.id}"),
                        Text(f"{s.total_amount:.2f}$"),
                        Text(s.timestamp.strftime('%Y-%m-%d %H:%M')),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                )
        self.update()
