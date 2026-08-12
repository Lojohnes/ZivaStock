package com.zivastock.data.repository

import com.zivastock.data.local.database.dao.ProductDao
import com.zivastock.data.local.database.entities.ProductEntity
import com.zivastock.data.remote.api.ApiService
import com.zivastock.data.remote.dto.ProductDto
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class ProductRepository @Inject constructor(
    private val productDao: ProductDao,
    private val apiService: ApiService
) {
    
    suspend fun getProductByBarcode(barcode: String): ProductEntity? {
        return productDao.getProductByBarcode(barcode)
    }
    
    suspend fun getProductById(id: Int): ProductEntity? {
        return productDao.getProductById(id)
    }
    
    suspend fun getAllProducts(): List<ProductEntity> {
        return productDao.getAllProducts()
    }
    
    suspend fun insertProduct(product: ProductEntity) {
        productDao.insertProduct(product)
    }
    
    suspend fun insertProducts(products: List<ProductEntity>) {
        productDao.insertProducts(products)
    }
    
    suspend fun fetchProductFromServer(token: String, barcode: String): ProductDto? {
        val response = apiService.getProductByBarcode(token, barcode)
        return if (response.isSuccessful) {
            response.body()
        } else {
            null
        }
    }
    
    suspend fun fetchProductsFromServer(token: String): List<ProductDto>? {
        val response = apiService.getProducts(token)
        return if (response.isSuccessful) {
            response.body()?.items
        } else {
            null
        }
    }
    
    suspend fun deleteAllProducts() {
        productDao.deleteAllProducts()
    }
}
