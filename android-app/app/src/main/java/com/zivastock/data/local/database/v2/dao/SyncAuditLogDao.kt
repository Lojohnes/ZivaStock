package com.zivastock.data.local.database.v2.dao

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import com.zivastock.data.local.database.v2.entities.SyncAuditLogEntity
import kotlinx.coroutines.flow.Flow

@Dao
interface SyncAuditLogDao {

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(item: SyncAuditLogEntity): Long

    @Query("SELECT * FROM v2_sync_audit_logs ORDER BY timestamp DESC")
    fun getAll(): Flow<List<SyncAuditLogEntity>>

    @Query("SELECT * FROM v2_sync_audit_logs ORDER BY timestamp DESC LIMIT :limit")
    suspend fun getRecent(limit: Int = 100): List<SyncAuditLogEntity>

    @Query("DELETE FROM v2_sync_audit_logs")
    suspend fun deleteAll()
}
