
package com.zivastock.data.repository.v2

import com.zivastock.data.local.database.ZivaStockDatabase
import com.zivastock.data.local.database.v2.entities.LocationEntity
import com.zivastock.data.remote.api.ZivaStockApi
import com.zivastock.data.remote.dto.v2.LocationDto
import kotlinx.coroutines.flow.Flow
import javax.inject.Inject

class LocationRepository @Inject constructor(
    private val database: ZivaStockDatabase,
    private val api: ZivaStockApi
) {
    private val dao = database.locationDao()

    fun getAll(): Flow<List<LocationEntity>> = dao.getAll()

    suspend fun getById(id: Long): LocationEntity? = dao.getById(id)

    suspend fun save(entity: LocationEntity) {
        // TODO: implement local save and queue for sync
        dao.insert(entity)
    }

    suspend fun saveAll(entities: List<LocationEntity>) {
        dao.insertAll(entities)
    }

    suspend fun delete(entity: LocationEntity) {
        dao.delete(entity)
    }

    suspend fun fetchFromServer() {
        // TODO: call api and map to entities
    }
}
