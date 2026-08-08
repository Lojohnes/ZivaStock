
package com.zivastock.di

import android.content.Context
import com.zivastock.data.local.database.ZivaStockDatabase
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.android.qualifiers.ApplicationContext
import dagger.hilt.components.SingletonComponent
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
object DatabaseV2Module {

    @Provides
    @Singleton
    fun provideZivaStockDatabase(@ApplicationContext context: Context): ZivaStockDatabase {
        return ZivaStockDatabase.getDatabase(context)
    }


        @Provides
        @Singleton
        fun provideProductDao(database: ZivaStockDatabase): com.zivastock.data.local.database.v2.dao.ProductDao {
            return database.productDao()
        }


        @Provides
        @Singleton
        fun provideProductCategoryDao(database: ZivaStockDatabase): com.zivastock.data.local.database.v2.dao.ProductCategoryDao {
            return database.productCategoryDao()
        }


        @Provides
        @Singleton
        fun provideLocationDao(database: ZivaStockDatabase): com.zivastock.data.local.database.v2.dao.LocationDao {
            return database.locationDao()
        }


        @Provides
        @Singleton
        fun provideShelfDao(database: ZivaStockDatabase): com.zivastock.data.local.database.v2.dao.ShelfDao {
            return database.shelfDao()
        }


        @Provides
        @Singleton
        fun provideShelfSectionDao(database: ZivaStockDatabase): com.zivastock.data.local.database.v2.dao.ShelfSectionDao {
            return database.shelfSectionDao()
        }


        @Provides
        @Singleton
        fun provideStocktakeSessionDao(database: ZivaStockDatabase): com.zivastock.data.local.database.v2.dao.StocktakeSessionDao {
            return database.stocktakeSessionDao()
        }


        @Provides
        @Singleton
        fun provideSessionAssignmentDao(database: ZivaStockDatabase): com.zivastock.data.local.database.v2.dao.SessionAssignmentDao {
            return database.sessionAssignmentDao()
        }


        @Provides
        @Singleton
        fun provideFirstCountDao(database: ZivaStockDatabase): com.zivastock.data.local.database.v2.dao.FirstCountDao {
            return database.firstCountDao()
        }


        @Provides
        @Singleton
        fun provideSecondCountDao(database: ZivaStockDatabase): com.zivastock.data.local.database.v2.dao.SecondCountDao {
            return database.secondCountDao()
        }


        @Provides
        @Singleton
        fun provideUserDao(database: ZivaStockDatabase): com.zivastock.data.local.database.v2.dao.UserDao {
            return database.userDao()
        }


        @Provides
        @Singleton
        fun provideRoleDao(database: ZivaStockDatabase): com.zivastock.data.local.database.v2.dao.RoleDao {
            return database.roleDao()
        }


        @Provides
        @Singleton
        fun providePermissionDao(database: ZivaStockDatabase): com.zivastock.data.local.database.v2.dao.PermissionDao {
            return database.permissionDao()
        }


        @Provides
        @Singleton
        fun provideRolePermissionCrossRefDao(database: ZivaStockDatabase): com.zivastock.data.local.database.v2.dao.RolePermissionCrossRefDao {
            return database.rolePermissionCrossRefDao()
        }


        @Provides
        @Singleton
        fun provideUserRoleCrossRefDao(database: ZivaStockDatabase): com.zivastock.data.local.database.v2.dao.UserRoleCrossRefDao {
            return database.userRoleCrossRefDao()
        }


        @Provides
        @Singleton
        fun provideSyncQueueItemDao(database: ZivaStockDatabase): com.zivastock.data.local.database.v2.dao.SyncQueueItemDao {
            return database.syncQueueItemDao()
        }

        @Provides
        @Singleton
        fun provideSyncAuditLogDao(database: ZivaStockDatabase): com.zivastock.data.local.database.v2.dao.SyncAuditLogDao {
            return database.syncAuditLogDao()
        }
}
