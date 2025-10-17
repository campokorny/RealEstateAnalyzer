import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from models.property_models import Income, Expense, Property
from services.calculations import calculate_metrics, project_long_term
from services.db import fetch_all_properties, update_property_in_db

st.subheader("🔍 In-Depth Property Analysis")

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
        is_portfolio_property = st.checkbox("Portfolio Property?", value=prop.is_portfolio_property)

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
        income = Income(rent_income=rent_income, laundry_income=laundry_income, other_income=other_income)
        expenses = Expense(
            tax_expense=tax_expense, insurance_expense=insurance_expense, electric_expense=electric_expense,
            water_sewer_expense=water_sewer_expense, garbage_expense=garbage_expense, gas_expense=gas_expense,
            hoa_expense=hoa_expense, lawn_care_expense=lawn_care_expense, snow_removal_expense=snow_removal_expense,
            vacancy_rate=vacancy_rate, repairs=repairs, capEx=capEx, property_management=property_management,
            mortgage=mortgage, other_expense=other_expense
        )
        prop_temp = Property(
            id=prop.id,
            address=prop.address,
            purchase_price=purchase_price,
            down_payment=down_payment,
            loan_interest_rate=loan_interest_rate / 100 if use_loan else 0.0,
            loan_years=loan_years if use_loan else 0,
            is_portfolio_property=is_portfolio_property,
            income=income,
            expenses=expenses
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
            st.rerun()

else:
    st.info("Add a property first to view in-depth analysis.")
