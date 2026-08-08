package com.zivastock.data.local.database.dao

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import com.zivastock.data.local.database.entities.CountEntity

@Dao
interface CountDao {
    
    @Query("SELECT * FROM counts WHERE id = :id LIMIT 1")
    suspend fun getCountById(id: Int): CountEntity?
    
    @Query("SELECT * FROM counts WHERE sessionId = :sessionId AND sectionId = :sectionId")
    suspend fun getCountsBySessionAndSection(sessionId: Int, sectionId: Int): List<CountEntity>
    
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertCount(count: CountEntity)
    
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertCounts(counts: List<CountEntity>)
    
    @Query("SELECT * FROM counts WHERE isSynced = 0")
    suspend fun getUnsyncedCounts(): List<CountEntity>
    
    @Query("UPDATE counts SET isSynced = 1, syncedAt = :syncedAt WHERE id = :id")
    suspend fun markCountAsSynced(id: Int, syncedAt: String)
    
    @Query("DELETE FROM counts WHERE id = :id")
    suspend fun deleteCount(id: Int)
}
