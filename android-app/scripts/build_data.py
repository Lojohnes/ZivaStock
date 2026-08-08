#!/usr/bin/env python3
"""Generate ZivaStock Android v2 data layer (Room, DTOs, API, repositories, DI)."""

import os
from pathlib import Path
from textwrap import dedent

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "app" / "src" / "main" / "java" / "com" / "zivastock"

PACKAGE = {
    "entity":    SRC / "data" / "local" / "database" / "v2" / "entities",
    "dao":       SRC / "data" / "local" / "database" / "v2" / "dao",
    "database":  SRC / "data" / "local" / "database",
    "dto":       SRC / "data" / "remote" / "dto" / "v2",
    "api":       SRC / "data" / "remote" / "api",
    "repo":      SRC / "data" / "repository" / "v2",
    "di":        SRC / "di",
}

for p in PACKAGE.values():
    p.mkdir(parents=True, exist_ok=True)

# ----------------------------------------------------------------------------
# Room v2 entities
# ----------------------------------------------------------------------------
ENTITIES = [
    ("Product", "v2_products", """
    val sku: String? = null,
    val barcode: String = "",
    val productCode: String? = null,
    val categoryId: Long? = null,
    val description: String = "",
    val unitOfMeasure: String = "EA",
    val systemQuantity: Double = 0.0,
    val unitCost: Double = 0.0,
    val unitPrice: Double = 0.0,
    val reorderLevel: Double = 0.0,
    val isActive: Boolean = true,
    val createdAt: String? = null,
    val updatedAt: String? = null,
    """),
    ("ProductCategory", "v2_product_categories", """
    val name: String = "",
    val parentId: Long? = null,
    val description: String? = null,
    val isActive: Boolean = true,
    val createdAt: String? = null,
    val updatedAt: String? = null,
    """),
    ("Location", "v2_locations", """
    val name: String = "",
    val type: String = "",
    val parentId: Long? = null,
    val address: String? = null,
    val isActive: Boolean = true,
    val createdAt: String? = null,
    val updatedAt: String? = null,
    """),
    ("Shelf", "v2_shelves", """
    val locationId: Long = 0,
    val name: String = "",
    val description: String? = null,
    val isActive: Boolean = true,
    val createdAt: String? = null,
    val updatedAt: String? = null,
    """),
    ("ShelfSection", "v2_shelf_sections", """
    val shelfId: Long = 0,
    val name: String = "",
    val description: String? = null,
    val isActive: Boolean = true,
    val createdAt: String? = null,
    val updatedAt: String? = null,
    """),
    ("StocktakeSession", "v2_stocktake_sessions", """
    val uuid: String = "",
    val name: String = "",
    val description: String? = null,
    val locationId: Long = 0,
    val sessionType: String = "full",
    val status: String = "not_started",
    val startTime: String? = null,
    val endTime: String? = null,
    val createdBy: Long = 0,
    val approvedBy: Long? = null,
    val approvedAt: String? = null,
    val createdAt: String? = null,
    val updatedAt: String? = null,
    """),
    ("SessionAssignment", "v2_session_assignments", """
    val sessionId: Long = 0,
    val userId: Long = 0,
    val shelfSectionId: Long? = null,
    val assignmentRole: String = "first_counter",
    val status: String = "assigned",
    val assignedBy: Long? = null,
    val assignedAt: String? = null,
    val startedAt: String? = null,
    val completedAt: String? = null,
    """),
    ("FirstCount", "v2_first_counts", """
    val sessionId: Long = 0,
    val productId: Long = 0,
    val shelfSectionId: Long = 0,
    val userId: Long = 0,
    val quantity: Double = 0.0,
    val clientId: String? = null,
    val deviceId: String? = null,
    val source: String = "mobile",
    val countedAt: String = "",
    val isSynced: Boolean = false,
    val syncedAt: String? = null,
    """),
    ("SecondCount", "v2_second_counts", """
    val sessionId: Long = 0,
    val productId: Long = 0,
    val shelfSectionId: Long = 0,
    val userId: Long = 0,
    val firstCountId: Long? = null,
    val quantity: Double = 0.0,
    val clientId: String? = null,
    val deviceId: String? = null,
    val source: String = "mobile",
    val countedAt: String = "",
    val isSynced: Boolean = false,
    val syncedAt: String? = null,
    """),
    ("User", "v2_users", """
    val uuid: String = "",
    val email: String = "",
    val firstName: String = "",
    val lastName: String = "",
    val phoneNumber: String? = null,
    val roleId: Long = 0,
    val isActive: Boolean = true,
    val isLocked: Boolean = false,
    val failedLoginAttempts: Int = 0,
    val lastLoginAt: String? = null,
    val passwordChangedAt: String? = null,
    val createdAt: String? = null,
    val updatedAt: String? = null,
    """),
    ("Role", "v2_roles", """
    val name: String = "",
    val description: String? = null,
    val isSystem: Boolean = false,
    val createdAt: String? = null,
    val updatedAt: String? = null,
    """),
    ("Permission", "v2_permissions", """
    val name: String = "",
    val description: String? = null,
    val module: String = "",
    val createdAt: String? = null,
    val updatedAt: String? = null,
    """),
    ("RolePermissionCrossRef", "v2_role_permissions", """
    val createdAt: String? = null,
    """),
    ("UserRoleCrossRef", "v2_user_roles", """
    val createdAt: String? = null,
    """),
    ("SyncQueueItem", "v2_sync_queue", """
    val tableName: String = "",
    val recordId: Long = 0,
    val operation: String = "insert",
    val payload: String = "",
    val status: String = "pending",
    val retryCount: Int = 0,
    val createdAt: String = "",
    val syncedAt: String? = null,
    """),
]

