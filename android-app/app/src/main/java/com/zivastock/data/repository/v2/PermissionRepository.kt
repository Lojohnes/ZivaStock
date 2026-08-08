
package com.zivastock.data.repository.v2

import com.zivastock.data.local.database.ZivaStockDatabase
import com.zivastock.data.local.database.v2.entities.PermissionEntity
import com.zivastock.data.remote.api.ZivaStockApi
import com.zivastock.data.remote.dto.v2.PermissionDto
import kotlinx.coroutines.flow.Flow
import javax.inject.Inject

class PermissionRepository @Inject constructor(
    private val database: ZivaStockDatabase,
    private val api: ZivaStockApi
) {
    private val dao = database.permissionDao()

    fun getAll(): Flow<List<PermissionEntity>> = dao.getAll()

    suspend fun getById(id: Long): PermissionEntity? = dao.getById(id)

    suspend fun save(entity: PermissionEntity) {
        // TODO: implement local save and queue for sync
        dao.insert(entity)
    }

    suspend fun saveAll(entities: List<PermissionEntity>) {
        dao.insertAll(entities)
    }

    suspend fun delete(entity: PermissionEntity) {
        dao.delete(entity)
    }

    suspend fun fetchFromServer() {
        // TODO: call api and map to entities
    }
}
