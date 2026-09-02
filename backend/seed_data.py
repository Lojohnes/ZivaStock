from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

from app.core.config import settings
from app.models.user import User
from app.models.role import Role, Permission
from app.models.location import Location, Shelf, ShelfSection
from app.models.product import Product, ProductCategory
from app.models.session import StocktakeSession
from app.core.security import get_password_hash

# -----------------------------------------------------------------------------
# Permission catalog, grouped by module
# -----------------------------------------------------------------------------
PERMISSIONS = [
    ("users.create", "users", "Create users"),
    ("users.update", "users", "Update users, reset passwords, unlock accounts"),
    ("users.delete", "users", "Delete users"),
    ("roles.create", "roles", "Create roles"),
    ("roles.update", "roles", "Update roles and their permissions"),
    ("roles.delete", "roles", "Delete non-system roles"),
    ("products.create", "products", "Create products and categories"),
    ("products.update", "products", "Update products and categories"),
    ("products.delete", "products", "Delete products and categories"),
    ("locations.create", "locations", "Create locations, shelves, sections"),
    ("locations.update", "locations", "Update locations, shelves, sections"),
    ("locations.delete", "locations", "Delete locations, shelves, sections"),
    ("sessions.create", "sessions", "Create stocktake sessions"),
    ("sessions.update", "sessions", "Update/transition stocktake sessions"),
    ("sessions.assign", "sessions", "Assign counters to sessions"),
    ("sessions.reconcile", "sessions", "Move a session into reconciliation"),
    ("sessions.approve", "sessions", "Approve/complete a stocktake session"),
    ("counts.create", "counts", "Submit first/second counts"),
    ("counts.update", "counts", "Edit existing counts"),
    ("counts.delete", "counts", "Delete counts"),
    ("adjustments.create", "adjustments", "Generate adjustments from counts"),
    ("adjustments.approve", "adjustments", "Approve or reject adjustments"),
    ("adjustments.post", "adjustments", "Post approved adjustments to inventory"),
    ("reports.view_audit", "reports", "View the audit trail report"),
]

# -----------------------------------------------------------------------------
# Roles -> permission names (Super Admin gets everything automatically)
# -----------------------------------------------------------------------------
ROLE_DEFINITIONS = {
    "Super Admin": {
        "description": "Full system access",
        "is_system": True,
        "permissions": "*",
    },
    "Stocktake Manager": {
        "description": "Manages stocktake sessions end-to-end",
        "is_system": True,
        "permissions": [
            "products.create", "products.update",
            "locations.create", "locations.update",
            "sessions.create", "sessions.update", "sessions.assign",
            "sessions.reconcile", "sessions.approve",
            "counts.update", "counts.delete",
            "adjustments.create", "adjustments.approve", "adjustments.post",
            "reports.view_audit",
        ],
    },
    "Supervisor": {
        "description": "Supervises counting teams and assignments",
        "is_system": True,
        "permissions": [
            "sessions.update", "sessions.assign",
            "counts.update",
            "adjustments.approve",
        ],
    },
    "Counter": {
        "description": "Performs first/second counts",
        "is_system": True,
        "permissions": ["counts.create"],
    },
    "Auditor": {
        "description": "Read-only review of reports and audit trail",
        "is_system": True,
        "permissions": ["reports.view_audit"],
    },
}


def seed():
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    try:
        # Permissions
        perm_by_name = {}
        for name, module, description in PERMISSIONS:
            perm = db.query(Permission).filter(Permission.name == name).first()
            if not perm:
                perm = Permission(name=name, module=module, description=description)
                db.add(perm)
                db.commit()
                db.refresh(perm)
            perm_by_name[name] = perm

        # Roles + role_permissions
        role_by_name = {}
        for name, defn in ROLE_DEFINITIONS.items():
            role = db.query(Role).filter(Role.name == name).first()
            if not role:
                role = Role(name=name, description=defn["description"], is_system=defn["is_system"])
                db.add(role)
                db.commit()
                db.refresh(role)

            wanted_perms = list(perm_by_name.values()) if defn["permissions"] == "*" else [
                perm_by_name[p] for p in defn["permissions"]
            ]
            existing_ids = {p.id for p in role.permissions}
            for perm in wanted_perms:
                if perm.id not in existing_ids:
                    role.permissions.append(perm)
            db.commit()
            role_by_name[name] = role

        # Super Admin user
        admin_role = role_by_name["Super Admin"]
        admin = db.query(User).filter(User.email == "admin@zivastock.com").first()
        if not admin:
            admin = User(
                email="admin@zivastock.com",
                password_hash=get_password_hash(os.getenv("SEED_ADMIN_PASSWORD", "Admin@12345")),
                first_name="System",
                last_name="Admin",
                role_id=admin_role.id,
                is_active=True,
            )
            db.add(admin)
            db.commit()
            db.refresh(admin)

        # Locations
        location = db.query(Location).filter(Location.name == "Main Warehouse").first()
        if not location:
            location = Location(name="Main Warehouse", type="warehouse")
            db.add(location)
            db.commit()
            db.refresh(location)

        # Shelves
        shelf = db.query(Shelf).filter(Shelf.name == "Shelf A", Shelf.location_id == location.id).first()
        if not shelf:
            shelf = Shelf(name="Shelf A", location_id=location.id)
            db.add(shelf)
            db.commit()
            db.refresh(shelf)

        # Shelf Sections
        section_names = ["A1", "A2", "B1", "B2", "C1"]
        for name in section_names:
            section = db.query(ShelfSection).filter(ShelfSection.name == name, ShelfSection.shelf_id == shelf.id).first()
            if not section:
                db.add(ShelfSection(name=name, shelf_id=shelf.id))
        db.commit()

        # Product category
        category = db.query(ProductCategory).filter(ProductCategory.name == "Electronics").first()
        if not category:
            category = ProductCategory(name="Electronics", description="Electronic devices and accessories")
            db.add(category)
            db.commit()
            db.refresh(category)

        # Products
        products = [
            Product(barcode="100000000001", product_code="P001", description="Laptop", unit_of_measure="EA", system_quantity=50.0, unit_cost=800.0, unit_price=999.0, category_id=category.id),
            Product(barcode="100000000002", product_code="P002", description="Mouse", unit_of_measure="EA", system_quantity=200.0, unit_cost=25.0, unit_price=39.0, category_id=category.id),
            Product(barcode="100000000003", product_code="P003", description="Keyboard", unit_of_measure="EA", system_quantity=150.0, unit_cost=60.0, unit_price=89.0, category_id=category.id),
            Product(barcode="100000000004", product_code="P004", description="Monitor", unit_of_measure="EA", system_quantity=75.0, unit_cost=300.0, unit_price=399.0, category_id=category.id),
            Product(barcode="100000000005", product_code="P005", description="Headphones", unit_of_measure="EA", system_quantity=100.0, unit_cost=80.0, unit_price=119.0, category_id=category.id),
        ]
        for product in products:
            existing = db.query(Product).filter(Product.barcode == product.barcode).first()
            if not existing:
                db.add(product)
        db.commit()

        # Stocktake session
        session = db.query(StocktakeSession).filter(StocktakeSession.name == "Initial Count 2026").first()
        if not session:
            session = StocktakeSession(
                name="Initial Count 2026",
                description="First full warehouse count",
                location_id=location.id,
                session_type="full",
                status="not_started",
                created_by=admin.id,
            )
            db.add(session)
            db.commit()

        print("Seed data applied successfully")
        print(f"Admin login: admin@zivastock.com / Admin@12345")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
