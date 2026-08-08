
package com.zivastock.data.local.database.v2.dao

import androidx.room.*
import com.zivastock.data.local.database.v2.entities.PermissionEntity
import kotlinx.coroutines.flow.Flow

@Dao
interface PermissionDao {
    @Query("SELECT * FROM v2_permissions")
    fun getAll(): Flow<List<PermissionEntity>>


    @Query("SELECT * FROM v2_permissions WHERE id = :id")
    suspend fun getById(id: Long): PermissionEntity?

    @Query("""
        SELECT p.module FROM v2_permissions p
        INNER JOIN v2_role_permissions rp ON p.id = rp.permissionId
        WHERE rp.roleId = :roleId
    """)
    suspend fun getModulesForRole(roleId: Long): List<String>


    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(item: PermissionEntity): Long

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertAll(items: List<PermissionEntity>): List<Long>

    @Update
    suspend fun update(item: PermissionEntity)

    @Delete
    suspend fun delete(item: PermissionEntity)

    @Query("DELETE FROM v2_permissions")
    suspend fun deleteAll()
}
