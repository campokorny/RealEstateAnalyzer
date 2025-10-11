import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from models import Property, Income, Expense
from db import create_tables, insert_property, fetch_all_properties, get_connection

st.set_page_config(page_title="Real Estate Analyzer", layout="wide")
st.title("🏠 Real Estate Investment Analyzer")

create_tables()

# =========================================
# Helper functions
# =========================================
def calculate_metrics(prop: Property):
    """Calculate financial metrics for a given property."""
    income = prop.income
    expenses = prop.expenses

    total_income = income.rent_income + income.laundry_income + income.other_income

    base_expenses = (
        expenses.tax_expense + expenses.insurance_expense + expenses.electric_expense +
        expenses.water_sewer_expense + expenses.garbage_expense + expenses.gas_expense +
        expenses.hoa_expense + expenses.lawn_care_expense + expenses.snow_removal_expense +
        expenses.repairs + expenses.capEx + expenses.property_management +
        expenses.mortgage + expenses.other_expense
    )

    vacancy_loss = total_income * expenses.vacancy_rate
    total_expenses = base_expenses + vacancy_loss

    monthly_cash_flow = total_income - total_expenses
    annual_cash_flow = monthly_cash_flow * 12
    cap_rate = (annual_cash_flow / prop.purchase_price) * 100 if prop.purchase_price else 0
    coc_return = (annual_cash_flow / prop.down_payment) * 100 if prop.down_payment else 0

    return {
        "Total Income": total_income,
        "Total Expenses": total_expenses,
        "Monthly Cash Flow": monthly_cash_flow,
        "Annual Cash Flow": annual_cash_flow,
        "Cap Rate (%)": cap_rate,
        "Cash-on-Cash Return (%)": coc_return
    }


def project_long_term(
    prop: Property,
    years=30,
    appreciation_rate=0.03,
    rent_growth=0.02,
    expense_growth=0.02
):
    """Project property value, cash flow, equity, and loan balance over time."""

    metrics = calculate_metrics(prop)
    value = prop.purchase_price
    rent = prop.income.rent_income
    cash_flow = metrics["Monthly Cash Flow"]

    # --- Mortgage setup ---
    loan_balance = 0
    principal_paid = 0
    interest_paid = 0
    monthly_payment = 0

    if prop.loan_years > 0 and prop.loan_interest_rate > 0:
        loan_balance = prop.purchase_price - prop.down_payment
        monthly_interest_rate = prop.loan_interest_rate / 12
        num_payments = prop.loan_years * 12
        monthly_payment = (
            loan_balance
            * (monthly_interest_rate * (1 + monthly_interest_rate) ** num_payments)
            / ((1 + monthly_interest_rate) ** num_payments - 1)
        )

    projection = []
    cumulative_cash_flow = 0
    equity = prop.down_payment

    for year in range(1, years + 1):
        # --- Growth ---
        value *= (1 + appreciation_rate)
        rent *= (1 + rent_growth)
        cash_flow *= (1 + (rent_growth - expense_growth))
        annual_cf = cash_flow * 12
        cumulative_cash_flow += annual_cf

        # --- Loan amortization ---
        interest_paid_year = 0
        principal_paid_year = 0
        for _ in range(12):  # simulate 12 monthly payments
            if loan_balance > 0:
                interest = loan_balance * (prop.loan_interest_rate / 12)
                principal = monthly_payment - interest
                loan_balance -= principal
                interest_paid_year += interest
                principal_paid_year += principal

        # --- Equity = down payment + principal paid + appreciation gain ---
        equity = prop.down_payment + (prop.purchase_price * ((1 + appreciation_rate) ** year - 1)) + (principal_paid + principal_paid_year)
        principal_paid += principal_paid_year
        interest_paid += interest_paid_year

        projection.append({
            "Year": year,
            "Property Value": value,
            "Annual Cash Flow": annual_cf,
            "Cumulative Cash Flow": cumulative_cash_flow,
            "Equity": equity,
            "Loan Balance": max(loan_balance, 0)
        })

    return pd.DataFrame(projection)


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


