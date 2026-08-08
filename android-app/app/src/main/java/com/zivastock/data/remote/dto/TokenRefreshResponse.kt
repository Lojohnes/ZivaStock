package com.zivastock.data.remote.dto

data class TokenRefreshResponse(
    val access_token: String,
    val token_type: String,
    val expires_in: Int
)
