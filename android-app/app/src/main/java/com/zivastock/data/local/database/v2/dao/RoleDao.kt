
package com.zivastock.data.local.database.v2.dao

import androidx.room.*
import com.zivastock.data.local.database.v2.entities.RoleEntity
import kotlinx.coroutines.flow.Flow

@Dao
interface RoleDao {
    @Query("SELECT * FROM v2_roles")
    fun getAll(): Flow<List<RoleEntity>>


    @Query("SELECT * FROM v2_roles WHERE id = :id")
    suspend fun getById(id: Long): RoleEntity?


    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(item: RoleEntity): Long

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertAll(items: List<RoleEntity>): List<Long>

    @Update
    suspend fun update(item: RoleEntity)

    @Delete
    suspend fun delete(item: RoleEntity)

    @Query("DELETE FROM v2_roles")
    suspend fun deleteAll()
}
