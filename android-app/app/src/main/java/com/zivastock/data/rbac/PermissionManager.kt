package com.zivastock.data.rbac

import com.zivastock.R
import com.zivastock.data.local.database.ZivaStockDatabase
import com.zivastock.data.local.database.v2.entities.PermissionEntity
import com.zivastock.data.local.database.v2.entities.RoleEntity
import com.zivastock.data.local.database.v2.entities.RolePermissionCrossRefEntity
import com.zivastock.data.local.preferences.SecureTokenManager
import com.zivastock.data.remote.api.ZivaStockApi
import com.zivastock.data.remote.dto.v2.PermissionDto
import com.zivastock.data.remote.dto.v2.RoleDto
import com.zivastock.utils.NetworkUtils
import kotlinx.coroutines.flow.first
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class PermissionManager @Inject constructor(
    private val database: ZivaStockDatabase,
    private val api: ZivaStockApi,
    private val secureTokenManager: SecureTokenManager,
    private val networkUtils: NetworkUtils
) {

    suspend fun ensureDefaults() {
        val existing = database.roleDao().getAll().first()
        if (existing.isNotEmpty()) return

        val (roles, permissions, crossRefs) = buildDefaultRbac()
        database.roleDao().insertAll(roles)
        database.permissionDao().insertAll(permissions)
        database.rolePermissionCrossRefDao().insertAll(crossRefs)
    }

    suspend fun sync() {
        if (!networkUtils.isNetworkAvailable()) return

        val userId = secureTokenManager.getUserId()?.toLongOrNull() ?: return
        val roleId = secureTokenManager.getUserRoleId()?.toLongOrNull() ?: return

        try {
            val rolesResponse = api.getRoles()
            if (rolesResponse.isSuccessful && rolesResponse.body() != null) {
                val roles = rolesResponse.body()!!.map { it.toEntity() }
                database.roleDao().insertAll(roles)
            }

            val permissionsResponse = api.getUserPermissions(userId)
            if (permissionsResponse.isSuccessful && permissionsResponse.body() != null) {
                val permissions = permissionsResponse.body()!!.map { it.toEntity() }
                database.permissionDao().insertAll(permissions)

                val crossRefs = permissions.map { permission ->
                    RolePermissionCrossRefEntity(roleId, permission.id)
                }
                database.rolePermissionCrossRefDao().deleteAll()
                database.rolePermissionCrossRefDao().insertAll(crossRefs)
            }
        } catch (e: Exception) {
            // keep existing local data on sync failure
        }
    }

    suspend fun getAllowedMenuIds(): Set<Int> {
        val roleId = secureTokenManager.getUserRoleId()?.toLongOrNull()
            ?: return ALL_MENU_IDS

        if (isSuperRole(roleId)) return ALL_MENU_IDS

        val modules = database.permissionDao().getModulesForRole(roleId)
        if (modules.isEmpty()) return ALL_MENU_IDS

        return modules.mapNotNull { moduleToMenuId[it] }.toSet()
    }

    suspend fun canAccessMenuItem(itemId: Int): Boolean {
        return getAllowedMenuIds().contains(itemId)
    }

    private fun isSuperRole(roleId: Long): Boolean {
        return roleId == ROLE_ADMINISTRATOR || roleId == ROLE_DEVELOPER
    }

    private fun buildDefaultRbac(): Triple<List<RoleEntity>, List<PermissionEntity>, List<RolePermissionCrossRefEntity>> {
        val roles = listOf(
            RoleEntity(ROLE_ADMINISTRATOR, "Administrator", "Full access to all modules and settings", true),
            RoleEntity(ROLE_DEVELOPER, "Developer", "Can access everything including Reports, Users, Assign Roles", true),
            RoleEntity(ROLE_SUPERVISOR, "Supervisor", "Can view Reports, Correct mistakes, and Print Reports", true),
            RoleEntity(ROLE_COUNTER, "Counter", "Can Access FirstCount, SecondCount, and Products only", true),
            RoleEntity(ROLE_VIEWER, "Viewer", "Can view Reports and Products only", true)
        )

        val permissions = listOf(
            PermissionEntity(PERM_FIRST_COUNT, "First Count", "Access first count screen", MODULE_FIRST_COUNT),
            PermissionEntity(PERM_SECOND_COUNT, "Second Count", "Access second count screen", MODULE_SECOND_COUNT),
            PermissionEntity(PERM_PRODUCTS, "Products", "Access products list", MODULE_PRODUCTS),
            PermissionEntity(PERM_BUTCHERY_FNV, "Butchery FnV", "Access butchery and fresh produce count", MODULE_BUTCHERY_FNV),
            PermissionEntity(PERM_CONSOLIDATION, "Consolidation", "View consolidation / comparison report", MODULE_CONSOLIDATION),
            PermissionEntity(PERM_PERMISSIONS, "Permissions", "View and manage user permissions", MODULE_PERMISSIONS),
            PermissionEntity(PERM_REPORTS, "Reports", "View and print reports", MODULE_REPORTS),
            PermissionEntity(PERM_SYNC, "Sync", "View sync status and trigger sync", MODULE_SYNC)
        )

        val crossRefs = mutableListOf<RolePermissionCrossRefEntity>()

        // Administrator and Developer: all permissions
        listOf(ROLE_ADMINISTRATOR, ROLE_DEVELOPER).forEach { roleId ->
            permissions.forEach { permission ->
                crossRefs.add(RolePermissionCrossRefEntity(roleId, permission.id))
            }
        }

        // Supervisor: count, products, consolidation, reports, sync, permissions
        listOf(
            PERM_FIRST_COUNT, PERM_SECOND_COUNT, PERM_PRODUCTS, PERM_CONSOLIDATION,
            PERM_REPORTS, PERM_SYNC, PERM_PERMISSIONS
        ).forEach { permissionId ->
            crossRefs.add(RolePermissionCrossRefEntity(ROLE_SUPERVISOR, permissionId))
        }

        // Counter: first, second, products, butchery
        listOf(PERM_FIRST_COUNT, PERM_SECOND_COUNT, PERM_PRODUCTS, PERM_BUTCHERY_FNV).forEach { permissionId ->
            crossRefs.add(RolePermissionCrossRefEntity(ROLE_COUNTER, permissionId))
        }

        // Viewer: products, reports
        listOf(PERM_PRODUCTS, PERM_REPORTS).forEach { permissionId ->
            crossRefs.add(RolePermissionCrossRefEntity(ROLE_VIEWER, permissionId))
        }

        return Triple(roles, permissions, crossRefs)
    }

    private fun PermissionDto.toEntity(): PermissionEntity {
        return PermissionEntity(
            id = id ?: 0,
            name = name.orEmpty(),
            description = description,
            module = module.orEmpty()
        )
    }

    private fun RoleDto.toEntity(): RoleEntity {
        return RoleEntity(
            id = id ?: 0,
            name = name.orEmpty(),
            description = description,
            isSystem = isSystem ?: false
        )
    }

    companion object {
        const val ROLE_ADMINISTRATOR = 1L
        const val ROLE_DEVELOPER = 2L
        const val ROLE_SUPERVISOR = 3L
        const val ROLE_COUNTER = 4L
        const val ROLE_VIEWER = 5L

        const val PERM_FIRST_COUNT = 1L
        const val PERM_SECOND_COUNT = 2L
        const val PERM_PRODUCTS = 3L
        const val PERM_BUTCHERY_FNV = 4L
        const val PERM_CONSOLIDATION = 5L
        const val PERM_PERMISSIONS = 6L
        const val PERM_REPORTS = 7L
        const val PERM_SYNC = 8L

        const val MODULE_FIRST_COUNT = "first_count"
        const val MODULE_SECOND_COUNT = "second_count"
        const val MODULE_PRODUCTS = "products"
        const val MODULE_BUTCHERY_FNV = "butchery_fnv"
        const val MODULE_CONSOLIDATION = "consolidation"
        const val MODULE_PERMISSIONS = "permissions"
        const val MODULE_REPORTS = "reports"
        const val MODULE_SYNC = "sync"

        val ALL_MENU_IDS = setOf(
            R.id.firstCountFragment,
            R.id.productsFragment,
            R.id.secondCountFragment,
            R.id.butcheryFnVFragment,
            R.id.permissionsFragment,
            R.id.reportsFragment,
            R.id.syncFragment
        )

        val moduleToMenuId = mapOf(
            MODULE_FIRST_COUNT to R.id.firstCountFragment,
            MODULE_SECOND_COUNT to R.id.secondCountFragment,
            MODULE_PRODUCTS to R.id.productsFragment,
            MODULE_BUTCHERY_FNV to R.id.butcheryFnVFragment,
            MODULE_CONSOLIDATION to R.id.consolidationFragment,
            MODULE_PERMISSIONS to R.id.permissionsFragment,
            MODULE_REPORTS to R.id.reportsFragment,
            MODULE_SYNC to R.id.syncFragment
        )
    }
}
