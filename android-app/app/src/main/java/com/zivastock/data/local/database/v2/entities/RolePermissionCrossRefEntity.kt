
    package com.zivastock.data.local.database.v2.entities

    import androidx.room.Entity

    @Entity(tableName = "v2_role_permissions", primaryKeys = ["roleId", "permissionId"])
    data class RolePermissionCrossRefEntity(
        val roleId: Long = 0,
val permissionId: Long = 0,
    val createdAt: String? = null,
    )