# =========================================
# SECTION 1 — Portfolio Overview
# =========================================
with st.expander("📊 Portfolio Overview", expanded=True):
    props = fetch_all_properties()

    if props:
        data = []
        for prop in props:
            metrics = calculate_metrics(prop)
            data.append({"Address": prop.address, **metrics})

        df = pd.DataFrame(data)

        # Summary Metrics
        total_cash_flow = df["Monthly Cash Flow"].sum()
        avg_cap_rate = df["Cap Rate (%)"].mean()
        avg_coc_return = df["Cash-on-Cash Return (%)"].mean()

        col1, col2, col3 = st.columns(3)
        col1.metric("🏦 Total Monthly Cash Flow", f"${total_cash_flow:,.2f}")
        col2.metric("📈 Avg Cap Rate", f"{avg_cap_rate:.2f}%")
        col3.metric("💰 Avg Cash-on-Cash Return", f"{avg_coc_return:.2f}%")

        # Charts
        c1, c2 = st.columns(2)
        with c1:
            fig1 = px.bar(df, x="Address", y="Monthly Cash Flow", title="Monthly Cash Flow by Property", text_auto=".2f")
            st.plotly_chart(fig1, use_container_width=True)
        with c2:
            fig2 = px.bar(df, x="Address", y="Cap Rate (%)", title="Cap Rate by Property", color="Cap Rate (%)", text_auto=".2f")
            st.plotly_chart(fig2, use_container_width=True)

        st.dataframe(df.set_index("Address"), use_container_width=True)

    else:
        st.info("No properties found yet. Add one below!")


# =========================================
# SECTION 2 — Add Property
# =========================================
with st.expander("➕ Add a New Property", expanded=False):
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


# =========================================
# SECTION 3 — Manage Properties
# =========================================
with st.expander("⚙️ Manage Properties", expanded=False):
    props = fetch_all_properties()
    if props:
        selected = st.selectbox("Select a property to delete", [p.address for p in props])
        if st.button("🗑️ Delete Selected Property"):
            delete_property(selected)
            st.warning(f"{selected} deleted.")
            st.rerun()
    else:
        st.info("No properties available to delete.")

