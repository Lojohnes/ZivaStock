
package com.zivastock.data.local.database.v2.dao

import androidx.room.*
import com.zivastock.data.local.database.v2.entities.ShelfSectionEntity
import kotlinx.coroutines.flow.Flow

@Dao
interface ShelfSectionDao {
    @Query("SELECT * FROM v2_shelf_sections")
    fun getAll(): Flow<List<ShelfSectionEntity>>


    @Query("SELECT * FROM v2_shelf_sections WHERE id = :id")
    suspend fun getById(id: Long): ShelfSectionEntity?


    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(item: ShelfSectionEntity): Long

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertAll(items: List<ShelfSectionEntity>): List<Long>

    @Update
    suspend fun update(item: ShelfSectionEntity)

    @Delete
    suspend fun delete(item: ShelfSectionEntity)

    @Query("DELETE FROM v2_shelf_sections")
    suspend fun deleteAll()
}
