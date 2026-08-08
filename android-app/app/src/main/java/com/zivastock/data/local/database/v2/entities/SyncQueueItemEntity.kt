
        package com.zivastock.data.local.database.v2.entities

        import androidx.room.Entity
import androidx.room.PrimaryKey

        @Entity(tableName = "v2_sync_queue")
        data class SyncQueueItemEntity(
            @PrimaryKey
    val id: Long = 0,
        val tableName: String = "",
    val recordId: Long = 0,
    val operation: String = "insert",
    val payload: String = "",
    val status: String = "pending",
    val retryCount: Int = 0,
    val createdAt: String = "",
    val syncedAt: String? = null,
        )
