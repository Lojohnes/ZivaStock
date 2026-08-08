
package com.zivastock.data.remote.api

import com.zivastock.data.remote.dto.v2.*
import retrofit2.Response
import retrofit2.http.*

interface ZivaStockApi {

    @POST("auth/login")
    suspend fun login(@Body request: LoginRequestDto): Response<LoginResponseDto>

    @POST("auth/refresh")
    suspend fun refreshToken(@Body request: RefreshRequestDto): Response<LoginResponseDto>

    @GET("products")
    suspend fun getProducts(): Response<List<ProductDto>>

    @GET("products/barcode/{barcode}")
    suspend fun getProductByBarcode(@Path("barcode") barcode: String): Response<ProductDto>

    @GET("products/{id}")
    suspend fun getProductById(@Path("id") id: Long): Response<ProductDto>

    @GET("locations")
    suspend fun getLocations(): Response<List<LocationDto>>

    @GET("locations/{id}")
    suspend fun getLocation(@Path("id") id: Long): Response<LocationDto>

    @GET("locations/{id}/tree")
    suspend fun getLocationTree(@Path("id") id: Long): Response<LocationDto>

    @POST("locations")
    suspend fun createLocation(@Body location: LocationDto): Response<LocationDto>

    @GET("locations/shelves")
    suspend fun getShelves(): Response<List<ShelfDto>>

    @GET("locations/sections")
    suspend fun getShelfSections(): Response<List<ShelfSectionDto>>

    @GET("sessions")
    suspend fun getSessions(): Response<List<StocktakeSessionDto>>

    @POST("sessions")
    suspend fun createSession(@Body session: StocktakeSessionDto): Response<StocktakeSessionDto>

    @GET("sessions/{id}")
    suspend fun getSession(@Path("id") id: Long): Response<StocktakeSessionDto>

    @GET("counts/first")
    suspend fun getFirstCounts(@Query("session_id") sessionId: Long?): Response<List<FirstCountDto>>

    @POST("counts/first")
    suspend fun createFirstCount(@Body count: FirstCountDto): Response<FirstCountDto>

    @POST("counts/first/bulk")
    suspend fun createFirstCounts(@Body counts: List<FirstCountDto>): Response<List<FirstCountDto>>

    @GET("counts/second")
    suspend fun getSecondCounts(@Query("session_id") sessionId: Long?): Response<List<SecondCountDto>>

    @POST("counts/second")
    suspend fun createSecondCount(@Body count: SecondCountDto): Response<SecondCountDto>

    @POST("counts/second/bulk")
    suspend fun createSecondCounts(@Body counts: List<SecondCountDto>): Response<List<SecondCountDto>>

    @POST("sync/push")
    suspend fun pushSync(@Body request: SyncPushRequestDto): Response<SyncPullResponseDto>

    @POST("sync/pull")
    suspend fun pullSync(@Query("last_sync") lastSync: String?): Response<SyncPullResponseDto>

    @GET("sync/status")
    suspend fun getSyncStatus(): Response<SyncPullResponseDto>

    @GET("users/me")
    suspend fun getCurrentUser(): Response<UserDto>

    @GET("users/{id}/permissions")
    suspend fun getUserPermissions(@Path("id") id: Long): Response<List<PermissionDto>>

    @GET("roles")
    suspend fun getRoles(): Response<List<RoleDto>>
}
