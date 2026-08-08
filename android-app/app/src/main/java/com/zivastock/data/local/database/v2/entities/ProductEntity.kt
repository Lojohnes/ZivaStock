
        package com.zivastock.data.local.database.v2.entities

        import androidx.room.Entity
import androidx.room.PrimaryKey

        @Entity(tableName = "v2_products")
        data class ProductEntity(
            @PrimaryKey
    val id: Long = 0,
        val sku: String? = null,
    val barcode: String = "",
    val productCode: String? = null,
    val categoryId: Long? = null,
    val description: String = "",
    val unitOfMeasure: String = "EA",
    val systemQuantity: Double = 0.0,
    val unitCost: Double = 0.0,
    val unitPrice: Double = 0.0,
    val reorderLevel: Double = 0.0,
    val isActive: Boolean = true,
    val createdAt: String? = null,
    val updatedAt: String? = null,
        )
