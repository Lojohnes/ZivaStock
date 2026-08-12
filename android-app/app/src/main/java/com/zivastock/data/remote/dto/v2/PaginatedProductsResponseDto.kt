package com.zivastock.data.remote.dto.v2

data class PaginatedProductsResponseDto(
    val items: List<ProductDto> = emptyList(),
    val total: Int = 0,
    val page: Int = 1,
    val limit: Int = 100,
    val pages: Int = 0,
)
