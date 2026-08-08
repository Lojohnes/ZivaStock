
package com.zivastock.data.repository.v2

import com.zivastock.data.local.database.ZivaStockDatabase
import com.zivastock.data.local.database.v2.entities.StocktakeSessionEntity
import com.zivastock.data.remote.api.ZivaStockApi
import com.zivastock.data.remote.dto.v2.StocktakeSessionDto
import kotlinx.coroutines.flow.Flow
import javax.inject.Inject

class StocktakeSessionRepository @Inject constructor(
    private val database: ZivaStockDatabase,
    private val api: ZivaStockApi
) {
    private val dao = database.stocktakeSessionDao()

    fun getAll(): Flow<List<StocktakeSessionEntity>> = dao.getAll()

    suspend fun getById(id: Long): StocktakeSessionEntity? = dao.getById(id)

    suspend fun save(entity: StocktakeSessionEntity) {
        // TODO: implement local save and queue for sync
        dao.insert(entity)
    }

    suspend fun saveAll(entities: List<StocktakeSessionEntity>) {
        dao.insertAll(entities)
    }

    suspend fun delete(entity: StocktakeSessionEntity) {
        dao.delete(entity)
    }

    suspend fun fetchFromServer() {
        // TODO: call api and map to entities
    }
}
