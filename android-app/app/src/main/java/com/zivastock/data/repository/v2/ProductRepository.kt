
package com.zivastock.data.repository.v2

import com.zivastock.data.local.database.ZivaStockDatabase
import com.zivastock.data.local.database.v2.entities.ProductEntity
import com.zivastock.data.remote.api.ZivaStockApi
import com.zivastock.data.remote.dto.v2.ProductDto
import kotlinx.coroutines.flow.Flow
import javax.inject.Inject

class ProductRepository @Inject constructor(
    private val database: ZivaStockDatabase,
    private val api: ZivaStockApi
) {
    private val dao = database.productDao()

    fun getAll(): Flow<List<ProductEntity>> = dao.getAll()

    fun search(query: String): Flow<List<ProductEntity>> =
        if (query.isBlank()) dao.getAll() else dao.search(query.trim())

    fun searchByDescription(description: String): Flow<List<ProductEntity>> =
        dao.searchByDescription(description.trim())

    suspend fun getById(id: Long): ProductEntity? = dao.getById(id)

    suspend fun getByBarcode(barcode: String): ProductEntity? = dao.getByBarcode(barcode)

    suspend fun getByProductCode(productCode: String): ProductEntity? = dao.getByProductCode(productCode)

    suspend fun save(entity: ProductEntity) {
        dao.insert(entity)
    }

    suspend fun saveAll(entities: List<ProductEntity>) {
        dao.insertAll(entities)
    }

    suspend fun delete(entity: ProductEntity) {
        dao.delete(entity)
    }

    suspend fun fetchFromServer(): Result<Int> {
        return try {
            val response = api.getProducts()
            if (response.isSuccessful && response.body() != null) {
                val entities = response.body()!!.map { it.toEntity() }
                dao.insertAll(entities)
                Result.success(entities.size)
            } else {
                Result.failure(Exception("Failed to fetch products: ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    private fun ProductDto.toEntity(): ProductEntity {
        return ProductEntity(
            id = id ?: 0,
            sku = sku,
            barcode = barcode.orEmpty(),
            productCode = productCode,
            categoryId = categoryId,
            description = description.orEmpty(),
            unitOfMeasure = unitOfMeasure ?: "EA",
            systemQuantity = systemQuantity ?: 0.0,
            unitCost = unitCost ?: 0.0,
            unitPrice = unitPrice ?: 0.0,
            reorderLevel = reorderLevel ?: 0.0,
            isActive = isActive ?: true,
            createdAt = createdAt,
            updatedAt = updatedAt
        )
    }
}
