package com.zivastock.sync

import com.zivastock.data.local.database.dao.CountDao
import com.zivastock.data.local.database.dao.ProductDao
import com.zivastock.data.local.database.entities.ProductEntity
import com.zivastock.data.local.preferences.SecureTokenManager
import com.zivastock.data.local.preferences.SharedPreferencesManager
import com.zivastock.data.remote.dto.CountDto
import com.zivastock.data.repository.SyncRepository
import com.zivastock.data.repository.v2.FirstCountRepository
import com.zivastock.data.repository.v2.SecondCountRepository
import com.zivastock.data.repository.v2.SyncAuditLogRepository
import com.zivastock.utils.NetworkUtils
import kotlinx.coroutines.coroutineScope
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.firstOrNull
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class SyncEngine @Inject constructor(
    private val syncRepository: SyncRepository,
    private val productDao: ProductDao,
    private val countDao: CountDao,
    private val firstCountRepository: FirstCountRepository,
    private val secondCountRepository: SecondCountRepository,
    private val auditLogRepository: SyncAuditLogRepository,
    private val syncQueueManager: SyncQueueManager,
    private val networkUtils: NetworkUtils,
    private val secureTokenManager: SecureTokenManager,
    private val sharedPreferencesManager: SharedPreferencesManager
) {
    
    private val dateFormat = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss", Locale.getDefault())

    suspend fun performSync() = coroutineScope {
        auditLogRepository.log(
            operation = "sync_start",
            entityType = "sync",
            status = "info",
            message = "Starting background synchronization",
            details = "network=${networkUtils.isNetworkAvailable()}"
        )

        if (!networkUtils.isNetworkAvailable()) {
            auditLogRepository.log(
                operation = "sync_skip",
                entityType = "sync",
                status = "info",
                message = "No network connection; sync deferred",
            )
            throw Exception("No network")
        }

        val accessToken = secureTokenManager.getAccessToken()

        if (accessToken == null) {
            auditLogRepository.log(
                operation = "sync_skip",
                entityType = "sync",
                status = "info",
                message = "No access token; sync deferred",
            )
            throw Exception("Not authenticated")
        }

        try {
            // Step 1: Push unsynced v1 counts
            val unsyncedCounts = countDao.getUnsyncedCounts()
            if (unsyncedCounts.isNotEmpty()) {
                val countDtos = unsyncedCounts.map { count ->
                    CountDto(
                        product_id = count.productId,
                        section_id = count.sectionId,
                        quantity = count.quantity,
                        session_id = count.sessionId,
                        counted_at = count.countedAt
                    )
                }

                val pushResponse = syncRepository.pushCountsToServer(accessToken, countDtos)
                if (pushResponse != null && pushResponse.success_count > 0) {
                    val syncedAt = dateFormat.format(Date())
                    unsyncedCounts.forEach { count ->
                        countDao.markCountAsSynced(count.id, syncedAt)
                    }
                    auditLogRepository.log(
                        operation = "push",
                        entityType = "v1_counts",
                        status = "success",
                        message = "Pushed ${pushResponse.success_count} v1 count(s)",
                        details = "syncedAt=$syncedAt"
                    )
                } else {
                    auditLogRepository.log(
                        operation = "push",
                        entityType = "v1_counts",
                        status = "failure",
                        message = "Failed to push v1 counts",
                        details = "response=$pushResponse"
                    )
                }
            }

            // Step 2: Push unsynced v2 first counts
            firstCountRepository.syncUnsynced().onSuccess { count ->
                if (count > 0) {
                    auditLogRepository.log(
                        operation = "push",
                        entityType = "v2_first_counts",
                        status = "success",
                        message = "Pushed $count first count(s)",
                    )
                }
            }.onFailure { error ->
                auditLogRepository.log(
                    operation = "push",
                    entityType = "v2_first_counts",
                    status = "failure",
                    message = error.message ?: "First count push failed",
                )
            }

            // Step 3: Push unsynced v2 second counts
            secondCountRepository.syncUnsynced().onSuccess { count ->
                if (count > 0) {
                    auditLogRepository.log(
                        operation = "push",
                        entityType = "v2_second_counts",
                        status = "success",
                        message = "Pushed $count second count(s)",
                    )
                }
            }.onFailure { error ->
                auditLogRepository.log(
                    operation = "push",
                    entityType = "v2_second_counts",
                    status = "failure",
                    message = error.message ?: "Second count push failed",
                )
            }

            // Step 4: Process generic v2 sync queue
            processSyncQueue()

            // Step 5: Pull latest data from server
            val lastSync = sharedPreferencesManager.lastSyncTimestamp.firstOrNull()

            val pullResponse = syncRepository.pullDataFromServer(accessToken, lastSync)
            if (pullResponse != null) {
                val products = pullResponse.products.map { dto ->
                    ProductEntity(
                        id = dto.id,
                        barcode = dto.barcode,
                        productCode = dto.product_code,
                        description = dto.description,
                        unitOfMeasure = dto.unit_of_measure,
                        systemQuantity = dto.system_quantity,
                        unitCost = dto.unit_cost,
                        updatedAt = dto.updated_at,
                        syncedAt = pullResponse.sync_timestamp
                    )
                }
                productDao.insertProducts(products)

                sharedPreferencesManager.updateLastSyncTimestamp(pullResponse.sync_timestamp)

                auditLogRepository.log(
                    operation = "pull",
                    entityType = "products",
                    status = "success",
                    message = "Pulled ${products.size} product(s)",
                    details = "syncTimestamp=${pullResponse.sync_timestamp}"
                )
            } else {
                auditLogRepository.log(
                    operation = "pull",
                    entityType = "products",
                    status = "failure",
                    message = "Pull returned no data",
                )
            }

            auditLogRepository.log(
                operation = "sync_complete",
                entityType = "sync",
                status = "success",
                message = "Background synchronization completed",
            )
        } catch (e: Exception) {
            auditLogRepository.log(
                operation = "sync_error",
                entityType = "sync",
                status = "failure",
                message = e.message ?: "Sync failed",
                details = e.stackTraceToString()
            )
            throw e
        }
    }

    private suspend fun processSyncQueue() {
        val pendingItems = syncQueueManager.getPending()
        if (pendingItems.isEmpty()) return

        for (item in pendingItems) {
            if (item.retryCount >= 3) {
                auditLogRepository.log(
                    operation = "queue_max_retries",
                    entityType = item.tableName,
                    entityId = item.recordId,
                    status = "failure",
                    message = "Max retries exceeded for queue item",
                    details = "queueId=${item.id}"
                )
                continue
            }

            syncQueueManager.markProcessing(item.id)
            delay(100)

            if (item.tableName == "v2_first_counts" || item.tableName == "v2_second_counts") {
                // Counts are handled by their dedicated repositories which update queue status.
                continue
            }

            // For other tables, mark as completed as a placeholder until dedicated handlers exist.
            syncQueueManager.markCompleted(item.tableName, item.recordId)

            auditLogRepository.log(
                operation = "queue_process",
                entityType = item.tableName,
                entityId = item.recordId,
                status = "success",
                message = "Processed queue item",
                details = "queueId=${item.id}"
            )
        }
    }
}
