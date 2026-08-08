package com.zivastock.data.local.database.dao

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import com.zivastock.data.local.database.entities.SyncQueueEntity

@Dao
interface SyncQueueDao {
    
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertSyncItem(item: SyncQueueEntity)
    
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertSyncItems(items: List<SyncQueueEntity>)
    
    @Query("SELECT * FROM sync_queue WHERE status = 'pending' ORDER BY createdAt ASC")
    suspend fun getPendingSyncItems(): List<SyncQueueEntity>
    
    @Query("UPDATE sync_queue SET status = :status, retryCount = retryCount + 1, lastAttempt = :lastAttempt WHERE id = :id")
    suspend fun updateSyncItemStatus(id: Int, status: String, lastAttempt: String)
    
    @Query("UPDATE sync_queue SET errorMessage = :errorMessage WHERE id = :id")
    suspend fun updateSyncItemError(id: Int, errorMessage: String)
    
    @Query("DELETE FROM sync_queue WHERE id = :id")
    suspend fun deleteSyncItem(id: Int)
    
    @Query("DELETE FROM sync_queue WHERE status = 'completed'")
    suspend fun deleteCompletedSyncItems()
    
    @Query("SELECT COUNT(*) FROM sync_queue WHERE status = 'pending'")
    suspend fun getPendingSyncCount(): Int
}
