from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from app.core.database import get_db
from app.schemas.location import (
    LocationCreate, LocationUpdate, LocationResponse,
    ShelfCreate, ShelfUpdate, ShelfResponse,
    ShelfSectionCreate, ShelfSectionUpdate, ShelfSectionResponse
)
from app.services.location_service import LocationService
from app.models.user import User
from app.api.deps import get_current_user_id, require_permission

router = APIRouter()


# Location endpoints
@router.post("", response_model=LocationResponse, status_code=status.HTTP_201_CREATED)
def create_location(
    location_data: LocationCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("locations.create")),
):
    """Create a new location (requires locations.create permission)"""
    location_service = LocationService(db)
    location = location_service.create_location(location_data)
    return location


@router.get("", response_model=list[LocationResponse])
def get_locations(
    type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """Get all locations"""
    location_service = LocationService(db)
    return location_service.get_locations(type=type)


@router.get("/tree")
def get_location_tree(db: Session = Depends(get_db), current_user_id: int = Depends(get_current_user_id)):
    """Get location hierarchy tree"""
    location_service = LocationService(db)
    return location_service.get_location_tree()


# Shelf endpoints
@router.get("/shelves", response_model=List[ShelfResponse])
def get_shelves(
    location_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    """Get shelves, optionally filtered by location"""
    return LocationService(db).get_shelves(location_id=location_id)


@router.post("/shelves", response_model=ShelfResponse, status_code=status.HTTP_201_CREATED)
def create_shelf(
    shelf_data: ShelfCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("locations.create")),
):
    """Create a new shelf (requires locations.create permission)"""
    location_service = LocationService(db)
    try:
        return location_service.create_shelf(shelf_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put("/shelves/{shelf_id}", response_model=ShelfResponse)
def update_shelf(
    shelf_id: int,
    shelf_data: ShelfUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("locations.update")),
):
    """Update a shelf (requires locations.update permission)"""
    shelf = LocationService(db).update_shelf(shelf_id, shelf_data)
    if not shelf:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shelf not found")
    return shelf


@router.delete("/shelves/{shelf_id}")
def delete_shelf(
    shelf_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("locations.delete")),
):
    """Delete a shelf (requires locations.delete permission)"""
    success = LocationService(db).delete_shelf(shelf_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shelf not found")
    return {"message": "Shelf deleted successfully"}


@router.get("/shelves/{shelf_id}/sections", response_model=List[ShelfSectionResponse])
def get_shelf_sections(shelf_id: int, db: Session = Depends(get_db), current_user_id: int = Depends(get_current_user_id)):
    """Get all sections for a shelf"""
    location_service = LocationService(db)
    return location_service.get_shelf_sections(shelf_id)


# Shelf Section endpoints
@router.get("/sections", response_model=List[ShelfSectionResponse])
def get_sections(db: Session = Depends(get_db), current_user_id: int = Depends(get_current_user_id)):
    """Get all shelf sections"""
    return LocationService(db).get_sections()


@router.post("/sections", response_model=ShelfSectionResponse, status_code=status.HTTP_201_CREATED)
def create_section(
    section_data: ShelfSectionCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("locations.create")),
):
    """Create a new shelf section (requires locations.create permission)"""
    location_service = LocationService(db)
    try:
        return location_service.create_section(section_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put("/sections/{section_id}", response_model=ShelfSectionResponse)
def update_section(
    section_id: int,
    section_data: ShelfSectionUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("locations.update")),
):
    """Update a shelf section (requires locations.update permission)"""
    section = LocationService(db).update_section(section_id, section_data)
    if not section:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Section not found")
    return section


@router.delete("/sections/{section_id}")
def delete_section(
    section_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("locations.delete")),
):
    """Delete a shelf section (requires locations.delete permission)"""
    success = LocationService(db).delete_section(section_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Section not found")
    return {"message": "Section deleted successfully"}


@router.get("/{location_id}", response_model=LocationResponse)
def get_location(location_id: int, db: Session = Depends(get_db), current_user_id: int = Depends(get_current_user_id)):
    """Get location by ID"""
    location_service = LocationService(db)
    location = location_service.get_location(location_id)
    if not location:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Location not found")
    return location


@router.put("/{location_id}", response_model=LocationResponse)
def update_location(
    location_id: int,
    location_data: LocationUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("locations.update")),
):
    """Update location (requires locations.update permission)"""
    location_service = LocationService(db)
    location = location_service.update_location(location_id, location_data)
    if not location:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Location not found")
    return location
