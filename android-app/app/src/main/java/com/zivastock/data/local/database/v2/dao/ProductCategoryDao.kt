
package com.zivastock.data.local.database.v2.dao

import androidx.room.*
import com.zivastock.data.local.database.v2.entities.ProductCategoryEntity
import kotlinx.coroutines.flow.Flow

@Dao
interface ProductCategoryDao {
    @Query("SELECT * FROM v2_product_categories")
    fun getAll(): Flow<List<ProductCategoryEntity>>


    @Query("SELECT * FROM v2_product_categories WHERE id = :id")
    suspend fun getById(id: Long): ProductCategoryEntity?


    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(item: ProductCategoryEntity): Long

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertAll(items: List<ProductCategoryEntity>): List<Long>

    @Update
    suspend fun update(item: ProductCategoryEntity)

    @Delete
    suspend fun delete(item: ProductCategoryEntity)

    @Query("DELETE FROM v2_product_categories")
    suspend fun deleteAll()
}
