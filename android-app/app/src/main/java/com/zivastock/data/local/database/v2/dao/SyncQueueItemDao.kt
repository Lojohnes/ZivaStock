
package com.zivastock.data.local.database.v2.dao

import androidx.room.*
import com.zivastock.data.local.database.v2.entities.SyncQueueItemEntity
import kotlinx.coroutines.flow.Flow

@Dao
interface SyncQueueItemDao {
    @Query("SELECT * FROM v2_sync_queue")
    fun getAll(): Flow<List<SyncQueueItemEntity>>

    @Query("SELECT * FROM v2_sync_queue WHERE id = :id")
    suspend fun getById(id: Long): SyncQueueItemEntity?

    @Query("SELECT * FROM v2_sync_queue WHERE tableName = :tableName AND recordId = :recordId AND operation = :operation LIMIT 1")
    suspend fun getByTableRecordOperation(tableName: String, recordId: Long, operation: String): SyncQueueItemEntity?

    @Query("SELECT * FROM v2_sync_queue WHERE status = 'pending' ORDER BY createdAt ASC")
    suspend fun getPending(): List<SyncQueueItemEntity>

    @Query("SELECT * FROM v2_sync_queue WHERE status IN ('pending', 'failed') AND retryCount < :maxRetries ORDER BY createdAt ASC")
    suspend fun getPendingOrFailed(maxRetries: Int = 3): List<SyncQueueItemEntity>

    @Query("SELECT COUNT(*) FROM v2_sync_queue WHERE status IN ('pending', 'failed')")
    fun countPending(): Flow<Int>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(item: SyncQueueItemEntity): Long

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertAll(items: List<SyncQueueItemEntity>): List<Long>

    @Query("UPDATE v2_sync_queue SET status = 'processing', retryCount = retryCount + 1 WHERE id = :id")
    suspend fun markAsProcessing(id: Long)

    @Query("UPDATE v2_sync_queue SET status = 'completed', syncedAt = :syncedAt WHERE id = :id")
    suspend fun markAsCompleted(id: Long, syncedAt: String)

    @Query("UPDATE v2_sync_queue SET status = 'failed' WHERE id = :id")
    suspend fun markAsFailed(id: Long)

    @Update
    suspend fun update(item: SyncQueueItemEntity)

    @Delete
    suspend fun delete(item: SyncQueueItemEntity)

    @Query("DELETE FROM v2_sync_queue")
    suspend fun deleteAll()
}
