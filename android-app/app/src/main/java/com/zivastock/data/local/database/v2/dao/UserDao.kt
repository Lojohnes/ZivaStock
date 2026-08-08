
package com.zivastock.data.local.database.v2.dao

import androidx.room.*
import com.zivastock.data.local.database.v2.entities.UserEntity
import kotlinx.coroutines.flow.Flow

@Dao
interface UserDao {
    @Query("SELECT * FROM v2_users")
    fun getAll(): Flow<List<UserEntity>>


    @Query("SELECT * FROM v2_users WHERE id = :id")
    suspend fun getById(id: Long): UserEntity?


    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(item: UserEntity): Long

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertAll(items: List<UserEntity>): List<Long>

    @Update
    suspend fun update(item: UserEntity)

    @Delete
    suspend fun delete(item: UserEntity)

    @Query("DELETE FROM v2_users")
    suspend fun deleteAll()
}
