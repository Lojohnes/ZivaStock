package com.zivastock.data.remote.dto

data class SyncPullResponse(
    val products: List<ProductDto>,
    val counts: List<CountDto>,
    val sections: List<SectionDto>,
    val sync_timestamp: String
)

data class SectionDto(
    val id: Int,
    val shelf_id: Int,
    val name: String,
    val description: String?,
    val updated_at: String
)
