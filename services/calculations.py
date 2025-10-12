from models.property_models import Property
import pandas as pd

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

def monthly_mortgage(principal, annual_interest, years):
    """Calculate monthly mortgage payment using amortization formula."""
    r = annual_interest / 12
    n = years * 12
    if r == 0:
        return principal / n
    return principal * (r * (1 + r)**n) / ((1 + r)**n - 1)


def monthly_cash_flow(rent, other_income, expenses, mortgage):
    """Total rental income minus all monthly expenses (including mortgage)."""
    total_income = rent + other_income
    total_expenses = sum(expenses.values()) + mortgage
    return total_income - total_expenses


def cap_rate(annual_net_income, purchase_price):
    """Net operating income / purchase price."""
    return (annual_net_income / purchase_price) * 100 if purchase_price else 0


def cash_on_cash(annual_cash_flow, cash_invested):
    """Annual cash flow / total cash invested."""
    return (annual_cash_flow / cash_invested) * 100 if cash_invested else 0
