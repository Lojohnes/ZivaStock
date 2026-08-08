package com.zivastock.data.session

import androidx.lifecycle.LiveData
import androidx.lifecycle.asLiveData
import com.zivastock.data.local.database.v2.entities.StocktakeSessionEntity
import com.zivastock.data.repository.v2.SessionRepository
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class SessionManager @Inject constructor(
    private val repository: SessionRepository
) {

    private val _activeSession = MutableStateFlow<StocktakeSessionEntity?>(null)
    val activeSession: StateFlow<StocktakeSessionEntity?> = _activeSession.asStateFlow()

    val activeSessionLiveData: LiveData<StocktakeSessionEntity?> = repository.getActiveSession().asLiveData()

    init {
        // Observe the database source of truth and keep the in-memory snapshot up to date
        CoroutineScope(Dispatchers.IO).launch {
            repository.getActiveSession().collect { session ->
                _activeSession.value = session
            }
        }
    }

    suspend fun sync(): Result<StocktakeSessionEntity?> {
        return repository.syncActiveSession()
    }

    fun activeSessionId(): Long? = _activeSession.value?.id

    fun hasActiveSession(): Boolean = _activeSession.value != null
}
