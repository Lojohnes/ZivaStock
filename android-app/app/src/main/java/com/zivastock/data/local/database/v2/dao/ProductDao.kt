
package com.zivastock.data.local.database.v2.dao

import androidx.room.*
import com.zivastock.data.local.database.v2.entities.ProductEntity
import kotlinx.coroutines.flow.Flow

@Dao
interface ProductDao {
    @Query("SELECT * FROM v2_products")
    fun getAll(): Flow<List<ProductEntity>>

    @Query("""
        SELECT * FROM v2_products
        WHERE barcode LIKE '%' || :query || '%'
           OR productCode LIKE '%' || :query || '%'
           OR sku LIKE '%' || :query || '%'
           OR LOWER(description) LIKE '%' || LOWER(:query) || '%'
    """)
    fun search(query: String): Flow<List<ProductEntity>>

    @Query("SELECT * FROM v2_products WHERE id = :id")
    suspend fun getById(id: Long): ProductEntity?

    @Query("SELECT * FROM v2_products WHERE barcode = :barcode LIMIT 1")
    suspend fun getByBarcode(barcode: String): ProductEntity?

    @Query("SELECT * FROM v2_products WHERE productCode = :productCode LIMIT 1")
    suspend fun getByProductCode(productCode: String): ProductEntity?

    @Query("""
        SELECT * FROM v2_products
        WHERE LOWER(description) LIKE '%' || LOWER(:description) || '%'
    """)
    fun searchByDescription(description: String): Flow<List<ProductEntity>>


    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(item: ProductEntity): Long

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertAll(items: List<ProductEntity>): List<Long>

    @Update
    suspend fun update(item: ProductEntity)

    @Delete
    suspend fun delete(item: ProductEntity)

    @Query("DELETE FROM v2_products")
    suspend fun deleteAll()
}
