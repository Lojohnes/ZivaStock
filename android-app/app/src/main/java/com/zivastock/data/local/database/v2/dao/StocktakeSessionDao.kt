
package com.zivastock.data.local.database.v2.dao

import androidx.room.*
import com.zivastock.data.local.database.v2.entities.StocktakeSessionEntity
import kotlinx.coroutines.flow.Flow

@Dao
interface StocktakeSessionDao {
    @Query("SELECT * FROM v2_stocktake_sessions")
    fun getAll(): Flow<List<StocktakeSessionEntity>>


    @Query("SELECT * FROM v2_stocktake_sessions WHERE id = :id")
    suspend fun getById(id: Long): StocktakeSessionEntity?

    @Query("""
        SELECT * FROM v2_stocktake_sessions
        WHERE status NOT IN ('completed', 'cancelled', 'closed')
        ORDER BY id DESC
        LIMIT 1
    """)
    fun getActiveSession(): Flow<StocktakeSessionEntity?>


    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(item: StocktakeSessionEntity): Long

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertAll(items: List<StocktakeSessionEntity>): List<Long>

    @Update
    suspend fun update(item: StocktakeSessionEntity)

    @Delete
    suspend fun delete(item: StocktakeSessionEntity)

    @Query("DELETE FROM v2_stocktake_sessions")
    suspend fun deleteAll()
}
