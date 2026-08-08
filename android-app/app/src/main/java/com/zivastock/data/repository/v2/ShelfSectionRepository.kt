
package com.zivastock.data.repository.v2

import com.zivastock.data.local.database.ZivaStockDatabase
import com.zivastock.data.local.database.v2.entities.ShelfSectionEntity
import com.zivastock.data.remote.api.ZivaStockApi
import com.zivastock.data.remote.dto.v2.ShelfSectionDto
import kotlinx.coroutines.flow.Flow
import javax.inject.Inject

class ShelfSectionRepository @Inject constructor(
    private val database: ZivaStockDatabase,
    private val api: ZivaStockApi
) {
    private val dao = database.shelfSectionDao()

    fun getAll(): Flow<List<ShelfSectionEntity>> = dao.getAll()

    suspend fun getById(id: Long): ShelfSectionEntity? = dao.getById(id)

    suspend fun save(entity: ShelfSectionEntity) {
        // TODO: implement local save and queue for sync
        dao.insert(entity)
    }

    suspend fun saveAll(entities: List<ShelfSectionEntity>) {
        dao.insertAll(entities)
    }

    suspend fun delete(entity: ShelfSectionEntity) {
        dao.delete(entity)
    }

    suspend fun fetchFromServer() {
        // TODO: call api and map to entities
    }
}
