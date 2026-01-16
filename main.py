import flet as ft
from flet import Page, Text, ElevatedButton, TextField, Row, Column, icons, Image, Divider, ListView, Container, alignment, padding, margin, Colors as colors
import os
# Use absolute package imports (project is a package named 'app')
from app.db import get_db, engine, Base
from app.models import User, Product, Sale, SaleItem, RoleEnum
from sqlalchemy.orm import Session
import bcrypt

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

# Helper functions

def verify_password(plain_password: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed.encode('utf-8'))

def hash_password(plain_password: str) -> str:
    return bcrypt.hashpw(plain_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# UI Components (imported lazily to avoid circular imports)

def get_dashboard(page: Page):
    from app.ui.dashboard import Dashboard
    return Dashboard(page)

def get_inventory(page: Page):
    from app.ui.inventory import Inventory
    return Inventory(page)

def get_sales(page: Page):
    from app.ui.sales import Sales
    return Sales(page)

def get_user_mgmt(page: Page):
    from app.ui.users import UsersManagement
    return UsersManagement(page)

class AppState:
    def __init__(self):
        self.current_user: User | None = None
        self.page: Page | None = None
        self.content: ft.Control | None = None

state = AppState()

def main(page: Page):
    page.title = "Sistema de Ventas"
    page.horizontal_alignment = ft.CrossAxisAlignment.STRETCH
    state.page = page

    def logout(e):
        state.current_user = None
        page.controls.clear()
        page.update()
        page.add(login_view())

    def navigate(section: str):
        # Clear previous content
        if state.content:
            page.controls.remove(state.content)
        if section == "dashboard":
            state.content = get_dashboard(page)
        elif section == "inventory":
            state.content = get_inventory(page)
        elif section == "sales":
            state.content = get_sales(page)
        elif section == "users":
            state.content = get_user_mgmt(page)
        else:
            state.content = ft.Text("Sección no encontrada")
        page.add(state.content)
        page.update()

    def login_view():
        username = ft.TextField(label="Usuario", autofocus=True)
        password = ft.TextField(label="Contraseña", password=True, can_reveal_password=True)
        error_msg = ft.Text("", color=colors.RED)

        def attempt_login(e):
            with Session(engine) as db:
                user = db.query(User).filter(User.username == username.value).first()
                if user and verify_password(password.value, user.password_hash):
                    state.current_user = user
                    page.controls.clear()
                    # Build main layout
                    header = ft.Container(
                        content=ft.Row([
                            ft.Text(f"Bienvenido, {user.username} ({user.role.value})", weight=ft.FontWeight.BOLD),
                            ft.TextButton("Salir", icon="logout", on_click=logout)
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        padding=10
                    )
                    # Navigation bar
                    nav = ft.Container(
                        content=ft.Row([
                            ft.ElevatedButton("Dashboard", on_click=lambda e: navigate('dashboard')),
                            ft.ElevatedButton("Inventario", on_click=lambda e: navigate('inventory')),
                            ft.ElevatedButton("Ventas", on_click=lambda e: navigate('sales')),
                            ft.ElevatedButton("Usuarios", on_click=lambda e: navigate('users')),
                        ], alignment=ft.MainAxisAlignment.SPACE_EVENLY),
                        padding=10
                    )
                    page.add(header, ft.Divider(), nav, ft.Divider())
                    # Default to dashboard
                    navigate('dashboard')
                else:
                    error_msg.value = "Credenciales incorrectas"
                    error_msg.update()

        login_btn = ft.ElevatedButton("Ingresar", on_click=attempt_login)
        return ft.Column([
            ft.Text("Login", size=24, weight=ft.FontWeight.BOLD),
            username,
            password,
            login_btn,
            error_msg,
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10, expand=True)

    # Show login view initially
    page.add(login_view())
    page.update()

ft.app(target=main)
