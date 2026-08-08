import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.base import Base
from app.models.user import User
from app.models.role import Role
from app.models.product import Product
from app.models.location import Location, Shelf, Section
from app.models.session import StocktakeSession
from app.models.count import Count, Duplicate
from app.services.report_service import ReportService


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    TestingSessionLocal = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()


@pytest.fixture
def report_service(db_session):
    return ReportService(db_session)


def seed_data(session):
    role = Role(name="Counter", description="Stock counter")
    session.add(role)
    session.commit()

    user = User(
        email="counter@example.com",
        hashed_password="secret",
        first_name="Test",
        last_name="Counter",
        role_id=role.id,
        is_active=True,
    )
    session.add(user)

    product = Product(
        barcode="123456",
        product_code="P001",
        description="Test Product",
        unit_of_measure="each",
        system_quantity=100.0,
        unit_cost=10.0,
    )
    session.add(product)

    location = Location(name="Warehouse", type="warehouse")
    session.add(location)
    session.commit()

    shelf = Shelf(name="Shelf A", location_id=location.id)
    session.add(shelf)
    session.commit()

    section = Section(name="A1", shelf_id=shelf.id)
    session.add(section)
    session.commit()

    stock_session = StocktakeSession(name="Cycle 1", description="Test cycle", location_id=location.id, created_by=user.id)
    session.add(stock_session)
    session.commit()

    count = Count(
        product_id=product.id,
        section_id=section.id,
        quantity=95.0,
        user_id=user.id,
        session_id=stock_session.id,
    )
    session.add(count)
    session.commit()

    return user, product, section, stock_session


def test_get_dashboard_stats(report_service, db_session):
    seed_data(db_session)
    stats = report_service.get_dashboard_stats()
    assert "summary" in stats
    assert "sessions" in stats
    assert stats["summary"]["total_sessions"] == 1
    assert stats["summary"]["total_products"] == 1
    assert stats["summary"]["total_counts"] == 1


def test_get_variance_report(report_service, db_session):
    seed_data(db_session)
    result = report_service.get_variance_report(session_id=1)
    assert "variances" in result
    assert len(result["variances"]) == 1
    assert result["variances"][0]["variance"] == -5.0


def test_generate_duplicate_report(report_service, db_session):
    user, product, section, stock_session = seed_data(db_session)
    dup = Duplicate(
        product_id=product.id,
        section_id=section.id,
        session_id=stock_session.id,
    )
    db_session.add(dup)
    db_session.commit()
    result = report_service.generate_duplicate_report(session_id=stock_session.id)
    assert len(result) == 1


def test_get_missing_stock_report(report_service, db_session):
    seed_data(db_session)
    result = report_service.get_missing_stock_report(session_id=1)
    assert "missing_items" in result


def test_get_user_productivity_report(report_service, db_session):
    seed_data(db_session)
    result = report_service.get_user_productivity_report(session_id=1)
    assert "productivity" in result
    assert len(result["productivity"]) == 1
