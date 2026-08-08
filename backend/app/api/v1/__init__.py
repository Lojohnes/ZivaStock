from fastapi import APIRouter
from app.api.v1 import auth, users, products, counts, adjustments, sessions, sync, reports, locations, imports, exports, roles

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(roles.router, prefix="/roles", tags=["Roles"])
api_router.include_router(products.router, prefix="/products", tags=["Products"])
api_router.include_router(counts.router, prefix="/counts", tags=["Counts"])
api_router.include_router(adjustments.router, prefix="/adjustments", tags=["Adjustments"])
api_router.include_router(sessions.router, prefix="/sessions", tags=["Sessions"])
api_router.include_router(sync.router, prefix="/sync", tags=["Sync"])
api_router.include_router(reports.router, prefix="/reports", tags=["Reports"])
api_router.include_router(locations.router, prefix="/locations", tags=["Locations"])
api_router.include_router(imports.router, prefix="/imports", tags=["Imports"])
api_router.include_router(exports.router, prefix="/exports", tags=["Exports"])
