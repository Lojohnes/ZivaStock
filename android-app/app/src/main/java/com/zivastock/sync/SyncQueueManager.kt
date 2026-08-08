package com.zivastock.sync

import com.zivastock.data.local.database.ZivaStockDatabase
import com.zivastock.data.local.database.v2.entities.SyncQueueItemEntity
import com.zivastock.data.repository.v2.SyncAuditLogRepository
import com.google.gson.Gson
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class SyncQueueManager @Inject constructor(
    private val database: ZivaStockDatabase,
    private val auditLogRepository: SyncAuditLogRepository
) {

    private val dao = database.syncQueueItemDao()
    private val gson = Gson()
    private val dateFormat = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss", Locale.getDefault())

    suspend fun enqueue(tableName: String, recordId: Long, operation: String, payload: Any) {
        val existing = dao.getByTableRecordOperation(tableName, recordId, operation)
        if (existing != null && existing.status != "completed") {
            // Already queued; deduplicate
            return
        }

        val item = SyncQueueItemEntity(
            tableName = tableName,
            recordId = recordId,
            operation = operation,
            payload = gson.toJson(payload),
            status = "pending",
            retryCount = 0,
            createdAt = dateFormat.format(Date()),
            syncedAt = null
        )

        val id = dao.insert(item)

        auditLogRepository.log(
            operation = "enqueue",
            entityType = tableName,
            entityId = recordId,
            status = "success",
            message = "$operation queued for $tableName:$recordId",
            details = "queueId=$id"
        )
    }

    suspend fun markCompleted(tableName: String, recordId: Long, operation: String = "insert") {
        val existing = dao.getByTableRecordOperation(tableName, recordId, operation) ?: return
        dao.markAsCompleted(existing.id, dateFormat.format(Date()))
    }

    suspend fun markProcessing(id: Long) {
        dao.markAsProcessing(id)
    }

    suspend fun markFailed(tableName: String, recordId: Long, operation: String = "insert", reason: String) {
        val existing = dao.getByTableRecordOperation(tableName, recordId, operation) ?: return
        dao.markAsFailed(existing.id)
        auditLogRepository.log(
            operation = "sync_failed",
            entityType = tableName,
            entityId = recordId,
            status = "failure",
            message = reason,
            details = "queueId=${existing.id}"
        )
    }

    suspend fun getPending(): List<SyncQueueItemEntity> {
        return dao.getPendingOrFailed()
    }
}
