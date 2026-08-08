
package com.zivastock.data.repository.v2

import com.zivastock.data.local.database.ZivaStockDatabase
import com.zivastock.data.local.database.v2.entities.ShelfEntity
import com.zivastock.data.remote.api.ZivaStockApi
import com.zivastock.data.remote.dto.v2.ShelfDto
import kotlinx.coroutines.flow.Flow
import javax.inject.Inject

class ShelfRepository @Inject constructor(
    private val database: ZivaStockDatabase,
    private val api: ZivaStockApi
) {
    private val dao = database.shelfDao()

    fun getAll(): Flow<List<ShelfEntity>> = dao.getAll()

    suspend fun getById(id: Long): ShelfEntity? = dao.getById(id)

    suspend fun save(entity: ShelfEntity) {
        // TODO: implement local save and queue for sync
        dao.insert(entity)
    }

    suspend fun saveAll(entities: List<ShelfEntity>) {
        dao.insertAll(entities)
    }

    suspend fun delete(entity: ShelfEntity) {
        dao.delete(entity)
    }

    suspend fun fetchFromServer() {
        // TODO: call api and map to entities
    }
}
