package com.zivastock.ui.dashboard

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.asLiveData
import androidx.lifecycle.viewModelScope
import com.zivastock.data.local.database.v2.entities.StocktakeSessionEntity
import com.zivastock.data.repository.v2.DashboardRepository
import com.zivastock.data.repository.v2.SessionRepository
import com.zivastock.data.session.ActiveSessionDetails
import com.zivastock.data.session.SessionManager
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.map
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class DashboardViewModel @Inject constructor(
    private val sessionManager: SessionManager,
    private val sessionRepository: SessionRepository,
    private val dashboardRepository: DashboardRepository
) : ViewModel() {

    val activeSession: LiveData<StocktakeSessionEntity?> = sessionManager.activeSessionLiveData

    private val _details = MutableLiveData<ActiveSessionDetails?>(null)
    val details: LiveData<ActiveSessionDetails?> = _details

    val dashboardStats: LiveData<DashboardStats> = dashboardRepository
        .getDashboardStats()
        .asLiveData()

    val chartData: LiveData<DashboardChartData> = dashboardRepository
        .getDashboardStats()
        .map { dashboardRepository.getChartData(it) }
        .asLiveData()

    private val _syncState = MutableLiveData<SyncState>(SyncState.Idle)
    val syncState: LiveData<SyncState> = _syncState

    init {
        sync()
    }

    fun sync() {
        viewModelScope.launch {
            _syncState.value = SyncState.Loading
            val result = sessionManager.sync()
            _syncState.value = result.fold(
                onSuccess = { SyncState.Success(it?.name.orEmpty()) },
                onFailure = { SyncState.Error(it.message ?: "Session sync failed") }
            )
        }
    }

    fun loadDetails(session: StocktakeSessionEntity?) {
        if (session == null) {
            _details.value = null
            return
        }
        viewModelScope.launch {
            val location = sessionRepository.getLocationById(session.locationId)
            val shelves = sessionRepository.getShelvesForLocation(session.locationId)
            val shelfIds = shelves.map { it.id }
            val sections = if (shelfIds.isNotEmpty()) {
                sessionRepository.getSectionsForShelves(shelfIds)
            } else {
                emptyList()
            }

            val shelfLines = shelves.map { shelf ->
                val sectionNames = sections
                    .filter { it.shelfId == shelf.id }
                    .joinToString(", ") { it.name }
                "${shelf.name}${if (sectionNames.isNotBlank()) ": $sectionNames" else ""}"
            }

            _details.value = ActiveSessionDetails(
                id = session.id,
                name = session.name,
                description = session.description,
                status = session.status,
                locationName = location?.name ?: "Unknown location",
                sessionType = session.sessionType,
                shelves = shelfLines
            )
        }
    }

    fun onSyncHandled() {
        _syncState.value = SyncState.Idle
    }

    sealed class SyncState {
        object Idle : SyncState()
        object Loading : SyncState()
        data class Success(val sessionName: String) : SyncState()
        data class Error(val message: String) : SyncState()
    }
}
