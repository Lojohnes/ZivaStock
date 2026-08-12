
package com.zivastock.data.repository.v2

import androidx.room.withTransaction
import com.zivastock.data.local.database.ZivaStockDatabase
import com.zivastock.data.local.database.v2.entities.SecondCountEntity
import com.zivastock.data.local.preferences.SecureTokenManager
import com.zivastock.data.remote.api.ZivaStockApi
import com.zivastock.data.remote.dto.v2.SecondCountDto
import com.zivastock.data.repository.v2.SyncAuditLogRepository
import com.zivastock.sync.ConflictResolver
import com.zivastock.sync.SyncQueueManager
import com.zivastock.utils.NetworkUtils
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.first
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale
import javax.inject.Inject

class SecondCountRepository @Inject constructor(
    private val database: ZivaStockDatabase,
    private val api: ZivaStockApi,
    private val secureTokenManager: SecureTokenManager,
    private val networkUtils: NetworkUtils,
    private val syncQueueManager: SyncQueueManager,
    private val auditLogRepository: SyncAuditLogRepository
) {
    private val dao = database.secondCountDao()
    private val dateFormat = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss", Locale.getDefault())
    private val queueTable = "v2_second_counts"

    fun getAll(): Flow<List<SecondCountEntity>> = dao.getAll()

    suspend fun getById(id: Long): SecondCountEntity? = dao.getById(id)

    suspend fun save(entity: SecondCountEntity): Long {
        val id = database.withTransaction {
            val existing = dao.findByScope(entity.sessionId, entity.productId, entity.userId, entity.fileNumber, entity.sectionNumber)
            val saved = if (existing != null) {
                entity.copy(id = existing.id)
            } else {
                entity.copy(id = dao.insert(entity))
            }
            if (existing != null) dao.update(saved)
            syncQueueManager.enqueue(
                tableName = queueTable,
                recordId = saved.id,
                operation = "insert",
                payload = saved
            )
            saved.id
        }

        auditLogRepository.log(
            operation = "save",
            entityType = queueTable,
            entityId = id,
            status = "success",
            message = "Second count saved locally",
            details = "sessionId=${entity.sessionId}, productId=${entity.productId}"
        )

        tryPush(listOf(entity.copy(id = id)))
        return id
    }

    suspend fun syncUnsynced(): Result<Int> {
        val unsynced = dao.getUnsynced().first()
        return if (unsynced.isEmpty()) {
            Result.success(0)
        } else {
            tryPush(unsynced)
        }
    }

    private suspend fun tryPush(entities: List<SecondCountEntity>): Result<Int> {
        if (!networkUtils.isNetworkAvailable()) {
            logFailure(entities, "No network - queued for later")
            return Result.failure(Exception("No network"))
        }
        if (secureTokenManager.getAccessToken().isNullOrBlank()) {
            logFailure(entities, "Not authenticated - queued for later")
            return Result.failure(Exception("Not authenticated"))
        }

        return try {
            val dtos = entities.map { it.toDto() }
            val response = api.createSecondCounts(dtos)

            if (response.isSuccessful && response.body() != null) {
                val syncedAt = dateFormat.format(Date())
                val serverDtos = response.body()!!

                entities.forEach { local ->
                    val remote = serverDtos.find {
                        it.sessionId == local.sessionId &&
                        it.productId == local.productId &&
                        it.shelfSectionId == local.shelfSectionId &&
                        it.fileNumber == local.fileNumber &&
                        it.sectionNumber == local.sectionNumber
                    }

                    if (remote != null) {
                        when (ConflictResolver.resolve(local.countedAt, remote.countedAt)) {
                            ConflictResolver.Resolution.USE_REMOTE -> {
                                dao.update(local.copy(
                                    quantity = remote.quantity ?: local.quantity,
                                    countedAt = remote.countedAt ?: local.countedAt,
                                    isSynced = true,
                                    syncedAt = syncedAt
                                ))
                                auditLogRepository.log(
                                    operation = "conflict_resolution",
                                    entityType = queueTable,
                                    entityId = local.id,
                                    status = "resolved",
                                    message = "Server count accepted as newer",
                                    details = "localCountedAt=${local.countedAt}, remoteCountedAt=${remote.countedAt}"
                                )
                            }
                            ConflictResolver.Resolution.USE_LOCAL,
                            ConflictResolver.Resolution.MERGE -> {
                                dao.markAsSynced(local.id, syncedAt)
                            }
                        }
                    } else {
                        dao.markAsSynced(local.id, syncedAt)
                    }

                    syncQueueManager.markCompleted(queueTable, local.id)
                }

                auditLogRepository.log(
                    operation = "push",
                    entityType = queueTable,
                    status = "success",
                    message = "Pushed ${entities.size} second count(s)",
                    details = "syncedAt=$syncedAt"
                )

                Result.success(entities.size)
            } else if (response.code() == 409) {
                logFailure(entities, "Conflict: ${response.errorBody()?.string()}")
                Result.failure(Exception("Conflict: ${response.code()}"))
            } else {
                logFailure(entities, "Push failed: ${response.code()}")
                Result.failure(Exception("Push failed: ${response.code()}"))
            }
        } catch (e: Exception) {
            logFailure(entities, e.message ?: "Network exception")
            Result.failure(e)
        }
    }

    private suspend fun logFailure(entities: List<SecondCountEntity>, reason: String) {
        entities.forEach {
            syncQueueManager.markFailed(queueTable, it.id, reason = reason)
        }
        auditLogRepository.log(
            operation = "push",
            entityType = queueTable,
            status = "failure",
            message = reason,
            details = "count=${entities.size}"
        )
    }

    suspend fun saveAll(entities: List<SecondCountEntity>) {
        dao.insertAll(entities)
    }

    suspend fun delete(entity: SecondCountEntity) {
        dao.delete(entity)
    }

    suspend fun fetchFromServer() {
        // Second counts are only pushed from mobile
    }

    private fun SecondCountEntity.toDto(): SecondCountDto {
        return SecondCountDto(
            id = if (id == 0L) null else id,
            sessionId = sessionId,
            productId = productId,
            shelfSectionId = shelfSectionId,
            userId = userId,
            fileNumber = fileNumber,
            sectionNumber = sectionNumber,
            firstCountId = firstCountId,
            quantity = quantity,
            clientId = clientId,
            deviceId = deviceId,
            source = source,
            countedAt = countedAt,
            isSynced = isSynced,
            syncedAt = syncedAt
        )
    }
}
