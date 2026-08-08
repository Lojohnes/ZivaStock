package com.zivastock.presentation.sync

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.zivastock.data.local.preferences.SharedPreferencesManager
import com.zivastock.data.repository.CountRepository
import com.zivastock.utils.NetworkUtils
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class SyncStatusViewModel @Inject constructor(
    private val countRepository: CountRepository,
    private val preferences: SharedPreferencesManager,
    private val networkUtils: NetworkUtils
) : ViewModel() {

    private val _syncStatus = MutableStateFlow(SyncStatus())
    val syncStatus: StateFlow<SyncStatus> = _syncStatus

    fun refreshStatus() {
        viewModelScope.launch {
            val pending = countRepository.getUnsyncedCounts().size
            val lastSync = preferences.lastSyncTimestamp.first()
            val isOnline = networkUtils.isNetworkAvailable()
            _syncStatus.value = SyncStatus(pending, lastSync, isOnline)
        }
    }

    data class SyncStatus(
        val pendingCounts: Int = 0,
        val lastSync: String? = null,
        val isOnline: Boolean = false
    )
}
