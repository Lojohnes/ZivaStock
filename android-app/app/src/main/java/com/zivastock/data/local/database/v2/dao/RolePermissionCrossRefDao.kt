
package com.zivastock.data.local.database.v2.dao

import androidx.room.*
import com.zivastock.data.local.database.v2.entities.RolePermissionCrossRefEntity
import kotlinx.coroutines.flow.Flow

@Dao
interface RolePermissionCrossRefDao {
    @Query("SELECT * FROM v2_role_permissions")
    fun getAll(): Flow<List<RolePermissionCrossRefEntity>>


    @Query("SELECT * FROM v2_role_permissions WHERE roleId = :roleId AND permissionId = :permissionId")
    suspend fun getByIds(roleId: Long, permissionId: Long): RolePermissionCrossRefEntity?


    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(item: RolePermissionCrossRefEntity): Long

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertAll(items: List<RolePermissionCrossRefEntity>): List<Long>

    @Update
    suspend fun update(item: RolePermissionCrossRefEntity)

    @Delete
    suspend fun delete(item: RolePermissionCrossRefEntity)

    @Query("DELETE FROM v2_role_permissions")
    suspend fun deleteAll()
}