for cls, table, fields in ENTITIES:
    is_cross = cls in ("RolePermissionCrossRef", "UserRoleCrossRef")
    body = fields.strip()

    if is_cross:
        if cls == "RolePermissionCrossRef":
            primary = "    val roleId: Long = 0,\n    val permissionId: Long = 0,"
            entity_anno = f'@Entity(tableName = "{table}", primaryKeys = ["roleId", "permissionId"])'
        else:
            primary = "    val userId: Long = 0,\n    val roleId: Long = 0,"
            entity_anno = f'@Entity(tableName = "{table}", primaryKeys = ["userId", "roleId"])'
        import_keys = "import androidx.room.Entity"
    else:
        primary = "    @PrimaryKey\n    val id: Long = 0,"
        entity_anno = f'@Entity(tableName = "{table}")'
        import_keys = "import androidx.room.Entity\nimport androidx.room.PrimaryKey"

    text = dedent(f"""
        package com.zivastock.data.local.database.v2.entities

        {import_keys}

        {entity_anno}
        data class {cls}Entity(
        {primary}
        {body}
        )
    """)
    (PACKAGE["entity"] / f"{cls}Entity.kt").write_text(text, encoding="utf-8")

# ----------------------------------------------------------------------------
# DAOs
# ----------------------------------------------------------------------------
for cls, table, _ in ENTITIES:
    name = f"{cls}Dao"
    is_cross = cls in ("RolePermissionCrossRef", "UserRoleCrossRef")

    if is_cross:
        if cls == "RolePermissionCrossRef":
            by_id = f'''
            @Query("SELECT * FROM {table} WHERE roleId = :roleId AND permissionId = :permissionId")
            suspend fun getByIds(roleId: Long, permissionId: Long): RolePermissionCrossRefEntity?
            '''
        else:
            by_id = f'''
            @Query("SELECT * FROM {table} WHERE userId = :userId AND roleId = :roleId")
            suspend fun getByIds(userId: Long, roleId: Long): UserRoleCrossRefEntity?
            '''
    else:
        by_id = f'''
            @Query("SELECT * FROM {table} WHERE id = :id")
            suspend fun getById(id: Long): {cls}Entity?
        '''

    text = dedent(f"""
        package com.zivastock.data.local.database.v2.dao

        import androidx.room.*
        import com.zivastock.data.local.database.v2.entities.{cls}Entity
        import kotlinx.coroutines.flow.Flow

        @Dao
        interface {name} {{
            @Query("SELECT * FROM {table}")
            fun getAll(): Flow<List<{cls}Entity>>

{by_id}

            @Insert(onConflict = OnConflictStrategy.REPLACE)
            suspend fun insert(item: {cls}Entity): Long

            @Insert(onConflict = OnConflictStrategy.REPLACE)
            suspend fun insertAll(items: List<{cls}Entity>): List<Long>

            @Update
            suspend fun update(item: {cls}Entity)

            @Delete
            suspend fun delete(item: {cls}Entity)

            @Query("DELETE FROM {table}")
            suspend fun deleteAll()
        }}
    """)
    (PACKAGE["dao"] / f"{name}.kt").write_text(text, encoding="utf-8")

