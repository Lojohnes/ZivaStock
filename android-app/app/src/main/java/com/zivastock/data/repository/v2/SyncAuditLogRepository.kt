package com.zivastock.data.repository.v2

import com.zivastock.data.local.database.ZivaStockDatabase
import com.zivastock.data.local.database.v2.entities.SyncAuditLogEntity
import kotlinx.coroutines.flow.Flow
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class SyncAuditLogRepository @Inject constructor(
    private val database: ZivaStockDatabase
) {

    private val dao = database.syncAuditLogDao()
    private val dateFormat = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss", Locale.getDefault())

    fun getAll(): Flow<List<SyncAuditLogEntity>> = dao.getAll()

    suspend fun log(
        operation: String,
        entityType: String,
        entityId: Long? = null,
        status: String,
        message: String,
        details: String? = null
    ) {
        val entry = SyncAuditLogEntity(
            timestamp = dateFormat.format(Date()),
            operation = operation,
            entityType = entityType,
            entityId = entityId,
            status = status,
            message = message,
            details = details
        )
        dao.insert(entry)
    }

    suspend fun getRecent(limit: Int = 100): List<SyncAuditLogEntity> {
        return dao.getRecent(limit)
    }

    suspend fun clear() {
        dao.deleteAll()
    }
}
