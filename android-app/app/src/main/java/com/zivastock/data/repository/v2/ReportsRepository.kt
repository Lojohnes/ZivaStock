package com.zivastock.data.repository.v2

import com.zivastock.data.local.database.ZivaStockDatabase
import com.zivastock.data.local.database.v2.entities.FirstCountEntity
import com.zivastock.data.local.database.v2.entities.LocationEntity
import com.zivastock.data.local.database.v2.entities.ProductEntity
import com.zivastock.data.local.database.v2.entities.SecondCountEntity
import com.zivastock.data.local.database.v2.entities.ShelfEntity
import com.zivastock.data.local.database.v2.entities.ShelfSectionEntity
import com.zivastock.data.local.database.v2.entities.StocktakeSessionEntity
import com.zivastock.data.local.database.v2.entities.UserEntity
import com.zivastock.data.session.SessionManager
import com.zivastock.ui.reports.AuditTrailItem
import com.zivastock.ui.reports.ComparisonReportItem
import com.zivastock.ui.reports.ConsolidationReportItem
import com.zivastock.ui.reports.CountsReportItem
import com.zivastock.ui.reports.DuplicateCountItem
import com.zivastock.ui.reports.MissingProductItem
import com.zivastock.ui.reports.SessionProgressItem
import com.zivastock.ui.reports.UserProductivityItem
import com.zivastock.ui.reports.VarianceReportItem
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.combine
import kotlinx.coroutines.flow.map
import kotlin.jvm.JvmName
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class ReportsRepository @Inject constructor(
    private val database: ZivaStockDatabase,
    private val sessionManager: SessionManager
) {

    private val firstCountDao = database.firstCountDao()
    private val secondCountDao = database.secondCountDao()
    private val productDao = database.productDao()
    private val shelfDao = database.shelfDao()
    private val shelfSectionDao = database.shelfSectionDao()
    private val locationDao = database.locationDao()
    private val userDao = database.userDao()
    private val sessionDao = database.stocktakeSessionDao()
    private val auditLogDao = database.syncAuditLogDao()

    fun getSessions(): Flow<List<StocktakeSessionEntity>> = sessionDao.getAll()

    fun activeSession(): Flow<StocktakeSessionEntity?> = sessionManager.activeSession

    private fun baseDataFlow(): Flow<BaseData> = combine(
        sessionManager.activeSession,
        firstCountDao.getAll(),
        secondCountDao.getAll(),
        productDao.getAll(),
        shelfDao.getAll(),
        shelfSectionDao.getAll(),
        locationDao.getAll(),
        userDao.getAll(),
        sessionDao.getAll()
    ) { values ->
        BaseData(
            activeSession = values[0] as StocktakeSessionEntity?,
            firstCounts = values[1] as List<FirstCountEntity>,
            secondCounts = values[2] as List<SecondCountEntity>,
            products = values[3] as List<ProductEntity>,
            shelves = values[4] as List<ShelfEntity>,
            sections = values[5] as List<ShelfSectionEntity>,
            locations = values[6] as List<LocationEntity>,
            users = values[7] as List<UserEntity>,
            sessions = values[8] as List<StocktakeSessionEntity>
        )
    }

    fun getVarianceReport(sessionId: Long? = null): Flow<List<VarianceReportItem>> =
        baseDataFlow().mapData { data ->
            val targetSessionId = sessionId ?: data.activeSession?.id
            val sessionFirst = data.firstCounts.filterBySession(targetSessionId)
            val sessionSecond = data.secondCounts.filterBySession(targetSessionId)
            val productMap = data.products.associateBy { it.id }
            val countedQty = mutableMapOf<Long, Double>()
            val allCounts = sessionFirst.map { it.toCountData() } + sessionSecond.map { it.toCountData() }
            allCounts.forEach { count ->
                countedQty[count.productId] = countedQty.getOrDefault(count.productId, 0.0) + count.quantity
            }
            data.products.filter { it.isActive }.map { product ->
                val qty = countedQty[product.id] ?: 0.0
                VarianceReportItem(
                    barcode = product.barcode,
                    productName = product.description,
                    systemQty = product.systemQuantity,
                    countedQty = qty,
                    variance = qty - product.systemQuantity
                )
            }
        }

    fun getConsolidationReport(sessionId: Long? = null): Flow<List<ConsolidationReportItem>> =
        baseDataFlow().mapData { data ->
            val targetSessionId = sessionId ?: data.activeSession?.id
            val allCounts = data.firstCounts.filterBySession(targetSessionId).map { it.toCountData() } +
                data.secondCounts.filterBySession(targetSessionId).map { it.toCountData() }
            val productMap = data.products.associateBy { it.id }
            val totals = allCounts.groupBy { it.productId }
                .mapValues { entry -> entry.value.sumOf { it.quantity } }
            totals.map { (productId, total) ->
                val product = productMap[productId]
                ConsolidationReportItem(
                    barcode = product?.barcode ?: productId.toString(),
                    productName = product?.description ?: "Unknown",
                    totalCountedQty = total
                )
            }.sortedBy { it.productName }
        }

    fun getComparisonReport(sessionId: Long? = null): Flow<List<ComparisonReportItem>> =
        baseDataFlow().mapData { data ->
            val targetSessionId = sessionId ?: data.activeSession?.id
            val first = data.firstCounts.filterBySession(targetSessionId)
            val second = data.secondCounts.filterBySession(targetSessionId)
            buildComparisonRows(first, second, data)
        }

    fun getCountsReport(sessionId: Long? = null, isSecond: Boolean = false): Flow<List<CountsReportItem>> =
        baseDataFlow().mapData { data ->
            val targetSessionId = sessionId ?: data.activeSession?.id
            val counts = if (isSecond) {
                data.secondCounts.filterBySession(targetSessionId).map { it.toCountData() }
            } else {
                data.firstCounts.filterBySession(targetSessionId).map { it.toCountData() }
            }
            buildCountsRows(counts, data)
        }

    fun getMissingProducts(sessionId: Long? = null): Flow<List<MissingProductItem>> =
        baseDataFlow().mapData { data ->
            val targetSessionId = sessionId ?: data.activeSession?.id
            val countedProductIds = (
                data.firstCounts.filterBySession(targetSessionId).map { it.productId } +
                    data.secondCounts.filterBySession(targetSessionId).map { it.productId }
            ).toSet()
            data.products.filter { it.isActive && it.id !in countedProductIds }.map {
                MissingProductItem(
                    barcode = it.barcode,
                    productName = it.description,
                    systemQty = it.systemQuantity
                )
            }.sortedBy { it.productName }
        }

    fun getDuplicateCounts(sessionId: Long? = null): Flow<List<DuplicateCountItem>> =
        baseDataFlow().mapData { data ->
            val targetSessionId = sessionId ?: data.activeSession?.id
            val first = data.firstCounts.filterBySession(targetSessionId)
            val second = data.secondCounts.filterBySession(targetSessionId)
            buildDuplicateRows(
                first.map { it.toCountData() } + second.map { it.toCountData() },
                data
            )
        }

    fun getAuditTrail(): Flow<List<AuditTrailItem>> =
        auditLogDao.getAll().mapData { logs ->
            logs.map {
                AuditTrailItem(
                    timestamp = it.timestamp,
                    operation = it.operation,
                    entityType = it.entityType,
                    entityId = it.entityId?.toString(),
                    status = it.status,
                    message = it.message
                )
            }
        }

    fun getSessionProgress(sessionId: Long? = null): Flow<List<SessionProgressItem>> =
        baseDataFlow().mapData { data ->
            val targetSessionId = sessionId ?: data.activeSession?.id
            val targetSession = data.sessions.firstOrNull { it.id == targetSessionId }
                ?: data.activeSession
            val sessionShelves = if (targetSession != null) {
                data.shelves.filter { it.locationId == targetSession.locationId }
            } else data.shelves
            val shelfIds = sessionShelves.map { it.id }.toSet()
            val sessionSections = data.sections.filter { it.shelfId in shelfIds }
            val allCounts = data.firstCounts.filterBySession(targetSessionId).map { CountData.from(it) } +
                data.secondCounts.filterBySession(targetSessionId).map { CountData.from(it) }
            val countedSectionIds = allCounts.map { it.shelfSectionId }.toSet()
            val userMap = data.users.associateBy { it.id }
            val countMap = allCounts.groupBy { it.shelfSectionId }
            sessionSections.flatMap { section ->
                val shelf = sessionShelves.firstOrNull { it.id == section.shelfId }
                val counts = countMap[section.id].orEmpty()
                if (counts.isEmpty()) {
                    listOf(
                        SessionProgressItem(
                            shelfName = shelf?.name ?: "",
                            sectionName = section.name,
                            completed = false,
                            countedBy = null,
                            countedAt = null
                        )
                    )
                } else {
                    counts.map { count ->
                        val user = userMap[count.userId]
                        SessionProgressItem(
                            shelfName = shelf?.name ?: "",
                            sectionName = section.name,
                            completed = true,
                            countedBy = user?.let { "${it.firstName} ${it.lastName}" }?.trim() ?: count.userId.toString(),
                            countedAt = count.countedAt
                        )
                    }
                }
            }
        }

    fun getUserProductivity(sessionId: Long? = null): Flow<List<UserProductivityItem>> =
        baseDataFlow().mapData { data ->
            val targetSessionId = sessionId ?: data.activeSession?.id
            val first = data.firstCounts.filterBySession(targetSessionId)
            val second = data.secondCounts.filterBySession(targetSessionId)
            val userMap = data.users.associateBy { it.id }
            val firstByUser = first.groupBy { it.userId }.mapValues { entry -> entry.value.sumOf { it.quantity } }
            val secondByUser = second.groupBy { it.userId }.mapValues { entry -> entry.value.sumOf { it.quantity } }
            val userIds = (firstByUser.keys + secondByUser.keys).toSet()
            userIds.map { userId ->
                val user = userMap[userId]
                val firstQty = firstByUser[userId] ?: 0.0
                val secondQty = secondByUser[userId] ?: 0.0
                UserProductivityItem(
                    userName = user?.let { "${it.firstName} ${it.lastName}" }?.trim() ?: userId.toString(),
                    firstCountQty = firstQty,
                    secondCountQty = secondQty,
                    totalCounted = firstQty + secondQty
                )
            }.sortedBy { it.userName }
        }

    private inline fun <T, R> Flow<T>.mapData(crossinline transform: (T) -> R): Flow<R> =
        map { transform(it) }

    @JvmName("filterFirstCountsBySession")
    private fun List<FirstCountEntity>.filterBySession(sessionId: Long?): List<FirstCountEntity> =
        if (sessionId != null) filter { it.sessionId == sessionId } else this

    @JvmName("filterSecondCountsBySession")
    private fun List<SecondCountEntity>.filterBySession(sessionId: Long?): List<SecondCountEntity> =
        if (sessionId != null) filter { it.sessionId == sessionId } else this

    @JvmName("firstCountToCountData")
    private fun FirstCountEntity.toCountData(): CountData = CountData.from(this)

    @JvmName("secondCountToCountData")
    private fun SecondCountEntity.toCountData(): CountData = CountData.from(this)

    private fun BaseData.resolveNames(count: CountData): NameData {
        val product = products.associateBy { it.id }[count.productId]
        val section = sections.associateBy { it.id }[count.shelfSectionId]
        val shelf = shelves.associateBy { it.id }[section?.shelfId]
        val location = locations.associateBy { it.id }[shelf?.locationId]
        val user = users.associateBy { it.id }[count.userId]
        return NameData(
            barcode = product?.barcode ?: count.productId.toString(),
            productName = product?.description ?: "Unknown",
            sectionName = section?.name ?: "",
            shelfName = shelf?.name ?: "",
            locationName = location?.name ?: location?.id?.toString() ?: "",
            countedBy = user?.let { "${it.firstName} ${it.lastName}" }?.trim() ?: count.userId.toString()
        )
    }

    private fun buildCountsRows(counts: List<CountData>, data: BaseData): List<CountsReportItem> {
        return counts.map { count ->
            val names = data.resolveNames(count)
            CountsReportItem(
                fileNumber = count.fileNumber ?: "",
                locationName = names.locationName,
                shelfName = names.shelfName,
                sectionName = names.sectionName,
                barcode = names.barcode,
                productName = names.productName,
                quantity = count.quantity,
                countedBy = names.countedBy,
                countedAt = count.countedAt
            )
        }.sortedWith(
            compareBy(
                { it.fileNumber },
                { it.locationName },
                { it.shelfName },
                { it.sectionName },
                { it.productName }
            )
        )
    }

    private fun buildComparisonRows(first: List<FirstCountEntity>, second: List<SecondCountEntity>, data: BaseData): List<ComparisonReportItem> {
        val firstGroups = first.groupBy { Triple(it.fileNumber, it.shelfSectionId, it.productId) }
            .mapValues { entry -> entry.value.sumOf { it.quantity } }
        val secondGroups = second.groupBy { Triple(it.fileNumber, it.shelfSectionId, it.productId) }
            .mapValues { entry -> entry.value.sumOf { it.quantity } }
        val keys = (firstGroups.keys + secondGroups.keys).toSet()
        return keys.map { key ->
            val (fileNumber, sectionId, productId) = key
            val firstQty = firstGroups[key] ?: 0.0
            val secondQty = secondGroups[key] ?: 0.0
            val names = data.resolveNames(
                CountData(
                    productId = productId,
                    shelfSectionId = sectionId ?: 0L,
                    userId = 0L,
                    fileNumber = fileNumber,
                    quantity = 0.0,
                    countedAt = ""
                )
            )
            ComparisonReportItem(
                fileNumber = fileNumber ?: "",
                locationName = names.locationName,
                shelfName = names.shelfName,
                sectionName = names.sectionName,
                barcode = names.barcode,
                productName = names.productName,
                firstCountQty = firstQty,
                secondCountQty = secondQty,
                difference = firstQty - secondQty
            )
        }.sortedWith(
            compareBy(
                { it.fileNumber },
                { it.locationName },
                { it.shelfName },
                { it.sectionName },
                { it.productName }
            )
        )
    }

    private fun buildDuplicateRows(counts: List<CountData>, data: BaseData): List<DuplicateCountItem> {
        return counts.groupBy { Triple(it.fileNumber, it.shelfSectionId, it.productId) }
            .filter { it.value.size > 1 }
            .map { (key, group) ->
                val (fileNumber, sectionId, productId) = key
                val names = data.resolveNames(
                    CountData(
                        productId = productId,
                        shelfSectionId = sectionId ?: 0L,
                        userId = 0L,
                        fileNumber = fileNumber,
                        quantity = 0.0,
                        countedAt = ""
                    )
                )
                DuplicateCountItem(
                    fileNumber = fileNumber ?: "",
                    barcode = names.barcode,
                    productName = names.productName,
                    occurrences = group.size,
                    totalQty = group.sumOf { it.quantity }
                )
            }.sortedWith(
                compareBy(
                    { it.fileNumber },
                    { it.productName }
                )
            )
    }

    private data class CountData(
        val productId: Long,
        val shelfSectionId: Long,
        val userId: Long,
        val fileNumber: String?,
        val quantity: Double,
        val countedAt: String
    ) {
        companion object {
            @JvmName("fromFirstCountEntity")
            fun from(entity: FirstCountEntity): CountData = CountData(
                productId = entity.productId,
                shelfSectionId = entity.shelfSectionId,
                userId = entity.userId,
                fileNumber = entity.fileNumber,
                quantity = entity.quantity,
                countedAt = entity.countedAt
            )

            @JvmName("fromSecondCountEntity")
            fun from(entity: SecondCountEntity): CountData = CountData(
                productId = entity.productId,
                shelfSectionId = entity.shelfSectionId,
                userId = entity.userId,
                fileNumber = entity.fileNumber,
                quantity = entity.quantity,
                countedAt = entity.countedAt
            )
        }
    }

    private data class BaseData(
        val activeSession: StocktakeSessionEntity?,
        val firstCounts: List<FirstCountEntity>,
        val secondCounts: List<SecondCountEntity>,
        val products: List<ProductEntity>,
        val shelves: List<ShelfEntity>,
        val sections: List<ShelfSectionEntity>,
        val locations: List<LocationEntity>,
        val users: List<UserEntity>,
        val sessions: List<StocktakeSessionEntity>
    )

    private data class NameData(
        val barcode: String,
        val productName: String,
        val sectionName: String,
        val shelfName: String,
        val locationName: String,
        val countedBy: String
    )
}
