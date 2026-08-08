package com.zivastock.di

import com.zivastock.data.remote.api.ApiService
import com.zivastock.data.repository.CountRepository
import com.zivastock.data.repository.ProductRepository
import com.zivastock.data.repository.SyncRepository
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.components.SingletonComponent
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
object RepositoryModule {

    @Provides
    @Singleton
    fun provideProductRepository(
        productDao: com.zivastock.data.local.database.dao.ProductDao,
        apiService: ApiService
    ): ProductRepository {
        return ProductRepository(productDao, apiService)
    }
    
    @Provides
    @Singleton
    fun provideCountRepository(
        countDao: com.zivastock.data.local.database.dao.CountDao
    ): CountRepository {
        return CountRepository(countDao)
    }
    
    @Provides
    @Singleton
    fun provideSyncRepository(
        syncQueueDao: com.zivastock.data.local.database.dao.SyncQueueDao,
        apiService: ApiService
    ): SyncRepository {
        return SyncRepository(syncQueueDao, apiService)
    }
}