# ----------------------------------------------------------------------------
# Database
# ----------------------------------------------------------------------------
entity_classes = [f"{cls}Entity::class" for cls, _, _ in ENTITIES]
entity_imports = "\n".join(f"import com.zivastock.data.local.database.v2.entities.{cls}Entity" for cls, _, _ in ENTITIES)
dao_names = [f"{cls}Dao" for cls, _, _ in ENTITIES]
dao_abstracts = "\n".join(f"    abstract fun {name[0].lower() + name[1:]}(): {name}" for name in dao_names)
dao_imports = "\n".join(f"import com.zivastock.data.local.database.v2.dao.{name}" for name in dao_names)

database_text = dedent(f"""
    package com.zivastock.data.local.database

    import android.content.Context
    import androidx.room.Database
    import androidx.room.Room
    import androidx.room.RoomDatabase
    {entity_imports}
    {dao_imports}

    @Database(
        entities = [
            {", ".join(entity_classes)}
        ],
        version = 1,
        exportSchema = false
    )
    abstract class ZivaStockDatabase : RoomDatabase() {{
        {dao_abstracts}

        companion object {{
            @Volatile
            private var INSTANCE: ZivaStockDatabase? = null

            fun getDatabase(context: Context): ZivaStockDatabase {{
                return INSTANCE ?: synchronized(this) {{
                    val instance = Room.databaseBuilder(
                        context.applicationContext,
                        ZivaStockDatabase::class.java,
                        "ziva_stock_v2.db"
                    )
                    .fallbackToDestructiveMigration()
                    .build()
                    INSTANCE = instance
                    instance
                }}
            }}
        }}
    }}
""")
(PACKAGE["database"] / "ZivaStockDatabase.kt").write_text(database_text, encoding="utf-8")

# ----------------------------------------------------------------------------
# DTOs
# ----------------------------------------------------------------------------
DTOS = [
    ("Product", """
    val id: Long? = null,
    val sku: String? = null,
    val barcode: String? = null,
    val productCode: String? = null,
    val categoryId: Long? = null,
    val description: String? = null,
    val unitOfMeasure: String? = null,
    val systemQuantity: Double? = null,
    val unitCost: Double? = null,
    val unitPrice: Double? = null,
    val reorderLevel: Double? = null,
    val isActive: Boolean? = null,
    val createdAt: String? = null,
    val updatedAt: String? = null,
    """),
    ("ProductCategory", """
    val id: Long? = null,
    val name: String? = null,
    val parentId: Long? = null,
    val description: String? = null,
    val isActive: Boolean? = null,
    val createdAt: String? = null,
    val updatedAt: String? = null,
    """),
    ("Location", """
    val id: Long? = null,
    val name: String? = null,
    val type: String? = null,
    val parentId: Long? = null,
    val address: String? = null,
    val isActive: Boolean? = null,
    val createdAt: String? = null,
    val updatedAt: String? = null,
    """),
    ("Shelf", """
    val id: Long? = null,
    val locationId: Long? = null,
    val name: String? = null,
    val description: String? = null,
    val isActive: Boolean? = null,
    val createdAt: String? = null,
    val updatedAt: String? = null,
    """),
    ("ShelfSection", """
    val id: Long? = null,
    val shelfId: Long? = null,
    val name: String? = null,
    val description: String? = null,
    val isActive: Boolean? = null,
    val createdAt: String? = null,
    val updatedAt: String? = null,
    """),
    ("StocktakeSession", """
    val id: Long? = null,
    val uuid: String? = null,
    val name: String? = null,
    val description: String? = null,
    val locationId: Long? = null,
    val sessionType: String? = null,
    val status: String? = null,
    val startTime: String? = null,
    val endTime: String? = null,
    val createdBy: Long? = null,
    val approvedBy: Long? = null,
    val approvedAt: String? = null,
    val createdAt: String? = null,
    val updatedAt: String? = null,
    """),
    ("SessionAssignment", """
    val id: Long? = null,
    val sessionId: Long? = null,
    val userId: Long? = null,
    val shelfSectionId: Long? = null,
    val assignmentRole: String? = null,
    val status: String? = null,
    val assignedBy: Long? = null,
    val assignedAt: String? = null,
    val startedAt: String? = null,
    val completedAt: String? = null,
    """),
    ("FirstCount", """
    val id: Long? = null,
    val sessionId: Long? = null,
    val productId: Long? = null,
    val shelfSectionId: Long? = null,
    val userId: Long? = null,
    val quantity: Double? = null,
    val clientId: String? = null,
    val deviceId: String? = null,
    val source: String? = null,
    val countedAt: String? = null,
    val isSynced: Boolean? = null,
    val syncedAt: String? = null,
    """),
    ("SecondCount", """
    val id: Long? = null,
    val sessionId: Long? = null,
    val productId: Long? = null,
    val shelfSectionId: Long? = null,
    val userId: Long? = null,
    val firstCountId: Long? = null,
    val quantity: Double? = null,
    val clientId: String? = null,
    val deviceId: String? = null,
    val source: String? = null,
    val countedAt: String? = null,
    val isSynced: Boolean? = null,
    val syncedAt: String? = null,
    """),
    ("User", """
    val id: Long? = null,
    val uuid: String? = null,
    val email: String? = null,
    val firstName: String? = null,
    val lastName: String? = null,
    val phoneNumber: String? = null,
    val roleId: Long? = null,
    val isActive: Boolean? = null,
    val isLocked: Boolean? = null,
    val failedLoginAttempts: Int? = null,
    val lastLoginAt: String? = null,
    val passwordChangedAt: String? = null,
    val createdAt: String? = null,
    val updatedAt: String? = null,
    """),
    ("Role", """
    val id: Long? = null,
    val name: String? = null,
    val description: String? = null,
    val isSystem: Boolean? = null,
    val createdAt: String? = null,
    val updatedAt: String? = null,
    """),
    ("Permission", """
    val id: Long? = null,
    val name: String? = null,
    val description: String? = null,
    val module: String? = null,
    val createdAt: String? = null,
    val updatedAt: String? = null,
    """),
    ("SyncPushRequest", """
    val counts: List<FirstCountDto>? = null,
    val secondCounts: List<SecondCountDto>? = null,
    """)
    ,("SyncPullResponse", """
    val products: List<ProductDto>? = null,
    val firstCounts: List<FirstCountDto>? = null,
    val secondCounts: List<SecondCountDto>? = null,
    val locations: List<LocationDto>? = null,
    val sessions: List<StocktakeSessionDto>? = null,
    val syncTimestamp: String? = null,
    """)
    ,("LoginRequest", """
    val email: String? = null,
    val password: String? = null,
    """)
    ,("LoginResponse", """
    val accessToken: String? = null,
    val refreshToken: String? = null,
    val tokenType: String? = null,
    val user: UserDto? = null,
    """)
    ,("RefreshRequest", """
    val refreshToken: String? = null,
    """)
    ,("ApiError", """
    val detail: String? = null,
    """)
]

