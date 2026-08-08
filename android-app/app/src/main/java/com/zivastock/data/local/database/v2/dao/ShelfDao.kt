
package com.zivastock.data.local.database.v2.dao

import androidx.room.*
import com.zivastock.data.local.database.v2.entities.ShelfEntity
import kotlinx.coroutines.flow.Flow

@Dao
interface ShelfDao {
    @Query("SELECT * FROM v2_shelves")
    fun getAll(): Flow<List<ShelfEntity>>


    @Query("SELECT * FROM v2_shelves WHERE id = :id")
    suspend fun getById(id: Long): ShelfEntity?


    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(item: ShelfEntity): Long

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertAll(items: List<ShelfEntity>): List<Long>

    @Update
    suspend fun update(item: ShelfEntity)

    @Delete
    suspend fun delete(item: ShelfEntity)

    @Query("DELETE FROM v2_shelves")
    suspend fun deleteAll()
}
