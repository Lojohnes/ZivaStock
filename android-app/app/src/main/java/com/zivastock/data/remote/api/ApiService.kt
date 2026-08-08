package com.zivastock.data.remote.api

import com.zivastock.data.remote.dto.LoginRequest
import com.zivastock.data.remote.dto.LoginResponse
import com.zivastock.data.remote.dto.ProductDto
import com.zivastock.data.remote.dto.SyncPushRequest
import com.zivastock.data.remote.dto.SyncPushResponse
import com.zivastock.data.remote.dto.SyncPullResponse
import com.zivastock.data.remote.dto.SyncStatusResponse
import com.zivastock.data.remote.dto.TokenRefreshRequest
import com.zivastock.data.remote.dto.TokenRefreshResponse
import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.Path
import retrofit2.http.POST
import retrofit2.http.Query

interface ApiService {
    
    @POST("/api/v1/auth/login")
    suspend fun login(@Body request: LoginRequest): Response<LoginResponse>
    
    @POST("/api/v1/auth/refresh")
    suspend fun refreshToken(@Body request: TokenRefreshRequest): Response<TokenRefreshResponse>
    
    @GET("/api/v1/products/barcode/{barcode}")
    suspend fun getProductByBarcode(
        @Query("token") token: String,
        @Path("barcode") barcode: String
    ): Response<ProductDto>
    
    @GET("/api/v1/products")
    suspend fun getProducts(
        @Query("token") token: String,
        @Query("page") page: Int = 1,
        @Query("limit") limit: Int = 50
    ): Response<List<ProductDto>>
    
    @POST("/api/v1/sync/push")
    suspend fun pushCounts(
        @Query("token") token: String,
        @Body request: SyncPushRequest
    ): Response<SyncPushResponse>
    
    @GET("/api/v1/sync/pull")
    suspend fun pullData(
        @Query("token") token: String,
        @Query("last_sync") lastSync: String? = null
    ): Response<SyncPullResponse>
    
    @GET("/api/v1/sync/status")
    suspend fun getSyncStatus(
        @Query("token") token: String
    ): Response<SyncStatusResponse>
}
