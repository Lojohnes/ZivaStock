package com.zivastock.data.repository

import com.zivastock.data.local.database.dao.SyncQueueDao
import com.zivastock.data.local.database.entities.SyncQueueEntity
import com.zivastock.data.remote.api.ApiService
import com.zivastock.data.remote.dto.CountDto
import com.zivastock.data.remote.dto.SyncPullResponse
import com.zivastock.data.remote.dto.SyncPushRequest
import com.zivastock.data.remote.dto.SyncPushResponse
import com.google.gson.Gson
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class SyncRepository @Inject constructor(
    private val syncQueueDao: SyncQueueDao,
    private val apiService: ApiService
) {
    
    private val gson = Gson()
    private val dateFormat = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss", Locale.getDefault())
    
    suspend fun addToSyncQueue(
        entityType: String,
        entityId: Int?,
        action: String,
        payload: Any
    ) {
        val payloadJson = gson.toJson(payload)
        val syncItem = SyncQueueEntity(
            entityType = entityType,
            entityId = entityId,
            action = action,
            payload = payloadJson,
            status = "pending",
            lastAttempt = null,
            errorMessage = null,
            createdAt = dateFormat.format(Date())
        )
        syncQueueDao.insertSyncItem(syncItem)
    }
    
    suspend fun getPendingSyncItems(): List<SyncQueueEntity> {
        return syncQueueDao.getPendingSyncItems()
    }
    
    suspend fun pushCountsToServer(token: String, counts: List<CountDto>): SyncPushResponse? {
        val request = SyncPushRequest(counts = counts)
        val response = apiService.pushCounts(token, request)
        return if (response.isSuccessful) {
            response.body()
        } else {
            null
        }
    }
    
    suspend fun pullDataFromServer(token: String, lastSync: String?): SyncPullResponse? {
        val response = apiService.pullData(token, lastSync)
        return if (response.isSuccessful) {
            response.body()
        } else {
            null
        }
    }
    
    suspend fun getSyncStatus(token: String): com.zivastock.data.remote.dto.SyncStatusResponse? {
        val response = apiService.getSyncStatus(token)
        return if (response.isSuccessful) {
            response.body()
        } else {
            null
        }
    }
    
    suspend fun updateSyncItemStatus(id: Int, status: String) {
        val lastAttempt = dateFormat.format(Date())
        syncQueueDao.updateSyncItemStatus(id, status, lastAttempt)
    }
    
    suspend fun updateSyncItemError(id: Int, errorMessage: String) {
        syncQueueDao.updateSyncItemError(id, errorMessage)
    }
    
    suspend fun deleteSyncItem(id: Int) {
        syncQueueDao.deleteSyncItem(id)
    }
    
    suspend fun deleteCompletedSyncItems() {
        syncQueueDao.deleteCompletedSyncItems()
    }
    
    suspend fun getPendingSyncCount(): Int {
        return syncQueueDao.getPendingSyncCount()
    }

    suspend fun pushPending() {
        // TODO: flush pending counts to backend
    }

    suspend fun pullLatest() {
        // TODO: pull products / locations from backend
    }
}
