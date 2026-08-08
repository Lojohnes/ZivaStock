package com.zivastock.data.remote.dto

data class SyncPushRequest(
    val counts: List<CountDto>
)

data class CountDto(
    val product_id: Int,
    val section_id: Int,
    val quantity: Double,
    val session_id: Int,
    val counted_at: String
)
