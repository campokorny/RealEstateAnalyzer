import sqlite3
from pathlib import Path
from models.property_models import Property, Income, Expense

DB_PATH = Path(__file__).parent.parent / "data" / "real_estate.db"

def delete_property(address: str):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM properties WHERE address = ?", (address,))
    conn.commit()
    conn.close()

def update_property_in_db(prop: Property):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        UPDATE properties SET
            purchase_price=?, down_payment=?, loan_interest_rate=?, loan_years=?,
            rent_income=?, laundry_income=?, other_income=?,
            tax_expense=?, insurance_expense=?, electric_expense=?, water_sewer_expense=?,
            garbage_expense=?, gas_expense=?, hoa_expense=?, lawn_care_expense=?, snow_removal_expense=?,
            vacancy_rate=?, repairs=?, capEx=?, property_management=?, mortgage=?, other_expense=?
        WHERE address=?
    """, (
        prop.purchase_price, prop.down_payment, prop.loan_interest_rate, prop.loan_years,
        prop.income.rent_income, prop.income.laundry_income, prop.income.other_income,
        prop.expenses.tax_expense, prop.expenses.insurance_expense, prop.expenses.electric_expense,
        prop.expenses.water_sewer_expense, prop.expenses.garbage_expense, prop.expenses.gas_expense,
        prop.expenses.hoa_expense, prop.expenses.lawn_care_expense, prop.expenses.snow_removal_expense,
        prop.expenses.vacancy_rate, prop.expenses.repairs, prop.expenses.capEx,
        prop.expenses.property_management, prop.expenses.mortgage, prop.expenses.other_expense,
        prop.address
    ))
    conn.commit()
    conn.close()

def get_connection():
    """Return a SQLite connection (auto-creates data folder if needed)."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_PATH)


def create_tables():
    """Create tables for properties, incomes, and expenses."""
    conn = get_connection()
    c = conn.cursor()

    # Properties table
    c.execute("""
        CREATE TABLE IF NOT EXISTS properties (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            address TEXT NOT NULL,
            purchase_price REAL,
            down_payment REAL,
            loan_interest_rate REAL,
            loan_years INTEGER
        );
    """)

    # Income table (1-to-1 per property)
    c.execute("""
        CREATE TABLE IF NOT EXISTS incomes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            property_id INTEGER NOT NULL,
            rent_income REAL,
            laundry_income REAL,
            other_income REAL,
            FOREIGN KEY (property_id) REFERENCES properties (id) ON DELETE CASCADE
        );
    """)

    # Expense table (1-to-1 per property)
    c.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            property_id INTEGER NOT NULL,
            tax_expense REAL,
            insurance_expense REAL,
            electric_expense REAL,
            water_sewer_expense REAL,
            garbage_expense REAL,
            gas_expense REAL,
            hoa_expense REAL,
            lawn_care_expense REAL,
            snow_removal_expense REAL,
            vacancy_rate REAL,
            repairs REAL,
            capEx REAL,
            property_management REAL,
            mortgage REAL,
            other_expense REAL,
            FOREIGN KEY (property_id) REFERENCES properties (id) ON DELETE CASCADE
        );
    """)

    conn.commit()
    conn.close()


def insert_property(property_obj: Property):
    """Insert a Property (and its related income and expenses) into the DB."""
    conn = get_connection()
    c = conn.cursor()

    # Insert property
    c.execute("""
        INSERT INTO properties (address, purchase_price, down_payment, loan_interest_rate, loan_years)
        VALUES (?, ?, ?, ?, ?)
    """, (
        property_obj.address,
        property_obj.purchase_price,
        property_obj.down_payment,
        property_obj.loan_interest_rate,
        property_obj.loan_years
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
            _id, address, purchase_price, down_payment, loan_interest_rate, loan_years,
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
            address=address,
            purchase_price=purchase_price,
            down_payment=down_payment,
            loan_interest_rate=loan_interest_rate,
            loan_years=loan_years,
            income=income,
            expenses=expenses
        )

        properties.append(prop)

    return properties
