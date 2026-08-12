package com.zivastock.data.remote.dto.v2

data class RegisterRequestDto(
    val email: String,
    val firstName: String,
    val lastName: String,
    val password: String,
)
