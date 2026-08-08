
package com.zivastock.data.repository.v2

import com.zivastock.data.local.database.ZivaStockDatabase
import com.zivastock.data.local.database.v2.entities.UserEntity
import com.zivastock.data.remote.api.ZivaStockApi
import com.zivastock.data.remote.dto.v2.UserDto
import kotlinx.coroutines.flow.Flow
import javax.inject.Inject

class UserRepository @Inject constructor(
    private val database: ZivaStockDatabase,
    private val api: ZivaStockApi
) {
    private val dao = database.userDao()

    fun getAll(): Flow<List<UserEntity>> = dao.getAll()

    suspend fun getById(id: Long): UserEntity? = dao.getById(id)

    suspend fun save(entity: UserEntity) {
        // TODO: implement local save and queue for sync
        dao.insert(entity)
    }

    suspend fun saveAll(entities: List<UserEntity>) {
        dao.insertAll(entities)
    }

    suspend fun delete(entity: UserEntity) {
        dao.delete(entity)
    }

    suspend fun fetchFromServer() {
        // TODO: call api and map to entities
    }
}
