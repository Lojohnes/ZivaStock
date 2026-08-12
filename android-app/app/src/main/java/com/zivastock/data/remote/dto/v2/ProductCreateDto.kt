package com.zivastock.data.remote.dto.v2

data class ProductCreateDto(
    val barcode: String,
    val productCode: String? = null,
    val description: String,
    val unitOfMeasure: String = "EA",
    val systemQuantity: Double = 0.0,
    val unitCost: Double = 0.0,
)
