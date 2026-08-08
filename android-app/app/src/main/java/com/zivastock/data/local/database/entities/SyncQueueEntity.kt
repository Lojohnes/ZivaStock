package com.zivastock.data.local.database.entities

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "sync_queue")
data class SyncQueueEntity(
    @PrimaryKey(autoGenerate = true)
    val id: Int = 0,
    val entityType: String,
    val entityId: Int?,
    val action: String,
    val payload: String,
    val retryCount: Int = 0,
    val lastAttempt: String?,
    val status: String,
    val errorMessage: String?,
    val createdAt: String
)
