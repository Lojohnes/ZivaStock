package com.zivastock.data.remote.dto.v2

data class SessionsResponseDto(
    val items: List<StocktakeSessionDto> = emptyList(),
    val total: Int = 0,
    val page: Int = 1,
    val limit: Int = 20,
    val pages: Int = 0,
)
