
package com.zivastock.data.local.database.v2.dao

import androidx.room.*
import com.zivastock.data.local.database.v2.entities.UserRoleCrossRefEntity
import kotlinx.coroutines.flow.Flow

@Dao
interface UserRoleCrossRefDao {
    @Query("SELECT * FROM v2_user_roles")
    fun getAll(): Flow<List<UserRoleCrossRefEntity>>


    @Query("SELECT * FROM v2_user_roles WHERE userId = :userId AND roleId = :roleId")
    suspend fun getByIds(userId: Long, roleId: Long): UserRoleCrossRefEntity?


    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(item: UserRoleCrossRefEntity): Long

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertAll(items: List<UserRoleCrossRefEntity>): List<Long>

    @Update
    suspend fun update(item: UserRoleCrossRefEntity)

    @Delete
    suspend fun delete(item: UserRoleCrossRefEntity)

    @Query("DELETE FROM v2_user_roles")
    suspend fun deleteAll()
}