for cls, body in DTOS:
    text = dedent(f"""
        package com.zivastock.data.remote.dto.v2

        data class {cls}Dto(
        {body.strip()}
        )
    """)
    (PACKAGE["dto"] / f"{cls}Dto.kt").write_text(text, encoding="utf-8")

# ----------------------------------------------------------------------------
# ZivaStockApi v2
# ----------------------------------------------------------------------------
api_text = dedent('''
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

        @GET("products/{barcode}")
        suspend fun getProductByBarcode(@Path("barcode") barcode: String): Response<ProductDto>

        @GET("products/{id}/by-id")
        suspend fun getProductById(@Path("id") id: Long): Response<ProductDto>

        @GET("locations")
        suspend fun getLocations(): Response<List<LocationDto>>

        @GET("locations/{id}")
        suspend fun getLocation(@Path("id") id: Long): Response<LocationDto>

        @GET("locations/{id}/tree")
        suspend fun getLocationTree(@Path("id") id: Long): Response<LocationDto>

        @POST("locations")
        suspend fun createLocation(@Body location: LocationDto): Response<LocationDto>

        @GET("shelves")
        suspend fun getShelves(): Response<List<ShelfDto>>

        @GET("shelf-sections")
        suspend fun getShelfSections(): Response<List<ShelfSectionDto>>

        @GET("sessions")
        suspend fun getSessions(): Response<List<StocktakeSessionDto>>

        @POST("sessions")
        suspend fun createSession(@Body session: StocktakeSessionDto): Response<StocktakeSessionDto>

        @GET("sessions/{id}")
        suspend fun getSession(@Path("id") id: Long): Response<StocktakeSessionDto>

        @GET("first-counts")
        suspend fun getFirstCounts(@Query("session_id") sessionId: Long?): Response<List<FirstCountDto>>

        @POST("first-counts")
        suspend fun createFirstCount(@Body count: FirstCountDto): Response<FirstCountDto>

        @POST("first-counts/bulk")
        suspend fun createFirstCounts(@Body counts: List<FirstCountDto>): Response<List<FirstCountDto>>

        @GET("second-counts")
        suspend fun getSecondCounts(@Query("session_id") sessionId: Long?): Response<List<SecondCountDto>>

        @POST("second-counts")
        suspend fun createSecondCount(@Body count: SecondCountDto): Response<SecondCountDto>

        @POST("second-counts/bulk")
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
''')
(PACKAGE["api"] / "ZivaStockApi.kt").write_text(api_text, encoding="utf-8")

