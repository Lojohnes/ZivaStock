package com.zivastock.di

import android.content.Context
import com.zivastock.data.local.database.AppDatabase
import com.zivastock.data.local.database.dao.CountDao
import com.zivastock.data.local.database.dao.ProductDao
import com.zivastock.data.local.database.dao.SyncQueueDao
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.android.qualifiers.ApplicationContext
import dagger.hilt.components.SingletonComponent
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
object DatabaseModule {
    
    @Provides
    @Singleton
    fun provideAppDatabase(@ApplicationContext context: Context): AppDatabase {
        return AppDatabase.getDatabase(context)
    }
    
    @Provides
    @Singleton
    fun provideProductDao(database: AppDatabase): ProductDao {
        return database.productDao()
    }
    
    @Provides
    @Singleton
    fun provideCountDao(database: AppDatabase): CountDao {
        return database.countDao()
    }
    
    @Provides
    @Singleton
    fun provideSyncQueueDao(database: AppDatabase): SyncQueueDao {
        return database.syncQueueDao()
    }
}
