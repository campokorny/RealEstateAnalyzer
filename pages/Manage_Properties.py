import streamlit as st
from services.db import fetch_all_properties, delete_property, update_property_in_db
from models.property_models import Property, Income, Expense

st.subheader("⚙️ Manage Properties")

props = fetch_all_properties()
if props:
    prop_map = {p.address: p for p in props} # creates a map where the key is address and the value is Property object
    selected_address = st.selectbox("Select a property", list(prop_map.keys())) # lists addresses as dropdown options
    prop = prop_map[selected_address]

    # --- Edit form ---
    with st.form("edit_property_form"):
        st.write("Edit property details below:")

        # Basic info
        purchase_price = st.number_input("Purchase Price", value=prop.purchase_price, min_value=0.0)
        down_payment = st.number_input("Down Payment", value=prop.down_payment, min_value=0.0)
        loan_interest_rate = st.number_input("Loan Interest Rate (%)", value=prop.loan_interest_rate * 100)
        loan_years = st.number_input("Loan Term (years)", value=prop.loan_years, min_value=0, max_value=40)

        # Income
        rent_income = st.number_input("Rent Income", value=prop.income.rent_income)
        laundry_income = st.number_input("Laundry Income", value=prop.income.laundry_income)
        other_income = st.number_input("Other Income", value=prop.income.other_income)

        # Expenses
        tax_expense = st.number_input("Property Taxes", value=prop.expenses.tax_expense)
        insurance_expense = st.number_input("Insurance", value=prop.expenses.insurance_expense)
        electric_expense = st.number_input("Electric", value=prop.expenses.electric_expense)
        water_sewer_expense = st.number_input("Water/Sewer", value=prop.expenses.water_sewer_expense)
        garbage_expense = st.number_input("Garbage", value=prop.expenses.garbage_expense)
        gas_expense = st.number_input("Gas", value=prop.expenses.gas_expense)
        hoa_expense = st.number_input("HOA", value=prop.expenses.hoa_expense)
        lawn_care_expense = st.number_input("Lawn Care", value=prop.expenses.lawn_care_expense)
        snow_removal_expense = st.number_input("Snow Removal", value=prop.expenses.snow_removal_expense)
        vacancy_rate = st.number_input("Vacancy Rate (0-1)", value=prop.expenses.vacancy_rate, min_value=0.0,
                                       max_value=1.0, step=0.01)
        repairs = st.number_input("Repairs", value=prop.expenses.repairs)
        capEx = st.number_input("Capital Expenditures", value=prop.expenses.capEx)
        property_management = st.number_input("Property Management", value=prop.expenses.property_management)
        mortgage = st.number_input("Mortgage", value=prop.expenses.mortgage)
        other_expense = st.number_input("Other Expense", value=prop.expenses.other_expense)

        # Submit button
        submitted = st.form_submit_button("💾 Save Changes")
        if submitted:
            # Build updated Property object
            updated_income = Income(rent_income, laundry_income, other_income)
            updated_expenses = Expense(
                tax_expense, insurance_expense, electric_expense, water_sewer_expense,
                garbage_expense, gas_expense, hoa_expense, lawn_care_expense, snow_removal_expense,
                vacancy_rate, repairs, capEx, property_management, mortgage, other_expense
            )
            updated_property = Property(
                prop.id, prop.address, purchase_price, down_payment,
                loan_interest_rate / 100, loan_years, updated_income, updated_expenses
            )

            # Update in database
            update_property_in_db(updated_property)
            st.success(f"✅ {prop.address} updated successfully!")
            st.experimental_rerun()  # Refresh page to show updated values

    # --- Delete button ---
    if st.button("🗑️ Delete Selected Property"):
        delete_property(selected_address)
        st.warning(f"{selected_address} deleted.")
        st.experimental_rerun()

else:
    st.info("No properties available to manage.")
