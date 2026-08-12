package com.zivastock.ui.login

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.zivastock.data.rbac.PermissionManager
import com.zivastock.data.repository.AuthRepository
import com.zivastock.data.session.SessionManager
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class LoginViewModel @Inject constructor(
    private val authRepository: AuthRepository,
    private val permissionManager: PermissionManager,
    private val sessionManager: SessionManager
) : ViewModel() {

    private val _loginState = MutableLiveData<LoginState>(LoginState.Idle)
    val loginState: LiveData<LoginState> = _loginState

    init {
        if (authRepository.isLoggedIn()) {
            _loginState.value = LoginState.AlreadyLoggedIn
        }
    }

    fun login(email: String, password: String) {
        if (email.isBlank() || password.isBlank()) {
            _loginState.value = LoginState.Error("Email and password are required")
            return
        }

        _loginState.value = LoginState.Loading
        viewModelScope.launch {
            val result = authRepository.login(email, password)
            result.onSuccess {
                permissionManager.ensureDefaults()
                permissionManager.sync()
                sessionManager.sync()
            }
            _loginState.value = result.fold(
                onSuccess = { LoginState.Success(it.isOffline) },
                onFailure = { LoginState.Error(it.message ?: "Login failed") }
            )
        }
    }

    fun register(firstName: String, lastName: String, email: String, password: String) {
        _loginState.value = LoginState.Loading
        viewModelScope.launch {
            val result = authRepository.register(firstName, lastName, email, password)
            result.onSuccess {
                permissionManager.ensureDefaults()
                permissionManager.sync()
                sessionManager.sync()
            }
            _loginState.value = result.fold(
                onSuccess = { LoginState.Success(it.isOffline) },
                onFailure = { LoginState.Error(it.message ?: "Registration failed") }
            )
        }
    }

    fun resetState() {
        _loginState.value = LoginState.Idle
    }

    sealed class LoginState {
        object Idle : LoginState()
        object Loading : LoginState()
        object AlreadyLoggedIn : LoginState()
        data class Success(val isOffline: Boolean) : LoginState()
        data class Error(val message: String) : LoginState()
    }
}
