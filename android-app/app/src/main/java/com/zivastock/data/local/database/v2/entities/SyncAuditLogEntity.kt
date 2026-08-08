package com.zivastock.data.local.database.v2.entities

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "v2_sync_audit_logs")
data class SyncAuditLogEntity(
    @PrimaryKey(autoGenerate = true)
    val id: Long = 0,
    val timestamp: String = "",
    val operation: String = "",
    val entityType: String = "",
    val entityId: Long? = null,
    val status: String = "",
    val message: String = "",
    val details: String? = null
)
