import sqlite3
from pathlib import Path
from models.property_models import Property, Income, Expense
from services.schema import PROPERTY_FIELDS, INCOME_FIELDS, EXPENSE_FIELDS

DB_PATH = Path(__file__).parent.parent / "data" / "real_estate.db"

def delete_property(property_id: int):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM properties WHERE id = ?", (property_id,))
    conn.commit()
    conn.close()

def update_property_in_db(prop: Property):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        UPDATE properties SET
            purchase_price=?, down_payment=?, loan_interest_rate=?, loan_years=?, is_portfolio_property=?
        WHERE id=?
    """, (
        prop.purchase_price, prop.down_payment, prop.loan_interest_rate, prop.loan_years,
        prop.is_portfolio_property, prop.id
    ))

    c.execute("""
            UPDATE incomes SET
                rent_income=?, laundry_income=?, other_income=?
            WHERE id=?
        """, (
        prop.income.rent_income, prop.income.laundry_income, prop.income.other_income,
        prop.id
    ))

    c.execute("""
            UPDATE expenses SET
            tax_expense=?, insurance_expense=?, electric_expense=?, water_sewer_expense=?,
            garbage_expense=?, gas_expense=?, hoa_expense=?, lawn_care_expense=?, snow_removal_expense=?,
            vacancy_rate=?, repairs=?, capEx=?, property_management=?, mortgage=?, other_expense=?
            WHERE id=?
        """, (
        prop.expenses.tax_expense, prop.expenses.insurance_expense, prop.expenses.electric_expense,
        prop.expenses.water_sewer_expense, prop.expenses.garbage_expense, prop.expenses.gas_expense,
        prop.expenses.hoa_expense, prop.expenses.lawn_care_expense, prop.expenses.snow_removal_expense,
        prop.expenses.vacancy_rate, prop.expenses.repairs, prop.expenses.capEx,
        prop.expenses.property_management, prop.expenses.mortgage, prop.expenses.other_expense,
        prop.id
    ))

    conn.commit()
    conn.close()

def get_connection():
    """Return a SQLite connection (auto-creates data folder if needed)."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_PATH)

def create_table(conn, table_name: str, fields: dict):
    columns = ", ".join([f"{col} {dtype}" for col, dtype in fields.items()])
    conn.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({columns});")
    conn.commit()

def create_tables():
    """Create tables for properties, incomes, and expenses."""
    with get_connection() as conn:
        create_table(conn, "properties", PROPERTY_FIELDS)
        create_table(conn, "incomes", INCOME_FIELDS)
        create_table(conn, "expenses", EXPENSE_FIELDS)


def insert_property(property_obj: Property):
    """Insert a Property (and its related income and expenses) into the DB."""
    conn = get_connection()
    c = conn.cursor()

    # Insert property
    c.execute("""
        INSERT INTO properties (address, purchase_price, down_payment, loan_interest_rate, loan_years, 
        is_portfolio_property)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        property_obj.address,
        property_obj.purchase_price,
        property_obj.down_payment,
        property_obj.loan_interest_rate,
        property_obj.loan_years,
        property_obj.is_portfolio_property
    ))

    property_id = c.lastrowid

    # Insert income
    income = property_obj.income
    c.execute("""
        INSERT INTO incomes (property_id, rent_income, laundry_income, other_income)
        VALUES (?, ?, ?, ?)
    """, (
        property_id,
        income.rent_income,
        income.laundry_income,
        income.other_income
    ))

    # Insert expenses
    exp = property_obj.expenses
    c.execute("""
        INSERT INTO expenses (
            property_id, tax_expense, insurance_expense, electric_expense, water_sewer_expense,
            garbage_expense, gas_expense, hoa_expense, lawn_care_expense, snow_removal_expense,
            vacancy_rate, repairs, capEx, property_management, mortgage, other_expense
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        property_id,
        exp.tax_expense,
        exp.insurance_expense,
        exp.electric_expense,
        exp.water_sewer_expense,
        exp.garbage_expense,
        exp.gas_expense,
        exp.hoa_expense,
        exp.lawn_care_expense,
        exp.snow_removal_expense,
        exp.vacancy_rate,
        exp.repairs,
        exp.capEx,
        exp.property_management,
        exp.mortgage,
        exp.other_expense
    ))

    conn.commit()
    conn.close()
    print(f"✅ Property '{property_obj.address}' saved to database.")


