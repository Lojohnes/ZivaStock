package com.zivastock.data.remote.dto

data class SyncStatusResponse(
    val pending_sync_count: Int,
    val last_sync_at: String?,
    val sync_status: String
)
