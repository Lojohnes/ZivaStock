package com.zivastock

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.zivastock.data.repository.AuthRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class MainViewModel @Inject constructor(
    private val authRepository: AuthRepository
) : ViewModel() {

    private val _logoutEvent = MutableLiveData(false)
    val logoutEvent: LiveData<Boolean> = _logoutEvent

    fun logout() {
        viewModelScope.launch {
            authRepository.logout()
            _logoutEvent.postValue(true)
        }
    }

    fun onLogoutHandled() {
        _logoutEvent.value = false
    }
}
