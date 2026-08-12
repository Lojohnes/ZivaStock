
        package com.zivastock.data.local.database.v2.entities

        import androidx.room.Entity
import androidx.room.PrimaryKey

        @Entity(tableName = "v2_second_counts")
        data class SecondCountEntity(
            @PrimaryKey
    val id: Long = 0,
        val sessionId: Long = 0,
    val productId: Long = 0,
    val shelfSectionId: Long = 0,
    val userId: Long = 0,
    val firstCountId: Long? = null,
    val fileNumber: String? = null,
    val sectionNumber: String? = null,
    val remarks: String? = null,
    val quantity: Double = 0.0,
    val clientId: String? = null,
    val deviceId: String? = null,
    val source: String = "mobile",
    val countedAt: String = "",
    val isSynced: Boolean = false,
    val syncedAt: String? = null,
        )
