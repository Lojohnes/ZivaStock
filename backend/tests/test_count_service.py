import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.base import Base
from app.models.user import User
from app.models.role import Role
from app.models.product import Product
from app.models.location import Location, Shelf, Section
from app.models.session import StocktakeSession
from app.services.count_service import CountService
from app.schemas.count import CountCreate


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    TestingSessionLocal = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()


@pytest.fixture
def count_service(db_session):
    return CountService(db_session)


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

    location = Location(name="Warehouse", type="warehouse", description="Main warehouse")
    session.add(location)
    session.commit()

    shelf = Shelf(name="Shelf A", location_id=location.id)
    session.add(shelf)
    session.commit()

    section = Section(name="A1", shelf_id=shelf.id)
    session.add(section)

    product = Product(
        barcode="123456",
        product_code="P001",
        description="Test Product",
        unit_of_measure="each",
        system_quantity=100.0,
        unit_cost=10.0,
    )
    session.add(product)
    session.commit()

    stock_session = StocktakeSession(name="Cycle 1", location_id=location.id, created_by=user.id)
    session.add(stock_session)
    session.commit()

    return user, product, section, stock_session


def test_create_count(count_service, db_session):
    user, product, section, stock_session = seed_data(db_session)
    count_data = CountCreate(
        product_id=product.id,
        section_id=section.id,
        quantity=95.0,
        session_id=stock_session.id,
    )
    count = count_service.create_count(count_data, user.id)
    assert count.product_id == product.id
    assert count.section_id == section.id
    assert float(count.quantity) == 95.0


def test_get_counts_by_section(count_service, db_session):
    user, product, section, stock_session = seed_data(db_session)
    count_data = CountCreate(
        product_id=product.id,
        section_id=section.id,
        quantity=95.0,
        session_id=stock_session.id,
    )
    count_service.create_count(count_data, user.id)
    counts = count_service.get_counts_by_section(section.id, stock_session.id)
    assert len(counts) == 1


def test_create_count_product_not_found(count_service, db_session):
    user, _, section, stock_session = seed_data(db_session)
    count_data = CountCreate(
        product_id=9999,
        section_id=section.id,
        quantity=95.0,
        session_id=stock_session.id,
    )
    with pytest.raises(ValueError, match="Product not found"):
        count_service.create_count(count_data, user.id)


def test_delete_count(count_service, db_session):
    user, product, section, stock_session = seed_data(db_session)
    count_data = CountCreate(
        product_id=product.id,
        section_id=section.id,
        quantity=95.0,
        session_id=stock_session.id,
    )
    count = count_service.create_count(count_data, user.id)
    assert count_service.delete_count(count.id) is True
    assert count_service.delete_count(count.id) is False
