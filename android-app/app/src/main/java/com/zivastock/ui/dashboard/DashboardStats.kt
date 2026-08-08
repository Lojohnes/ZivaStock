package com.zivastock.ui.dashboard

import com.zivastock.data.local.database.v2.entities.StocktakeSessionEntity

data class DashboardStats(
    val activeSession: StocktakeSessionEntity? = null,
    val activeSessionLocationName: String = "",
    val activeSessionShelves: List<String> = emptyList(),
    val pendingSyncCount: Int = 0,
    val completedShelves: Int = 0,
    val completedSections: Int = 0,
    val productsCounted: Int = 0,
    val productsRemaining: Int = 0,
    val totalProducts: Int = 0,
    val varianceCount: Int = 0,
    val totalVariance: Double = 0.0,
    val totalShelves: Int = 0,
    val totalSections: Int = 0,
    val countedSectionsPercentage: Int = 0,
    val countedProductsPercentage: Int = 0
)

data class DashboardChartData(
    val groups: List<BarGroup>
) {
    data class BarGroup(
        val label: String,
        val bars: List<Bar>
    )

    data class Bar(
        val label: String,
        val value: Float,
        val color: Int
    )
}
