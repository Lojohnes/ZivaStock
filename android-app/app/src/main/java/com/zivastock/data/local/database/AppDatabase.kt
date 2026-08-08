package com.zivastock.data.local.database

import android.content.Context
import androidx.room.Database
import androidx.room.Room
import androidx.room.RoomDatabase
import com.zivastock.data.local.database.dao.CountDao
import com.zivastock.data.local.database.dao.ProductDao
import com.zivastock.data.local.database.dao.SyncQueueDao
import com.zivastock.data.local.database.entities.CountEntity
import com.zivastock.data.local.database.entities.ProductEntity
import com.zivastock.data.local.database.entities.SyncQueueEntity

@Database(
    entities = [
        ProductEntity::class,
        CountEntity::class,
        SyncQueueEntity::class
    ],
    version = 1,
    exportSchema = false
)
abstract class AppDatabase : RoomDatabase() {
    
    abstract fun productDao(): ProductDao
    abstract fun countDao(): CountDao
    abstract fun syncQueueDao(): SyncQueueDao
    
    companion object {
        @Volatile
        private var INSTANCE: AppDatabase? = null
        
        fun getDatabase(context: Context): AppDatabase {
            return INSTANCE ?: synchronized(this) {
                val instance = Room.databaseBuilder(
                    context.applicationContext,
                    AppDatabase::class.java,
                    "zivastock_database"
                )
                    .fallbackToDestructiveMigration()
                    .build()
                INSTANCE = instance
                instance
            }
        }
    }
}
