
        package com.zivastock.data.local.database.v2.entities

        import androidx.room.Entity
import androidx.room.PrimaryKey

        @Entity(tableName = "v2_permissions")
        data class PermissionEntity(
            @PrimaryKey
    val id: Long = 0,
        val name: String = "",
    val description: String? = null,
    val module: String = "",
    val createdAt: String? = null,
    val updatedAt: String? = null,
        )
