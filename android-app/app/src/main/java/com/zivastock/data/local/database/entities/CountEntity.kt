package com.zivastock.data.local.database.entities

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "counts")
data class CountEntity(
    @PrimaryKey
    val id: Int,
    val productId: Int,
    val sectionId: Int,
    val quantity: Double,
    val userId: Int,
    val sessionId: Int,
    val countedAt: String,
    val syncedAt: String?,
    val isSynced: Boolean
)
