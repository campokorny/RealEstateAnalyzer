from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, joinedload

from models.property_models import Base, Property, Income, Expense

# ---------- Database Setup ----------
DB_PATH = Path(__file__).parent.parent / "data" / "real_estate.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

DATABASE_URL = f"sqlite:///{DB_PATH}"
engine = create_engine(DATABASE_URL, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

# Create tables if they don't exist
Base.metadata.create_all(engine)


# ---------- CRUD Operations ----------

def get_session() -> Session:
    """Return a new SQLAlchemy session."""
    return SessionLocal()


def insert_property(property_obj: Property):
    """Insert a Property (and related income & expenses) using ORM."""
    with get_session() as session:
        session.add(property_obj)
        session.commit()
        print(f"✅ Property '{property_obj.address}' saved to database.")


def update_property_in_db(prop: Property):
    """Update an existing property and its relationships."""
    with get_session() as session:
        existing = session.query(Property).filter(Property.id == prop.id).first()
        if not existing:
            raise ValueError(f"Property with ID {prop.id} not found.")

        # --- Update property fields ---
        existing.address = prop.address
        existing.purchase_price = prop.purchase_price
        existing.down_payment = prop.down_payment
        existing.loan_interest_rate = prop.loan_interest_rate
        existing.loan_years = prop.loan_years
        existing.is_portfolio_property = prop.is_portfolio_property

        # --- Update or create Income ---
        if existing.income:
            existing.income.rent_income = prop.income.rent_income
            existing.income.laundry_income = prop.income.laundry_income
            existing.income.other_income = prop.income.other_income
        else:
            existing.income = Income(
                rent_income=prop.income.rent_income,
                laundry_income=prop.income.laundry_income,
                other_income=prop.income.other_income,
            )

        # --- Update or create Expense ---
        if existing.expenses:
            e = existing.expenses
            e.tax_expense = prop.expenses.tax_expense
            e.insurance_expense = prop.expenses.insurance_expense
            e.electric_expense = prop.expenses.electric_expense
            e.water_sewer_expense = prop.expenses.water_sewer_expense
            e.garbage_expense = prop.expenses.garbage_expense
            e.gas_expense = prop.expenses.gas_expense
            e.hoa_expense = prop.expenses.hoa_expense
            e.lawn_care_expense = prop.expenses.lawn_care_expense
            e.snow_removal_expense = prop.expenses.snow_removal_expense
            e.vacancy_rate = prop.expenses.vacancy_rate
            e.repairs = prop.expenses.repairs
            e.capEx = prop.expenses.capEx
            e.property_management = prop.expenses.property_management
            e.mortgage = prop.expenses.mortgage
            e.other_expense = prop.expenses.other_expense
        else:
            existing.expenses = Expense(
                tax_expense=prop.expenses.tax_expense,
                insurance_expense=prop.expenses.insurance_expense,
                electric_expense=prop.expenses.electric_expense,
                water_sewer_expense=prop.expenses.water_sewer_expense,
                garbage_expense=prop.expenses.garbage_expense,
                gas_expense=prop.expenses.gas_expense,
                hoa_expense=prop.expenses.hoa_expense,
                lawn_care_expense=prop.expenses.lawn_care_expense,
                snow_removal_expense=prop.expenses.snow_removal_expense,
                vacancy_rate=prop.expenses.vacancy_rate,
                repairs=prop.expenses.repairs,
                capEx=prop.expenses.capEx,
                property_management=prop.expenses.property_management,
                mortgage=prop.expenses.mortgage,
                other_expense=prop.expenses.other_expense,
            )

        session.commit()
        print(f"✅ Property '{prop.address}' updated successfully.")


def delete_property(property_id: int):
    """Delete a property (and its linked income/expenses)."""
    with get_session() as session:
        prop = session.query(Property).filter(Property.id == property_id).first()
        if not prop:
            raise ValueError(f"Property with ID {property_id} not found.")

        session.delete(prop)
        session.commit()
        print(f"🗑️ Property ID {property_id} deleted.")

def fetch_all_properties():
    session = get_session()
    try:
        properties = (
            session.query(Property)
            .options(
                joinedload(Property.income),
                joinedload(Property.expenses)
            )
            .all()
        )
        return properties
    finally:
        session.close()

def fetch_portfolio_properties():
    session = get_session()
    try:
        properties = (
            session.query(Property)
            .options(
                joinedload(Property.income),
                joinedload(Property.expenses)
            )
            .filter(Property.is_portfolio_property == True)
            .all()
        )
        return properties
    finally:
        session.close()

def create_tables():
    """Ensure all ORM models have corresponding tables."""
    Base.metadata.create_all(engine)
