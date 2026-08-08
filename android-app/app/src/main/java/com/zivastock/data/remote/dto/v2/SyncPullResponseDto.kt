
    package com.zivastock.data.remote.dto.v2

    data class SyncPullResponseDto(
    val products: List<ProductDto>? = null,
val firstCounts: List<FirstCountDto>? = null,
val secondCounts: List<SecondCountDto>? = null,
val locations: List<LocationDto>? = null,
val sessions: List<StocktakeSessionDto>? = null,
val syncTimestamp: String? = null,
    )
