package com.zivastock.data.repository

import com.zivastock.data.local.preferences.SecureTokenManager
import com.zivastock.data.local.preferences.SharedPreferencesManager
import com.zivastock.data.remote.api.ZivaStockApi
import com.zivastock.data.remote.dto.v2.LoginRequestDto
import com.zivastock.data.remote.dto.v2.LoginResponseDto
import com.zivastock.data.remote.dto.v2.RegisterRequestDto
import com.zivastock.utils.NetworkUtils
import kotlinx.coroutines.flow.firstOrNull
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class AuthRepository @Inject constructor(
    private val api: ZivaStockApi,
    private val secureTokenManager: SecureTokenManager,
    private val sharedPreferencesManager: SharedPreferencesManager,
    private val networkUtils: NetworkUtils
) {

    suspend fun login(email: String, password: String): Result<LoginResult> {
        val trimmedEmail = email.trim().lowercase()

        if (trimmedEmail.isBlank() || password.isBlank()) {
            return Result.failure(Exception("Email and password are required"))
        }

        if (networkUtils.isNetworkAvailable()) {
            try {
                val response = api.login(LoginRequestDto(trimmedEmail, password))

                if (response.isSuccessful && response.body() != null) {
                    val body = response.body()!!
                    val accessToken = body.accessToken
                        ?: return Result.failure(Exception("No access token received"))

                    val user = body.user
                    val userId = user?.id?.toString() ?: ""
                    val userEmail = user?.email ?: trimmedEmail
                    val userName = "${user?.firstName.orEmpty()} ${user?.lastName.orEmpty()}".trim()
                    val roleId = user?.roleId?.toString()

                    secureTokenManager.saveTokens(accessToken, body.refreshToken)
                    secureTokenManager.saveUser(userId, userEmail, userName, roleId)
                    secureTokenManager.saveCredentials(userEmail, password)
                    secureTokenManager.setOfflineSession(false)

                    sharedPreferencesManager.saveUserInfo(userId, userEmail, userName)

                    return Result.success(LoginResult(userName, userEmail, false))
                } else {
                    return Result.failure(Exception("Invalid credentials"))
                }
            } catch (e: Exception) {
                // fall through to offline attempt
            }
        }

        if (secureTokenManager.validateOfflineCredentials(trimmedEmail, password)) {
            secureTokenManager.setOfflineSession(true)
            val name = secureTokenManager.getUserName().orEmpty()
            val userEmail = secureTokenManager.getUserEmail().orEmpty()
            return Result.success(LoginResult(name, userEmail, true))
        }

        return Result.failure(
            Exception(
                if (networkUtils.isNetworkAvailable()) "Login failed" else "No network and no saved credentials"
            )
        )
    }

    suspend fun register(firstName: String, lastName: String, email: String, password: String): Result<LoginResult> {
        val trimmedEmail = email.trim().lowercase()
        if (firstName.isBlank() || lastName.isBlank() || trimmedEmail.isBlank() || password.length < 8) {
            return Result.failure(Exception("Name, email, and a password of at least 8 characters are required"))
        }
        return try {
            val response = api.register(RegisterRequestDto(trimmedEmail, firstName.trim(), lastName.trim(), password))
            if (response.isSuccessful) login(trimmedEmail, password)
            else Result.failure(Exception("Registration failed (${response.code()})"))
        } catch (e: Exception) {
            Result.failure(Exception("Unable to connect to the server: ${e.message ?: "network error"}"))
        }
    }

    suspend fun refreshToken(): Result<LoginResponseDto> {
        return try {
            val refreshToken = secureTokenManager.getRefreshToken()

            if (!refreshToken.isNullOrEmpty()) {
                val response = api.refreshToken(
                    com.zivastock.data.remote.dto.v2.RefreshRequestDto(refreshToken)
                )

                if (response.isSuccessful && response.body() != null) {
                    val tokenResponse = response.body()!!
                    secureTokenManager.saveTokens(
                        tokenResponse.accessToken ?: "",
                        refreshToken
                    )
                    Result.success(tokenResponse)
                } else {
                    Result.failure(Exception("Token refresh failed"))
                }
            } else {
                Result.failure(Exception("No refresh token available"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun logout() {
        secureTokenManager.clearAll()
        sharedPreferencesManager.clearAll()
    }

    fun isLoggedIn(): Boolean {
        return secureTokenManager.isLoggedIn()
    }

    fun getAccessToken(): String? = secureTokenManager.getAccessToken()

    data class LoginResult(
        val userName: String,
        val email: String,
        val isOffline: Boolean
    )
}
