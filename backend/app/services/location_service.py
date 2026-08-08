from sqlalchemy.orm import Session
from app.models.location import Location, Shelf, ShelfSection
from app.schemas.location import (
    LocationCreate, LocationUpdate, LocationResponse,
    ShelfCreate, ShelfUpdate, ShelfResponse,
    ShelfSectionCreate, ShelfSectionUpdate, ShelfSectionResponse
)
from typing import Optional, List


class LocationService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_location(self, location_id: int) -> Optional[Location]:
        """Get location by ID"""
        return self.db.query(Location).filter(Location.id == location_id).first()
    
    def get_locations(self, type: Optional[str] = None) -> List[Location]:
        """Get all locations with optional type filter"""
        query = self.db.query(Location)
        if type:
            query = query.filter(Location.type == type)
        return query.all()
    
    def create_location(self, location_data: LocationCreate) -> Location:
        """Create a new location"""
        db_location = Location(**location_data.model_dump())
        self.db.add(db_location)
        self.db.commit()
        self.db.refresh(db_location)
        return db_location
    
    def update_location(self, location_id: int, location_data: LocationUpdate) -> Optional[Location]:
        """Update location"""
        location = self.get_location(location_id)
        if not location:
            return None
        
        update_data = location_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(location, field, value)
        
        self.db.commit()
        self.db.refresh(location)
        return location
    
    def get_location_tree(self) -> dict:
        """Get location hierarchy as a tree"""
        locations = self.get_locations()
        
        def build_tree(parent_id=None):
            children = [loc for loc in locations if loc.parent_id == parent_id]
            return [
                {
                    "id": loc.id,
                    "name": loc.name,
                    "type": loc.type,
                    "children": build_tree(loc.id),
                    "shelves": [
                        {
                            "id": shelf.id,
                            "name": shelf.name,
                            "sections": [
                                {
                                    "id": section.id,
                                    "name": section.name
                                }
                                for section in self.db.query(ShelfSection).filter(ShelfSection.shelf_id == shelf.id).all()
                            ]
                        }
                        for shelf in self.db.query(Shelf).filter(Shelf.location_id == loc.id).all()
                    ]
                }
                for loc in children
            ]
        
        return build_tree()
    
    def get_shelves(self, location_id: Optional[int] = None) -> List[Shelf]:
        """Get shelves, optionally filtered by location"""
        query = self.db.query(Shelf)
        if location_id is not None:
            query = query.filter(Shelf.location_id == location_id)
        return query.all()

    def create_shelf(self, shelf_data: ShelfCreate) -> Shelf:
        """Create a new shelf"""
        # Verify location exists
        location = self.get_location(shelf_data.location_id)
        if not location:
            raise ValueError("Location not found")
        
        db_shelf = Shelf(**shelf_data.model_dump())
        self.db.add(db_shelf)
        self.db.commit()
        self.db.refresh(db_shelf)
        return db_shelf
    
    def get_shelf(self, shelf_id: int) -> Optional[Shelf]:
        """Get shelf by ID"""
        return self.db.query(Shelf).filter(Shelf.id == shelf_id).first()

    def update_shelf(self, shelf_id: int, shelf_data: ShelfUpdate) -> Optional[Shelf]:
        """Update shelf"""
        shelf = self.get_shelf(shelf_id)
        if not shelf:
            return None
        for field, value in shelf_data.model_dump(exclude_unset=True).items():
            setattr(shelf, field, value)
        self.db.commit()
        self.db.refresh(shelf)
        return shelf

    def delete_shelf(self, shelf_id: int) -> bool:
        shelf = self.get_shelf(shelf_id)
        if not shelf:
            return False
        self.db.delete(shelf)
        self.db.commit()
        return True

    def get_shelf_sections(self, shelf_id: int) -> List[ShelfSection]:
        """Get all sections for a shelf"""
        return self.db.query(ShelfSection).filter(ShelfSection.shelf_id == shelf_id).all()

    def get_sections(self) -> List[ShelfSection]:
        """Get all shelf sections"""
        return self.db.query(ShelfSection).all()

    def get_section(self, section_id: int) -> Optional[ShelfSection]:
        return self.db.query(ShelfSection).filter(ShelfSection.id == section_id).first()

    def create_section(self, section_data: ShelfSectionCreate) -> ShelfSection:
        """Create a new shelf section"""
        # Verify shelf exists
        shelf = self.db.query(Shelf).filter(Shelf.id == section_data.shelf_id).first()
        if not shelf:
            raise ValueError("Shelf not found")

        db_section = ShelfSection(**section_data.model_dump())
        self.db.add(db_section)
        self.db.commit()
        self.db.refresh(db_section)
        return db_section

    def update_section(self, section_id: int, section_data: ShelfSectionUpdate) -> Optional[ShelfSection]:
        section = self.get_section(section_id)
        if not section:
            return None
        for field, value in section_data.model_dump(exclude_unset=True).items():
            setattr(section, field, value)
        self.db.commit()
        self.db.refresh(section)
        return section

    def delete_section(self, section_id: int) -> bool:
        section = self.get_section(section_id)
        if not section:
            return False
        self.db.delete(section)
        self.db.commit()
        return True
