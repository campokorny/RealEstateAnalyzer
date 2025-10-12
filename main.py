from models.property_models import Property, Income, Expense
from services.db import create_tables, insert_property, fetch_all_properties

def main():
    create_tables()

    income = Income(rent_income=2000, laundry_income=100, other_income=0)
    expenses = Expense(
        tax_expense=300, insurance_expense=100, electric_expense=50,
        water_sewer_expense=50, garbage_expense=30, gas_expense=40,
        hoa_expense=0, lawn_care_expense=60, snow_removal_expense=0,
        vacancy_rate=0.05, repairs=100, capEx=100, property_management=150,
        mortgage=900, other_expense=0
    )

    prop = Property(
        address="123 Main St",
        purchase_price=250000,
        down_payment=50000,
        loan_interest_rate=0.07,
        loan_years=30,
        income=income,
        expenses=expenses
    )

    insert_property(prop)

    print("\nProperties in database:")
    for p in fetch_all_properties():
        print(f"{p.address} — Rent: ${p.income.rent_income}, Taxes: ${p.expenses.tax_expense}")

if __name__ == "__main__":
    main()