def fetch_all_properties():
    """Return all properties as Property objects (with nested Income and Expense)."""
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        SELECT 
            p.id, p.address, p.purchase_price, p.down_payment, p.loan_interest_rate, p.loan_years, 
            p.is_portfolio_property,
            i.rent_income, i.laundry_income, i.other_income,
            e.tax_expense, e.insurance_expense, e.electric_expense, e.water_sewer_expense,
            e.garbage_expense, e.gas_expense, e.hoa_expense, e.lawn_care_expense,
            e.snow_removal_expense, e.vacancy_rate, e.repairs, e.capEx,
            e.property_management, e.mortgage, e.other_expense
        FROM properties p
        JOIN incomes i ON p.id = i.property_id
        JOIN expenses e ON p.id = e.property_id
        ORDER BY p.id;
    """)

    rows = c.fetchall()
    conn.close()

    properties = []
    for row in rows:
        (
            _id, address, purchase_price, down_payment, loan_interest_rate, loan_years, is_portfolio_property,
            rent_income, laundry_income, other_income,
            tax_expense, insurance_expense, electric_expense, water_sewer_expense,
            garbage_expense, gas_expense, hoa_expense, lawn_care_expense,
            snow_removal_expense, vacancy_rate, repairs, capEx,
            property_management, mortgage, other_expense
        ) = row

        income = Income(
            rent_income=rent_income,
            laundry_income=laundry_income,
            other_income=other_income
        )

        expenses = Expense(
            tax_expense=tax_expense,
            insurance_expense=insurance_expense,
            electric_expense=electric_expense,
            water_sewer_expense=water_sewer_expense,
            garbage_expense=garbage_expense,
            gas_expense=gas_expense,
            hoa_expense=hoa_expense,
            lawn_care_expense=lawn_care_expense,
            snow_removal_expense=snow_removal_expense,
            vacancy_rate=vacancy_rate,
            repairs=repairs,
            capEx=capEx,
            property_management=property_management,
            mortgage=mortgage,
            other_expense=other_expense
        )

        prop = Property(
            id = _id,
            address=address,
            purchase_price=purchase_price,
            down_payment=down_payment,
            loan_interest_rate=loan_interest_rate,
            loan_years=loan_years,
            is_portfolio_property=is_portfolio_property,
            income=income,
            expenses=expenses
        )

        properties.append(prop)

    return properties


def fetch_portfolio_properties():
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT 
            p.id, p.address, p.purchase_price, p.down_payment, p.loan_interest_rate, p.loan_years, 
            p.is_portfolio_property,
            i.rent_income, i.laundry_income, i.other_income,
            e.tax_expense, e.insurance_expense, e.electric_expense, e.water_sewer_expense,
            e.garbage_expense, e.gas_expense, e.hoa_expense, e.lawn_care_expense,
            e.snow_removal_expense, e.vacancy_rate, e.repairs, e.capEx,
            e.property_management, e.mortgage, e.other_expense
        FROM properties p
        JOIN incomes i ON p.id = i.property_id
        JOIN expenses e ON p.id = e.property_id
        WHERE p.is_portfolio_property = 1
        ORDER BY p.id;
    """)
    rows = c.fetchall()
    conn.close()

    properties = []
    for row in rows:
        (
            _id, address, purchase_price, down_payment, loan_interest_rate, loan_years, is_portfolio_property,
            rent_income, laundry_income, other_income,
            tax_expense, insurance_expense, electric_expense, water_sewer_expense,
            garbage_expense, gas_expense, hoa_expense, lawn_care_expense,
            snow_removal_expense, vacancy_rate, repairs, capEx,
            property_management, mortgage, other_expense
        ) = row

        income = Income(
            rent_income=rent_income,
            laundry_income=laundry_income,
            other_income=other_income
        )

        expenses = Expense(
            tax_expense=tax_expense,
            insurance_expense=insurance_expense,
            electric_expense=electric_expense,
            water_sewer_expense=water_sewer_expense,
            garbage_expense=garbage_expense,
            gas_expense=gas_expense,
            hoa_expense=hoa_expense,
            lawn_care_expense=lawn_care_expense,
            snow_removal_expense=snow_removal_expense,
            vacancy_rate=vacancy_rate,
            repairs=repairs,
            capEx=capEx,
            property_management=property_management,
            mortgage=mortgage,
            other_expense=other_expense
        )

        prop = Property(
            id=_id,
            address=address,
            purchase_price=purchase_price,
            down_payment=down_payment,
            loan_interest_rate=loan_interest_rate,
            loan_years=loan_years,
            is_portfolio_property=is_portfolio_property,
            income=income,
            expenses=expenses
        )

        properties.append(prop)

    return properties


