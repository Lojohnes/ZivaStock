package com.zivastock.data.remote.dto

data class SyncPushResponse(
    val success_count: Int,
    val failed_count: Int,
    val errors: List<String>
)
