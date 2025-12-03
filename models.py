from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

class Tutor(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    address: Mapped[str] = mapped_column(String(200), nullable=True)
    pets = relationship("Pet", back_populates="tutor")
    sales = relationship("Sale", back_populates="tutor")

class Pet(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    breed: Mapped[str] = mapped_column(String(100), nullable=True)
    age: Mapped[int] = mapped_column(Integer, nullable=True)
    tutor_id: Mapped[int] = mapped_column(ForeignKey("tutor.id"))
    tutor = relationship("Tutor", back_populates="pets")
    appointments = relationship("Appointment", back_populates="pet")

class Appointment(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    date_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    service: Mapped[str] = mapped_column(String(100), nullable=False) # Banho, Tosa, etc.
    status: Mapped[str] = mapped_column(String(20), default="Scheduled") # Scheduled, Completed, Canceled
    pet_id: Mapped[int] = mapped_column(ForeignKey("pet.id"))
    pet = relationship("Pet", back_populates="appointments")

class Product(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    sales = relationship("Sale", back_populates="product")

class Sale(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    total: Mapped[float] = mapped_column(Float, nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("product.id"))
    tutor_id: Mapped[int] = mapped_column(ForeignKey("tutor.id"), nullable=True) # Can be anonymous
    product = relationship("Product", back_populates="sales")
    tutor = relationship("Tutor", back_populates="sales")
