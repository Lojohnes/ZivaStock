package com.zivastock.ui.sync

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.zivastock.sync.SyncEngine
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class SyncViewModel @Inject constructor(
    private val syncEngine: SyncEngine,
) : ViewModel() {
    private val _state = MutableLiveData<SyncState>(SyncState.Idle)
    val state: LiveData<SyncState> = _state

    fun sync() {
        if (_state.value is SyncState.Loading) return
        _state.value = SyncState.Loading
        viewModelScope.launch {
            try {
                syncEngine.performSync()
                _state.value = SyncState.Success("Synchronization completed successfully")
            } catch (error: Exception) {
                _state.value = SyncState.Error(error.message ?: "Synchronization failed")
            }
        }
    }

    sealed class SyncState {
        data object Idle : SyncState()
        data object Loading : SyncState()
        data class Success(val message: String) : SyncState()
        data class Error(val message: String) : SyncState()
    }
}
