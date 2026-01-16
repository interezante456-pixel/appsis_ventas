import flet as ft
from flet import (
    Column,
    Row,
    Text,
    TextField,
    ElevatedButton,
    Dropdown,
    dropdown,
    icons,
    Divider,
)
from sqlalchemy.orm import Session
from app.db import engine
from app.models import User, RoleEnum
import bcrypt

class UsersManagement(ft.Column):
    """UI para crear y listar usuarios con sus roles."""

    def __init__(self, page: ft.Page):
        super().__init__()
        self.main_page = page
        self.username = ft.TextField(label="Usuario", width=300)
        self.password = ft.TextField(label="Contraseña", password=True, width=300)
        self.role = ft.Dropdown(
            label="Rol",
            width=300,
            options=[
                ft.dropdown.Option(RoleEnum.SUPERUSER.value, "Superusuario"),
                ft.dropdown.Option(RoleEnum.ADMIN.value, "Administrador"),
                ft.dropdown.Option(RoleEnum.EMPLOYEE.value, "Empleado"),
            ],
            value=RoleEnum.EMPLOYEE.value,
        )
        self.user_list = ft.Column(spacing=5)
        
        self.controls = [self._build_content()]
        self.spacing = 12
        self.scroll = ft.ScrollMode.AUTO
        self.controls = [self._build_content()]
        self.spacing = 12
        self.scroll = ft.ScrollMode.AUTO

    def did_mount(self):
        self._refresh_user_list()

    # ------------------------------------------------------------------
    # Callbacks
    # ------------------------------------------------------------------
    def _create_user(self, e):
        if not (self.username.value and self.password.value):
            self.main_page.snack_bar = ft.SnackBar(ft.Text("Usuario y contraseña obligatorios"))
            self.main_page.snack_bar.open = True
            self.main_page.update()
            return

        with Session(engine) as db:
            if db.query(User).filter(User.username == self.username.value).first():
                self.main_page.snack_bar = ft.SnackBar(ft.Text("El usuario ya existe"))
                self.main_page.snack_bar.open = True
                self.main_page.update()
                return

            new_user = User(
                username=self.username.value,
                password_hash=bcrypt.hashpw(self.password.value.encode("utf-8"), bcrypt.gensalt()).decode("utf-8"),
                role=self.role.value,
            )
            db.add(new_user)
            db.commit()

        # Limpiar formulario
        self.username.value = ""
        self.password.value = ""
        self.role.value = RoleEnum.EMPLOYEE.value
        self.update()
        self._refresh_user_list()
        self.main_page.snack_bar = ft.SnackBar(ft.Text("Usuario creado"))
        self.main_page.snack_bar.open = True
        self.main_page.update()

    def _refresh_user_list(self):
        with Session(engine) as db:
            users = db.query(User).order_by(User.id).all()
        rows = []
        for u in users:
            rows.append(
                ft.Row(
                    [
                        ft.Text(u.username, width=200),
                        ft.Text(u.role.value, width=120),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                )
            )
        self.user_list.controls = rows
        self.update()

    # ------------------------------------------------------------------
    # UI building
    # ------------------------------------------------------------------
    def _build_content(self):
        create_btn = ft.ElevatedButton("Crear usuario", on_click=self._create_user, icon="add")
        
        return ft.Column(
            [
                ft.Text("Gestión de usuarios", size=24, weight=ft.FontWeight.BOLD),
                ft.Row([self.username, self.password]),
                self.role,
                create_btn,
                ft.Divider(),
                ft.Text("Lista de usuarios:", weight=ft.FontWeight.BOLD),
                self.user_list,
            ],
            spacing=12,
        )
