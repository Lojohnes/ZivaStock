
        package com.zivastock.data.local.database.v2.entities

        import androidx.room.Entity
import androidx.room.PrimaryKey

        @Entity(tableName = "v2_roles")
        data class RoleEntity(
            @PrimaryKey
    val id: Long = 0,
        val name: String = "",
    val description: String? = null,
    val isSystem: Boolean = false,
    val createdAt: String? = null,
    val updatedAt: String? = null,
        )
