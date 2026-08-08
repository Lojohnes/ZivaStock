package com.zivastock.data.repository.v2

import com.zivastock.data.local.database.ZivaStockDatabase
import com.zivastock.data.local.database.v2.entities.FirstCountEntity
import com.zivastock.data.local.database.v2.entities.ProductEntity
import com.zivastock.data.local.database.v2.entities.SecondCountEntity
import com.zivastock.data.local.database.v2.entities.ShelfEntity
import com.zivastock.data.local.database.v2.entities.ShelfSectionEntity
import com.zivastock.data.local.database.v2.entities.StocktakeSessionEntity
import com.zivastock.data.session.SessionManager
import com.zivastock.ui.dashboard.DashboardChartData
import com.zivastock.ui.dashboard.DashboardStats
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.combine
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class DashboardRepository @Inject constructor(
    private val database: ZivaStockDatabase,
    private val sessionManager: SessionManager
) {

    private val firstCountDao = database.firstCountDao()
    private val secondCountDao = database.secondCountDao()
    private val productDao = database.productDao()
    private val shelfDao = database.shelfDao()
    private val shelfSectionDao = database.shelfSectionDao()
    private val syncQueueItemDao = database.syncQueueItemDao()

    fun getDashboardStats(): Flow<DashboardStats> = combine(
        sessionManager.activeSession,
        firstCountDao.getAll(),
        secondCountDao.getAll(),
        productDao.getAll(),
        syncQueueItemDao.countPending(),
        shelfDao.getAll(),
        shelfSectionDao.getAll()
    ) { values ->
        val activeSession = values[0] as StocktakeSessionEntity?
        val firstCounts = values[1] as List<FirstCountEntity>
        val secondCounts = values[2] as List<SecondCountEntity>
        val products = values[3] as List<ProductEntity>
        val pendingSync = values[4] as Int
        val shelves = values[5] as List<ShelfEntity>
        val sections = values[6] as List<ShelfSectionEntity>
        computeStats(activeSession, firstCounts, secondCounts, products, pendingSync, shelves, sections)
    }

    fun getChartData(stats: DashboardStats): DashboardChartData {
        val productsCounted = stats.productsCounted.toFloat()
        val productsRemaining = stats.productsRemaining.toFloat().coerceAtLeast(0f)
        val sectionsCompleted = stats.completedSections.toFloat()
        val sectionsRemaining = (stats.totalSections - stats.completedSections).toFloat().coerceAtLeast(0f)

        return DashboardChartData(
            groups = listOf(
                DashboardChartData.BarGroup(
                    label = "Products",
                    bars = listOf(
                        DashboardChartData.Bar("Counted", productsCounted, 0xFF00838F.toInt()),
                        DashboardChartData.Bar("Remaining", productsRemaining, 0xFFB0BEC5.toInt())
                    )
                ),
                DashboardChartData.BarGroup(
                    label = "Sections",
                    bars = listOf(
                        DashboardChartData.Bar("Completed", sectionsCompleted, 0xFF2E7D32.toInt()),
                        DashboardChartData.Bar("Remaining", sectionsRemaining, 0xFFB0BEC5.toInt())
                    )
                )
            )
        )
    }

    private fun computeStats(
        activeSession: StocktakeSessionEntity?,
        firstCounts: List<FirstCountEntity>,
        secondCounts: List<SecondCountEntity>,
        products: List<ProductEntity>,
        pendingSync: Int,
        shelves: List<ShelfEntity>,
        sections: List<ShelfSectionEntity>
    ): DashboardStats {
        val sessionId = activeSession?.id

        val sessionFirstCounts = if (sessionId != null) {
            firstCounts.filter { it.sessionId == sessionId }
        } else {
            emptyList()
        }

        val sessionSecondCounts = if (sessionId != null) {
            secondCounts.filter { it.sessionId == sessionId }
        } else {
            emptyList()
        }

        val countedSectionIds = (
            sessionFirstCounts.map { it.shelfSectionId } + sessionSecondCounts.map { it.shelfSectionId }
        ).toSet()
        val countedProductIds = (
            sessionFirstCounts.map { it.productId } + sessionSecondCounts.map { it.productId }
        ).toSet()

        val sessionShelves = if (activeSession != null) {
            shelves.filter { it.locationId == activeSession.locationId }
        } else {
            shelves
        }

        val sessionShelfIds = sessionShelves.map { it.id }.toSet()

        val sessionSections = sections.filter { it.shelfId in sessionShelfIds }
        val totalSections = sessionSections.size

        val completedSections = sessionSections.count { it.id in countedSectionIds }

        val completedShelfIds = sessionSections
            .filter { it.id in countedSectionIds }
            .map { it.shelfId }
            .toSet()

        val completedShelves = sessionShelves.count { it.id in completedShelfIds }

        val activeProducts = products.filter { it.isActive }
        val totalProducts = activeProducts.size
        val productsCounted = countedProductIds.size
        val productsRemaining = (totalProducts - productsCounted).coerceAtLeast(0)

        val productMap = activeProducts.associateBy { it.id }

        var varianceCount = 0
        var totalVariance = 0.0

        sessionFirstCounts.forEach { count ->
            val product = productMap[count.productId]
            if (product != null) {
                val variance = count.quantity - product.systemQuantity
                if (variance != 0.0) {
                    varianceCount++
                    totalVariance += variance
                }
            }
        }

        val countedSectionsPercentage = if (totalSections > 0) {
            (completedSections * 100 / totalSections)
        } else 0

        val countedProductsPercentage = if (totalProducts > 0) {
            (productsCounted * 100 / totalProducts)
        } else 0

        val shelfLines = sessionShelves.map { shelf ->
            val sectionNames = sessionSections
                .filter { it.shelfId == shelf.id }
                .joinToString(", ") { it.name }
            "${shelf.name}${if (sectionNames.isNotBlank()) ": $sectionNames" else ""}"
        }

        val location = if (activeSession != null) {
            shelves.firstOrNull { it.locationId == activeSession.locationId }?.name ?: "Location ${activeSession.locationId}"
        } else ""

        return DashboardStats(
            activeSession = activeSession,
            activeSessionLocationName = if (activeSession != null) location else "",
            activeSessionShelves = shelfLines,
            pendingSyncCount = pendingSync,
            completedShelves = completedShelves,
            completedSections = completedSections,
            productsCounted = productsCounted,
            productsRemaining = productsRemaining,
            totalProducts = totalProducts,
            varianceCount = varianceCount,
            totalVariance = totalVariance,
            totalShelves = sessionShelves.size,
            totalSections = totalSections,
            countedSectionsPercentage = countedSectionsPercentage,
            countedProductsPercentage = countedProductsPercentage
        )
    }
}
