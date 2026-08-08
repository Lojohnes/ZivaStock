package com.zivastock.data.session

data class ActiveSessionDetails(
    val id: Long,
    val name: String,
    val description: String?,
    val status: String,
    val locationName: String,
    val sessionType: String,
    val shelves: List<String>
)
