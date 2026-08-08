
    package com.zivastock.data.remote.dto.v2

    data class LoginResponseDto(
    val accessToken: String? = null,
val refreshToken: String? = null,
val tokenType: String? = null,
val user: UserDto? = null,
    )
