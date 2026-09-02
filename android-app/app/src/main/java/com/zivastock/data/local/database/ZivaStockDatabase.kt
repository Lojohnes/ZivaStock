
    package com.zivastock.data.local.database

    import android.content.Context
    import androidx.room.Database
    import androidx.room.Room
    import androidx.room.RoomDatabase
    import com.zivastock.data.local.database.v2.entities.ProductEntity
import com.zivastock.data.local.database.v2.entities.ProductCategoryEntity
import com.zivastock.data.local.database.v2.entities.LocationEntity
import com.zivastock.data.local.database.v2.entities.ShelfEntity
import com.zivastock.data.local.database.v2.entities.ShelfSectionEntity
import com.zivastock.data.local.database.v2.entities.StocktakeSessionEntity
import com.zivastock.data.local.database.v2.entities.SessionAssignmentEntity
import com.zivastock.data.local.database.v2.entities.FirstCountEntity
import com.zivastock.data.local.database.v2.entities.SecondCountEntity
import com.zivastock.data.local.database.v2.entities.UserEntity
import com.zivastock.data.local.database.v2.entities.RoleEntity
import com.zivastock.data.local.database.v2.entities.PermissionEntity
import com.zivastock.data.local.database.v2.entities.RolePermissionCrossRefEntity
import com.zivastock.data.local.database.v2.entities.UserRoleCrossRefEntity
import com.zivastock.data.local.database.v2.entities.SyncQueueItemEntity
import com.zivastock.data.local.database.v2.entities.SyncAuditLogEntity
    import com.zivastock.data.local.database.v2.dao.ProductDao
import com.zivastock.data.local.database.v2.dao.ProductCategoryDao
import com.zivastock.data.local.database.v2.dao.LocationDao
import com.zivastock.data.local.database.v2.dao.ShelfDao
import com.zivastock.data.local.database.v2.dao.ShelfSectionDao
import com.zivastock.data.local.database.v2.dao.StocktakeSessionDao
import com.zivastock.data.local.database.v2.dao.SessionAssignmentDao
import com.zivastock.data.local.database.v2.dao.FirstCountDao
import com.zivastock.data.local.database.v2.dao.SecondCountDao
import com.zivastock.data.local.database.v2.dao.UserDao
import com.zivastock.data.local.database.v2.dao.RoleDao
import com.zivastock.data.local.database.v2.dao.PermissionDao
import com.zivastock.data.local.database.v2.dao.RolePermissionCrossRefDao
import com.zivastock.data.local.database.v2.dao.UserRoleCrossRefDao
import com.zivastock.data.local.database.v2.dao.SyncQueueItemDao
import com.zivastock.data.local.database.v2.dao.SyncAuditLogDao

    @Database(
        entities = [
            ProductEntity::class, ProductCategoryEntity::class, LocationEntity::class, ShelfEntity::class, ShelfSectionEntity::class, StocktakeSessionEntity::class, SessionAssignmentEntity::class, FirstCountEntity::class, SecondCountEntity::class, UserEntity::class, RoleEntity::class, PermissionEntity::class, RolePermissionCrossRefEntity::class, UserRoleCrossRefEntity::class, SyncQueueItemEntity::class, SyncAuditLogEntity::class
        ],
        version = 2,
        exportSchema = false
    )
    abstract class ZivaStockDatabase : RoomDatabase() {
            abstract fun productDao(): ProductDao
    abstract fun productCategoryDao(): ProductCategoryDao
    abstract fun locationDao(): LocationDao
    abstract fun shelfDao(): ShelfDao
    abstract fun shelfSectionDao(): ShelfSectionDao
    abstract fun stocktakeSessionDao(): StocktakeSessionDao
    abstract fun sessionAssignmentDao(): SessionAssignmentDao
    abstract fun firstCountDao(): FirstCountDao
    abstract fun secondCountDao(): SecondCountDao
    abstract fun userDao(): UserDao
    abstract fun roleDao(): RoleDao
    abstract fun permissionDao(): PermissionDao
    abstract fun rolePermissionCrossRefDao(): RolePermissionCrossRefDao
    abstract fun userRoleCrossRefDao(): UserRoleCrossRefDao
    abstract fun syncQueueItemDao(): SyncQueueItemDao
    abstract fun syncAuditLogDao(): SyncAuditLogDao

        companion object {
            @Volatile
            private var INSTANCE: ZivaStockDatabase? = null

            fun getDatabase(context: Context): ZivaStockDatabase {
                return INSTANCE ?: synchronized(this) {
                    val instance = Room.databaseBuilder(
                        context.applicationContext,
                        ZivaStockDatabase::class.java,
                        "ziva_stock_v2.db"
                    )
                    .fallbackToDestructiveMigration()
                    .build()
                    INSTANCE = instance
                    instance
                }
            }
        }
    }
