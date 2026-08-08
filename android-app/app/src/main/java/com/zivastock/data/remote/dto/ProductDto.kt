package com.zivastock.data.remote.dto

data class ProductDto(
    val id: Int,
    val barcode: String,
    val product_code: String?,
    val description: String,
    val unit_of_measure: String,
    val system_quantity: Double,
    val unit_cost: Double,
    val updated_at: String
)
