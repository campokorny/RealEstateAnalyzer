from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class Property(Base):
    __tablename__ = "properties"

    id = Column(Integer, primary_key=True)
    address = Column(String, nullable=False)
    purchase_price = Column(Float)
    down_payment = Column(Float)
    loan_interest_rate = Column(Float)
    loan_years = Column(Integer)
    is_portfolio_property = Column(Boolean, default=False)
    # financing_type: TEXT
    # property_type: TEXT

    # Relationships
    income = relationship("Income", uselist=False, back_populates="property", cascade="all, delete-orphan")
    expenses = relationship("Expense", uselist=False, back_populates="property", cascade="all, delete-orphan")


class Income(Base):
    __tablename__ = "incomes"

    id = Column(Integer, primary_key=True)
    property_id = Column(Integer, ForeignKey("properties.id"))
    rent_income = Column(Float, default=0)
    laundry_income = Column(Float, default=0)
    other_income = Column(Float, default=0)

    property = relationship("Property", back_populates="income")


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True)
    property_id = Column(Integer, ForeignKey("properties.id"))
    tax_expense = Column(Float, default=0)
    insurance_expense = Column(Float, default=0)
    electric_expense = Column(Float, default=0)
    water_sewer_expense = Column(Float, default=0)
    garbage_expense= Column(Float, default=0)
    gas_expense= Column(Float, default=0)
    hoa_expense= Column(Float, default=0)
    lawn_care_expense= Column(Float, default=0)
    snow_removal_expense= Column(Float, default=0)
    vacancy_rate= Column(Float, default=0)
    repairs= Column(Float, default=0)
    capEx= Column(Float, default=0)
    property_management= Column(Float, default=0)
    mortgage= Column(Float, default=0)
    other_expense= Column(Float, default=0)

    property = relationship("Property", back_populates="expenses")
