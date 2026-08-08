package com.zivastock.data.remote.dto

data class LoginResponse(
    val access_token: String,
    val refresh_token: String,
    val token_type: String,
    val expires_in: Int,
    val user: UserDto
)

data class UserDto(
    val id: Int,
    val email: String,
    val first_name: String,
    val last_name: String,
    val role_id: Int,
    val is_active: Boolean
)
