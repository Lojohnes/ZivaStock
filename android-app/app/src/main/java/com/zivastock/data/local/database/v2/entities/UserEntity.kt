
        package com.zivastock.data.local.database.v2.entities

        import androidx.room.Entity
import androidx.room.PrimaryKey

        @Entity(tableName = "v2_users")
        data class UserEntity(
            @PrimaryKey
    val id: Long = 0,
        val uuid: String = "",
    val email: String = "",
    val firstName: String = "",
    val lastName: String = "",
    val phoneNumber: String? = null,
    val roleId: Long = 0,
    val isActive: Boolean = true,
    val isLocked: Boolean = false,
    val failedLoginAttempts: Int = 0,
    val lastLoginAt: String? = null,
    val passwordChangedAt: String? = null,
    val createdAt: String? = null,
    val updatedAt: String? = null,
        )
