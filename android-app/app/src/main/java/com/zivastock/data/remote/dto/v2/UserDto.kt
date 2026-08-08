
    package com.zivastock.data.remote.dto.v2

    data class UserDto(
    val id: Long? = null,
val uuid: String? = null,
val email: String? = null,
val firstName: String? = null,
val lastName: String? = null,
val phoneNumber: String? = null,
val roleId: Long? = null,
val isActive: Boolean? = null,
val isLocked: Boolean? = null,
val failedLoginAttempts: Int? = null,
val lastLoginAt: String? = null,
val passwordChangedAt: String? = null,
val createdAt: String? = null,
val updatedAt: String? = null,
    )
