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
