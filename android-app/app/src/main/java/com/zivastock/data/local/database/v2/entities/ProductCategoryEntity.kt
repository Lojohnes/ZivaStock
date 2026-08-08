
        package com.zivastock.data.local.database.v2.entities

        import androidx.room.Entity
import androidx.room.PrimaryKey

        @Entity(tableName = "v2_product_categories")
        data class ProductCategoryEntity(
            @PrimaryKey
    val id: Long = 0,
        val name: String = "",
    val parentId: Long? = null,
    val description: String? = null,
    val isActive: Boolean = true,
    val createdAt: String? = null,
    val updatedAt: String? = null,
        )
