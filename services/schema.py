PROPERTY_FIELDS = {
    "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
    "address": "TEXT NOT NULL",
    "purchase_price": "REAL",
    "down_payment": "REAL",
    "loan_interest_rate": "REAL",
    "loan_years": "INTEGER",
    "is_portfolio_property": "BOOLEAN",
    # "financing_type": "TEXT",   # "cash" or "financed"
    # "property_type": "TEXT"     # "rental" or "flip"
}

INCOME_FIELDS = {
    "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
    "property_id": "INTEGER",
    "rent_income": "REAL",
    "laundry_income": "REAL",
    "other_income": "REAL",
    "FOREIGN KEY(property_id)": "REFERENCES properties(id) ON DELETE CASCADE"
}

EXPENSE_FIELDS = {
    "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
    "property_id": "INTEGER",
    "tax_expense": "REAL",
    "insurance_expense": "REAL",
    "electric_expense": "REAL",
    "water_sewer_expense": "REAL",
    "garbage_expense": "REAL",
    "gas_expense": "REAL",
    "hoa_expense": "REAL",
    "lawn_care_expense": "REAL",
    "snow_removal_expense": "REAL",
    "vacancy_rate": "REAL",
    "repairs": "REAL",
    "capEx": "REAL",
    "property_management": "REAL",
    "mortgage": "REAL",
    "other_expense": "REAL",
    "FOREIGN KEY(property_id)": "REFERENCES properties(id) ON DELETE CASCADE"
}


# TODO: remove if unused
# configuration for form generation
PROPERTY_INPUTS = {
    "address": {"label": "Address", "widget": "text_input"},
    "purchase_price": {"label": "Purchase Price", "widget": "number_input"},
    "down_payment": {"label": "Down Payment", "widget": "number_input"},
    "loan_interest_rate": {"label": "Interest Rate (%)", "widget": "number_input"},
    "loan_years": {"label": "Loan Term (years)", "widget": "number_input"},
    "is_portfolio_property": {"label": "Add to Portfolio", "widget": "checkbox"},
    "financing_type": {"label": "Financing Type", "widget": "selectbox", "options": ["Cash", "Financed"]},
    "property_type": {"label": "Property Type", "widget": "selectbox", "options": ["Rental", "Flip"]},
}
