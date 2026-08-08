package com.zivastock.ui.permissions

import androidx.lifecycle.LiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.asLiveData
import androidx.lifecycle.map
import androidx.lifecycle.viewModelScope
import com.zivastock.data.local.database.v2.entities.RoleEntity
import com.zivastock.data.rbac.PermissionManager
import com.zivastock.data.repository.v2.RoleRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class PermissionsViewModel @Inject constructor(
    private val roleRepository: RoleRepository,
    private val permissionManager: PermissionManager
) : ViewModel() {

    val roles: LiveData<List<RoleEntity>> = roleRepository.getAll().asLiveData()

    init {
        viewModelScope.launch {
            permissionManager.ensureDefaults()
        }
    }
}
