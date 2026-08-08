
    package com.zivastock.data.local.database.v2.entities

    import androidx.room.Entity

    @Entity(tableName = "v2_user_roles", primaryKeys = ["userId", "roleId"])
    data class UserRoleCrossRefEntity(
        val userId: Long = 0,
val roleId: Long = 0,
    val createdAt: String? = null,
    )
