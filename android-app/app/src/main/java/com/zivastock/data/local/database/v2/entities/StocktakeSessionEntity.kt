
        package com.zivastock.data.local.database.v2.entities

        import androidx.room.Entity
import androidx.room.PrimaryKey

        @Entity(tableName = "v2_stocktake_sessions")
        data class StocktakeSessionEntity(
            @PrimaryKey
    val id: Long = 0,
        val uuid: String = "",
    val name: String = "",
    val description: String? = null,
    val locationId: Long = 0,
    val sessionType: String = "full",
    val status: String = "not_started",
    val startTime: String? = null,
    val endTime: String? = null,
    val createdBy: Long = 0,
    val approvedBy: Long? = null,
    val approvedAt: String? = null,
    val createdAt: String? = null,
    val updatedAt: String? = null,
        )
