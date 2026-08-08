package com.zivastock.data.repository.v2

import com.zivastock.data.local.database.ZivaStockDatabase
import com.zivastock.data.local.database.v2.entities.LocationEntity
import com.zivastock.data.local.database.v2.entities.ShelfEntity
import com.zivastock.data.local.database.v2.entities.ShelfSectionEntity
import com.zivastock.data.local.database.v2.entities.StocktakeSessionEntity
import com.zivastock.data.remote.api.ZivaStockApi
import com.zivastock.data.remote.dto.v2.LocationDto
import com.zivastock.data.remote.dto.v2.ShelfDto
import com.zivastock.data.remote.dto.v2.ShelfSectionDto
import com.zivastock.data.remote.dto.v2.StocktakeSessionDto
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.first
import javax.inject.Inject

class SessionRepository @Inject constructor(
    private val database: ZivaStockDatabase,
    private val api: ZivaStockApi
) {
    private val sessionDao = database.stocktakeSessionDao()
    private val locationDao = database.locationDao()
    private val shelfDao = database.shelfDao()
    private val shelfSectionDao = database.shelfSectionDao()

    fun getAll(): Flow<List<StocktakeSessionEntity>> = sessionDao.getAll()

    fun getActiveSession(): Flow<StocktakeSessionEntity?> = sessionDao.getActiveSession()

    fun getAllLocations(): Flow<List<LocationEntity>> = locationDao.getAll()

    suspend fun getLocationById(id: Long): LocationEntity? = locationDao.getById(id)

    suspend fun getShelvesForLocation(locationId: Long): List<ShelfEntity> {
        return shelfDao.getAll().first().filter { it.locationId == locationId }
    }

    suspend fun getSectionsForShelves(shelfIds: List<Long>): List<ShelfSectionEntity> {
        return shelfSectionDao.getAll().first().filter { it.shelfId in shelfIds }
    }

    suspend fun syncActiveSession(): Result<StocktakeSessionEntity?> {
        return try {
            val sessionsResponse = api.getSessions()
            if (!sessionsResponse.isSuccessful || sessionsResponse.body() == null) {
                return Result.failure(Exception("Failed to fetch sessions: ${sessionsResponse.code()}"))
            }

            val sessions = sessionsResponse.body()!!.map { it.toEntity() }
            sessionDao.deleteAll()
            sessionDao.insertAll(sessions)

            val active = sessions.filter { it.status in ACTIVE_STATUSES }.maxByOrNull { it.id }

            // Also refresh location / shelf / section catalog so the dashboard can display names
            syncCatalog()

            Result.success(active)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    private suspend fun syncCatalog() {
        try {
            val locations = api.getLocations()
            if (locations.isSuccessful && locations.body() != null) {
                locationDao.deleteAll()
                locationDao.insertAll(locations.body()!!.map { it.toEntity() })
            }

            val shelves = api.getShelves()
            if (shelves.isSuccessful && shelves.body() != null) {
                shelfDao.deleteAll()
                shelfDao.insertAll(shelves.body()!!.map { it.toEntity() })
            }

            val sections = api.getShelfSections()
            if (sections.isSuccessful && sections.body() != null) {
                shelfSectionDao.deleteAll()
                shelfSectionDao.insertAll(sections.body()!!.map { it.toEntity() })
            }
        } catch (e: Exception) {
            // catalog is optional for the session itself; keep local copy on failure
        }
    }

    private fun StocktakeSessionDto.toEntity(): StocktakeSessionEntity {
        return StocktakeSessionEntity(
            id = id ?: 0,
            uuid = uuid.orEmpty(),
            name = name.orEmpty(),
            description = description,
            locationId = locationId ?: 0,
            sessionType = sessionType ?: "full",
            status = status ?: "not_started",
            startTime = startTime,
            endTime = endTime,
            createdBy = createdBy ?: 0,
            approvedBy = approvedBy,
            approvedAt = approvedAt,
            createdAt = createdAt,
            updatedAt = updatedAt
        )
    }

    private fun LocationDto.toEntity(): LocationEntity {
        return LocationEntity(
            id = id ?: 0,
            name = name.orEmpty(),
            type = type.orEmpty(),
            parentId = parentId,
            address = address,
            isActive = isActive ?: true,
            createdAt = createdAt,
            updatedAt = updatedAt
        )
    }

    private fun ShelfDto.toEntity(): ShelfEntity {
        return ShelfEntity(
            id = id ?: 0,
            locationId = locationId ?: 0,
            name = name.orEmpty(),
            description = description,
            isActive = isActive ?: true,
            createdAt = createdAt,
            updatedAt = updatedAt
        )
    }

    private fun ShelfSectionDto.toEntity(): ShelfSectionEntity {
        return ShelfSectionEntity(
            id = id ?: 0,
            shelfId = shelfId ?: 0,
            name = name.orEmpty(),
            description = description,
            isActive = isActive ?: true,
            createdAt = createdAt,
            updatedAt = updatedAt
        )
    }

    companion object {
        val ACTIVE_STATUSES = setOf("active", "in_progress", "not_started", "started")
    }
}