# ----------------------------------------------------------------------------
# Repositories
# ----------------------------------------------------------------------------
REPOS = [
    ("FirstCount", "firstCountDao"),
    ("SecondCount", "secondCountDao"),
    ("Product", "productDao"),
    ("Location", "locationDao"),
    ("Shelf", "shelfDao"),
    ("ShelfSection", "shelfSectionDao"),
    ("StocktakeSession", "stocktakeSessionDao"),
    ("User", "userDao"),
    ("Role", "roleDao"),
    ("Permission", "permissionDao"),
    ("Sync", "syncQueueItemDao"),
]

for repo, dao in REPOS:
    entity = f"{repo}Entity" if repo != "Sync" else "SyncQueueItemEntity"
    dto = f"{repo}Dto" if repo != "Sync" else "SyncPullResponseDto"
    text = dedent(f'''
        package com.zivastock.data.repository.v2

        import com.zivastock.data.local.database.ZivaStockDatabase
        import com.zivastock.data.local.database.v2.entities.{entity}
        import com.zivastock.data.remote.api.ZivaStockApi
        import com.zivastock.data.remote.dto.v2.{dto}
        import kotlinx.coroutines.flow.Flow
        import javax.inject.Inject

        class {repo}Repository @Inject constructor(
            private val database: ZivaStockDatabase,
            private val api: ZivaStockApi
        ) {{
            private val dao = database.{dao}()

            fun getAll(): Flow<List<{entity}>> = dao.getAll()

            suspend fun getById(id: Long): {entity}? = dao.getById(id)

            suspend fun save(entity: {entity}) {{
                // TODO: implement local save and queue for sync
                dao.insert(entity)
            }}

            suspend fun saveAll(entities: List<{entity}>) {{
                dao.insertAll(entities)
            }}

            suspend fun delete(entity: {entity}) {{
                dao.delete(entity)
            }}

            suspend fun fetchFromServer() {{
                // TODO: call api and map to entities
            }}
        }}
    ''')
    (PACKAGE["repo"] / f"{repo}Repository.kt").write_text(text, encoding="utf-8")

# ----------------------------------------------------------------------------
# DI modules
# ----------------------------------------------------------------------------
database_v2_module = dedent('''
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
''')
for cls, _, _ in ENTITIES:
    dao = f"{cls}Dao"
    name = f"provide{dao}"
    database_v2_module += f"""

        @Provides
        @Singleton
        fun {name}(database: ZivaStockDatabase): com.zivastock.data.local.database.v2.dao.{dao} {{
            return database.{dao[0].lower() + dao[1:]}()
        }}
"""
database_v2_module += "}\n"
(PACKAGE["di"] / "DatabaseV2Module.kt").write_text(database_v2_module, encoding="utf-8")

repo_v2_module = dedent('''
    package com.zivastock.di

    import com.zivastock.data.repository.v2.*
    import dagger.Binds
    import dagger.Module
    import dagger.hilt.InstallIn
    import dagger.hilt.components.SingletonComponent

    // Repositories use constructor injection; this module may be used for interface bindings in the future.
    @Module
    @InstallIn(SingletonComponent::class)
    abstract class RepositoryV2Module {
        // TODO: add @Binds methods if interfaces are introduced
    }
''')
(PACKAGE["di"] / "RepositoryV2Module.kt").write_text(repo_v2_module, encoding="utf-8")

# ----------------------------------------------------------------------------
# Update NetworkModule to provide ZivaStockApi
# ----------------------------------------------------------------------------
network_module_path = PACKAGE["di"] / "NetworkModule.kt"
network_module = network_module_path.read_text(encoding="utf-8")
if "ZivaStockApi" not in network_module:
    insert = "\n    @Provides\n    @Singleton\n    fun provideZivaStockApi(retrofit: Retrofit): com.zivastock.data.remote.api.ZivaStockApi {\n        return retrofit.create(com.zivastock.data.remote.api.ZivaStockApi::class.java)\n    }\n"
    # Insert before the last closing brace
    idx = network_module.rfind("}")
    if idx != -1:
        new_text = network_module[:idx] + insert + network_module[idx:]
        network_module_path.write_text(new_text, encoding="utf-8")

print("v2 data layer generated.")
