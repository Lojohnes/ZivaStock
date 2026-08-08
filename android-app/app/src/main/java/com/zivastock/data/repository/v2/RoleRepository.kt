
package com.zivastock.data.repository.v2

import com.zivastock.data.local.database.ZivaStockDatabase
import com.zivastock.data.local.database.v2.entities.RoleEntity
import com.zivastock.data.remote.api.ZivaStockApi
import com.zivastock.data.remote.dto.v2.RoleDto
import kotlinx.coroutines.flow.Flow
import javax.inject.Inject

class RoleRepository @Inject constructor(
    private val database: ZivaStockDatabase,
    private val api: ZivaStockApi
) {
    private val dao = database.roleDao()

    fun getAll(): Flow<List<RoleEntity>> = dao.getAll()

    suspend fun getById(id: Long): RoleEntity? = dao.getById(id)

    suspend fun save(entity: RoleEntity) {
        // TODO: implement local save and queue for sync
        dao.insert(entity)
    }

    suspend fun saveAll(entities: List<RoleEntity>) {
        dao.insertAll(entities)
    }

    suspend fun delete(entity: RoleEntity) {
        dao.delete(entity)
    }

    suspend fun fetchFromServer() {
        // TODO: call api and map to entities
    }
}
