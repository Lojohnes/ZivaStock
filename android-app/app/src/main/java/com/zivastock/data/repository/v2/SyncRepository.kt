
package com.zivastock.data.repository.v2

import com.zivastock.data.local.database.ZivaStockDatabase
import com.zivastock.data.local.database.v2.entities.SyncQueueItemEntity
import com.zivastock.data.remote.api.ZivaStockApi
import com.zivastock.data.remote.dto.v2.SyncPullResponseDto
import kotlinx.coroutines.flow.Flow
import javax.inject.Inject

class SyncRepository @Inject constructor(
    private val database: ZivaStockDatabase,
    private val api: ZivaStockApi
) {
    private val dao = database.syncQueueItemDao()

    fun getAll(): Flow<List<SyncQueueItemEntity>> = dao.getAll()

    suspend fun getById(id: Long): SyncQueueItemEntity? = dao.getById(id)

    suspend fun save(entity: SyncQueueItemEntity) {
        // TODO: implement local save and queue for sync
        dao.insert(entity)
    }

    suspend fun saveAll(entities: List<SyncQueueItemEntity>) {
        dao.insertAll(entities)
    }

    suspend fun delete(entity: SyncQueueItemEntity) {
        dao.delete(entity)
    }

    suspend fun fetchFromServer() {
        // TODO: call api and map to entities
    }
}