# =========================================
# Section 4: In-Depth Property Analysis (with What-If)
# =========================================
with st.expander("🔍 In-Depth Property Analysis", expanded=True):
    props = fetch_all_properties()

    if props:
        selected = st.selectbox("Select property to analyze", [p.address for p in props])
        prop = next(p for p in props if p.address == selected)

        metrics = calculate_metrics(prop)
        st.subheader(f"📄 {prop.address}")
        st.write("Current Metrics:")
        col1, col2, col3 = st.columns(3)
        col1.metric("Monthly Cash Flow", f"${metrics['Monthly Cash Flow']:,.2f}")
        col2.metric("Cap Rate", f"{metrics['Cap Rate (%)']:.2f}%")
        col3.metric("CoC Return", f"{metrics['Cash-on-Cash Return (%)']:.2f}%")

        col1, col2 = st.columns(2)
        with col1:
            st.write("**Purchase Price:**", f"${prop.purchase_price:,.0f}")
            st.write("**Down Payment:**", f"${prop.down_payment:,.0f}")
            st.write("**Loan Term:**", f"{prop.loan_years} years")
            st.write("**Interest Rate:**", f"{prop.loan_interest_rate * 100:.2f}%")
        with col2:
            st.write("**Total Income:**", f"${metrics['Total Income']:.2f}")
            st.write("**Total Expenses:**", f"${metrics['Total Expenses']:.2f}")
            st.write("**Monthly Cash Flow:**", f"${metrics['Monthly Cash Flow']:.2f}")
            st.write("**Cap Rate:**", f"{metrics['Cap Rate (%)']:.2f}%")
            st.write("**Cash-on-Cash Return:**", f"{metrics['Cash-on-Cash Return (%)']:.2f}%")

        # What-If Analysis
        with st.expander("🧮 What-If Analysis (Editable Scenario)", expanded=False):
            st.write("Adjust property data and assumptions below to simulate new outcomes:")

            # Property + Financing
            st.markdown("#### Property & Financing")
            c1, c2, c3, c4 = st.columns(4)
            purchase_price = c1.number_input("Purchase Price", value=prop.purchase_price, min_value=0.0)
            down_payment = c2.number_input("Down Payment", value=prop.down_payment, min_value=0.0)
            use_loan = c3.checkbox("Use Loan?", value=prop.loan_interest_rate > 0)
            loan_interest_rate = c4.number_input("Loan Interest Rate (%)", value=prop.loan_interest_rate * 100 if use_loan else 0.0)
            loan_years = st.number_input("Loan Term (years)", value=prop.loan_years if use_loan else 0, step=1, min_value=0, max_value=40)

            # Income & Expenses
            st.markdown("#### Monthly Income & Expenses")
            income_cols = st.columns(3)
            rent_income = income_cols[0].number_input("Rent", value=prop.income.rent_income)
            laundry_income = income_cols[1].number_input("Laundry", value=prop.income.laundry_income)
            other_income = income_cols[2].number_input("Other Income", value=prop.income.other_income)

            exp_cols = st.columns(3)
            tax_expense = exp_cols[0].number_input("Property Taxes", value=prop.expenses.tax_expense)
            insurance_expense = exp_cols[1].number_input("Insurance", value=prop.expenses.insurance_expense)
            electric_expense = exp_cols[2].number_input("Electric", value=prop.expenses.electric_expense)
            water_sewer_expense = exp_cols[0].number_input("Water/Sewer", value=prop.expenses.water_sewer_expense)
            garbage_expense = exp_cols[1].number_input("Garbage", value=prop.expenses.garbage_expense)
            gas_expense = exp_cols[2].number_input("Gas", value=prop.expenses.gas_expense)
            hoa_expense = exp_cols[0].number_input("HOA", value=prop.expenses.hoa_expense)
            lawn_care_expense = exp_cols[1].number_input("Lawn Care", value=prop.expenses.lawn_care_expense)
            snow_removal_expense = exp_cols[2].number_input("Snow Removal", value=prop.expenses.snow_removal_expense)
            vacancy_rate = st.slider("Vacancy Rate (0-1)", 0.0, 1.0, value=prop.expenses.vacancy_rate, step=0.01)
            repairs = st.number_input("Repairs", value=prop.expenses.repairs)
            capEx = st.number_input("Capital Expenditures", value=prop.expenses.capEx)
            property_management = st.number_input("Property Management", value=prop.expenses.property_management)
            mortgage = st.number_input("Mortgage", value=prop.expenses.mortgage)
            other_expense = st.number_input("Other Expense", value=prop.expenses.other_expense)

            # Growth assumptions
            st.markdown("#### Long-Term Assumptions")
            colg = st.columns(3)
            appreciation_rate = colg[0].slider("Appreciation Rate (%)", 0.0, 10.0, 3.0)
            rent_growth = colg[1].slider("Rent Growth (%)", 0.0, 10.0, 2.0)
            expense_growth = colg[2].slider("Expense Growth (%)", 0.0, 10.0, 2.0)

            # Create temp Property for scenario
            income = Income(rent_income, laundry_income, other_income)
            expenses = Expense(
                tax_expense, insurance_expense, electric_expense, water_sewer_expense,
                garbage_expense, gas_expense, hoa_expense, lawn_care_expense, snow_removal_expense,
                vacancy_rate, repairs, capEx, property_management,
                mortgage, other_expense
            )
            prop_temp = Property(
                prop.address,
                purchase_price,
                down_payment,
                loan_interest_rate / 100 if use_loan else 0.0,
                loan_years if use_loan else 0,
                income,
                expenses
            )

            # Recalculate with new values
            metrics_new = calculate_metrics(prop_temp)
            df_proj = project_long_term(prop_temp,
                                        appreciation_rate=appreciation_rate / 100,
                                        rent_growth=rent_growth / 100,
                                        expense_growth=expense_growth / 100)

            # Display updated metrics
            st.markdown("### Updated Financials")
            c1, c2, c3 = st.columns(3)
            c1.metric("Monthly Cash Flow", f"${metrics_new['Monthly Cash Flow']:,.2f}")
            c2.metric("Cap Rate", f"{metrics_new['Cap Rate (%)']:.2f}%")
            c3.metric("CoC Return", f"{metrics_new['Cash-on-Cash Return (%)']:.2f}%")

            # Charts
            c1, c2 = st.columns(2)
            with c1:
                fig1 = px.line(df_proj, x="Year", y="Property Value", title="Projected Property Value Growth")
                st.plotly_chart(fig1, use_container_width=True)
            with c2:
                fig2 = px.line(df_proj, x="Year", y="Annual Cash Flow", title="Projected Annual Cash Flow")
                st.plotly_chart(fig2, use_container_width=True)

            fig3 = go.Figure()
            fig3.add_trace(go.Scatter(x=df_proj["Year"], y=df_proj["Cumulative Cash Flow"], mode='lines', name='Cumulative Cash Flow'))
            fig3.add_trace(go.Scatter(x=df_proj["Year"], y=df_proj["Equity"], mode='lines', name='Equity'))
            fig3.add_trace(go.Scatter(x=df_proj["Year"], y=df_proj["Loan Balance"], mode='lines', name='Loan Balance'))
            fig3.update_layout(title="Cumulative Cash Flow, Equity & Loan Balance", xaxis_title="Year", yaxis_title="USD")
            st.plotly_chart(fig3, use_container_width=True)

            # Save button
            if st.button("💾 Save Changes to Property"):
                update_property_in_db(prop_temp)
                st.success(f"{prop.address} updated successfully!")
                st.rerun()
    else:
        st.info("Add a property first to view in-depth analysis.")
