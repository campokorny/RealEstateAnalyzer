from dataclasses import dataclass

@dataclass
class Expense:
    """
    Expenses are listed per month
    """
    tax_expense: float
    insurance_expense: float
    electric_expense: float
    water_sewer_expense: float
    garbage_expense: float
    gas_expense: float
    hoa_expense: float
    lawn_care_expense: float
    snow_removal_expense: float
    vacancy_rate: float
    repairs: float
    capEx: float
    property_management: float
    mortgage: float
    other_expense: float



@dataclass
class Income:
    """
    Income is listed per month
    """
    rent_income: float
    laundry_income: float
    other_income: float


@dataclass
class Property:
    id: int | None # SQL creates the ID, we will then read and use that ID when retrieving properties
    address: str
    purchase_price: float
    down_payment: float
    loan_interest_rate: float
    loan_years: int
    is_portfolio_property: bool
    income: Income
    expenses: Expense
