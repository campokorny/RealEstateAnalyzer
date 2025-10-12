import streamlit as st

from models.property_models import Income, Expense, Property
from services.db import insert_property

st.title("➕ Add a New Property")

with st.form("property_form"):
    address = st.text_input("Address")
    purchase_price = st.number_input("Purchase Price", min_value=0.0)
    down_payment = st.number_input("Down Payment", min_value=0.0)
    loan_interest_rate = st.number_input("Loan Interest Rate (%)", min_value=0.0)
    loan_years = st.number_input("Loan Term (years)", min_value=1, max_value=40)

    st.subheader("Income (Monthly)")
    rent_income = st.number_input("Rent", min_value=0.0)
    laundry_income = st.number_input("Laundry", min_value=0.0)
    other_income = st.number_input("Other Income", min_value=0.0)

    st.subheader("Expenses (Monthly)")
    tax_expense = st.number_input("Property Taxes", min_value=0.0)
    insurance_expense = st.number_input("Insurance", min_value=0.0)
    electric_expense = st.number_input("Electric", min_value=0.0)
    water_sewer_expense = st.number_input("Water/Sewer", min_value=0.0)
    garbage_expense = st.number_input("Garbage", min_value=0.0)
    gas_expense = st.number_input("Gas", min_value=0.0)
    hoa_expense = st.number_input("HOA", min_value=0.0)
    lawn_care_expense = st.number_input("Lawn Care", min_value=0.0)
    snow_removal_expense = st.number_input("Snow Removal", min_value=0.0)
    vacancy_rate = st.number_input("Vacancy Rate (0-1)", min_value=0.0, max_value=1.0, step=0.01)
    repairs = st.number_input("Repairs", min_value=0.0)
    capEx = st.number_input("Capital Expenditures", min_value=0.0)
    property_management = st.number_input("Property Management", min_value=0.0)
    mortgage = st.number_input("Mortgage", min_value=0.0)
    other_expense = st.number_input("Other", min_value=0.0)

    submitted = st.form_submit_button("💾 Save Property")

    if submitted and address:
        income = Income(rent_income, laundry_income, other_income)
        expenses = Expense(
            tax_expense, insurance_expense, electric_expense, water_sewer_expense,
            garbage_expense, gas_expense, hoa_expense, lawn_care_expense, snow_removal_expense,
            vacancy_rate, repairs, capEx, property_management, mortgage, other_expense
        )
        prop = Property(
            address, purchase_price, down_payment,
            loan_interest_rate / 100, loan_years, income, expenses
        )
        insert_property(prop)
        st.success(f"✅ {address} added successfully!")

