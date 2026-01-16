import enum
import os
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from .db import Base

class RoleEnum(str, enum.Enum):
    SUPERUSER = "superuser"
    ADMIN = "admin"
    EMPLOYEE = "employee"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    role = Column(Enum(RoleEnum), default=RoleEnum.EMPLOYEE, nullable=False)

    def __repr__(self):
        return f"<User {self.username} ({self.role})>"

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    barcode = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    price = Column(Float, nullable=False)
    image_path = Column(String, nullable=True)  # local path to image file

    def __repr__(self):
        return f"<Product {self.name} [{self.barcode}]>"

class Sale(Base):
    __tablename__ = "sales"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    timestamp = Column(DateTime, default=datetime.utcnow)
    total_amount = Column(Float, nullable=False)

    user = relationship('User')
    items = relationship('SaleItem', back_populates='sale')

    def __repr__(self):
        return f"<Sale {self.id} by {self.user_id} @ {self.timestamp}>"

class SaleItem(Base):
    __tablename__ = "sale_items"
    id = Column(Integer, primary_key=True, index=True)
    sale_id = Column(Integer, ForeignKey('sales.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    quantity = Column(Integer, default=1)
    line_total = Column(Float, nullable=False)

    sale = relationship('Sale', back_populates='items')
    product = relationship('Product')

    def __repr__(self):
        return f"<SaleItem {self.product_id} x{self.quantity}>"
