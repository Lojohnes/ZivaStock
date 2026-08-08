
package com.zivastock.data.local.database.v2.dao

import androidx.room.*
import com.zivastock.data.local.database.v2.entities.LocationEntity
import kotlinx.coroutines.flow.Flow

@Dao
interface LocationDao {
    @Query("SELECT * FROM v2_locations")
    fun getAll(): Flow<List<LocationEntity>>


    @Query("SELECT * FROM v2_locations WHERE id = :id")
    suspend fun getById(id: Long): LocationEntity?


    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(item: LocationEntity): Long

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertAll(items: List<LocationEntity>): List<Long>

    @Update
    suspend fun update(item: LocationEntity)

    @Delete
    suspend fun delete(item: LocationEntity)

    @Query("DELETE FROM v2_locations")
    suspend fun deleteAll()
}
