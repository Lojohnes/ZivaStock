package com.zivastock.data.local.database.entities

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "products")
data class ProductEntity(
    @PrimaryKey
    val id: Int,
    val barcode: String,
    val productCode: String?,
    val description: String,
    val unitOfMeasure: String,
    val systemQuantity: Double,
    val unitCost: Double,
    val updatedAt: String,
    val syncedAt: String?
)
