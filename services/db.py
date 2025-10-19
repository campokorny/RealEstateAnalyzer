from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, joinedload

from models.property_models import Base, Property, Income, Expense

# ---------- Database Setup ----------
DB_PATH = Path(__file__).parent.parent / "data" / "real_estate.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

DATABASE_URL = f"sqlite:///{DB_PATH}"
engine = create_engine(DATABASE_URL, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

# Create tables if they don't exist
Base.metadata.create_all(engine)


# ---------- CRUD Operations ----------

def get_session() -> Session:
    """Return a new SQLAlchemy session."""
    return SessionLocal()

def insert_property(property_obj: Property):
    """Insert a Property (and related income & expenses) using ORM."""
    with get_session() as session:
        try:
            session.add(property_obj)
            session.commit()
            session.refresh(property_obj)
            print(f"✅ Property '{property_obj.address}' saved to database.")

        except Exception as e:
            session.rollback()
            print(f"❌ Failed to insert property: {e}")


def update_property_in_db(prop: Property):
    """Update or merge a detached ORM property."""
    with get_session() as session:
        try:
            session.merge(prop)  # Reattach detached object and update DB
            session.commit()
            print(f"✅ Property '{prop.address}' updated successfully.")
        except Exception as e:
            session.rollback()
            print(f"❌ Failed to update property: {e}")


def delete_property(property_id: int):
    """Delete a property (and its linked income/expenses)."""
    with get_session() as session:
        try:
            prop = session.get(Property, property_id)
            if not prop:
                print(f"⚠️ Property ID {property_id} not found.")
                return
            session.delete(prop)
            session.commit()
            print(f"🗑️ Property ID {property_id} deleted.")
        except Exception as e:
            session.rollback()
            print(f"❌ Failed to delete property: {e}")

def fetch_all_properties():
    """Fetch all properties with related income and expenses."""
    with get_session() as session:
        try:
            properties = (
                session.query(Property)
                .options(
                    joinedload(Property.income),
                    joinedload(Property.expenses)
                )
                .all()
            )
            return properties
        except Exception as e:
            print(f"⚠️ Error fetching properties: {e}")
            return []


def fetch_portfolio_properties():
    """Fetch only properties marked as part of the portfolio."""
    with get_session() as session:
        try:
            properties = (
                session.query(Property)
                .options(
                    joinedload(Property.income),
                    joinedload(Property.expenses)
                )
                .filter(Property.is_portfolio_property == True)
                .all()
            )
            return properties
        except Exception as e:
            print(f"⚠️ Error fetching portfolio properties: {e}")
            return []

def create_tables():
    """Ensure all ORM models have corresponding tables."""
    Base.metadata.create_all(engine)
