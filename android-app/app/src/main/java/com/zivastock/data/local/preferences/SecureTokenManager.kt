package com.zivastock.data.local.preferences

import android.content.Context
import android.content.SharedPreferences
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKeys
import dagger.hilt.android.qualifiers.ApplicationContext
import java.security.MessageDigest
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class SecureTokenManager @Inject constructor(
    @ApplicationContext private val context: Context
) {

    private val prefs: SharedPreferences by lazy { createPreferences() }

    private fun createPreferences(): SharedPreferences {
        return try {
            val masterKeyAlias = MasterKeys.getOrCreate(MasterKeys.AES256_GCM_SPEC)

            EncryptedSharedPreferences.create(
                SECURE_PREFS_FILE,
                masterKeyAlias,
                context,
                EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
                EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
            )
        } catch (e: Exception) {
            context.getSharedPreferences(FALLBACK_PREFS_FILE, Context.MODE_PRIVATE)
        }
    }

    fun saveTokens(accessToken: String, refreshToken: String?) {
        prefs.edit()
            .putString(KEY_ACCESS_TOKEN, accessToken)
            .putString(KEY_REFRESH_TOKEN, refreshToken)
            .apply()
    }

    fun saveUser(userId: String, email: String, name: String, roleId: String?) {
        prefs.edit()
            .putString(KEY_USER_ID, userId)
            .putString(KEY_USER_EMAIL, email)
            .putString(KEY_USER_NAME, name)
            .putString(KEY_USER_ROLE_ID, roleId)
            .apply()
    }

    fun saveCredentials(email: String, password: String) {
        val hash = sha256("${email.lowercase().trim()}:$password")
        prefs.edit()
            .putString(KEY_USER_EMAIL, email.lowercase().trim())
            .putString(KEY_PASSWORD_HASH, hash)
            .putBoolean(KEY_OFFLINE_MODE, false)
            .apply()
    }

    fun setOfflineSession(isOffline: Boolean) {
        prefs.edit()
            .putBoolean(KEY_OFFLINE_MODE, isOffline)
            .apply()
    }

    fun validateOfflineCredentials(email: String, password: String): Boolean {
        val storedEmail = getUserEmail() ?: return false
        val storedHash = prefs.getString(KEY_PASSWORD_HASH, null) ?: return false
        return storedEmail.equals(email.trim(), ignoreCase = true) &&
                storedHash == sha256("${email.lowercase().trim()}:$password")
    }

    fun getAccessToken(): String? = prefs.getString(KEY_ACCESS_TOKEN, null)

    fun getRefreshToken(): String? = prefs.getString(KEY_REFRESH_TOKEN, null)

    fun getUserId(): String? = prefs.getString(KEY_USER_ID, null)

    fun getUserEmail(): String? = prefs.getString(KEY_USER_EMAIL, null)

    fun getUserName(): String? = prefs.getString(KEY_USER_NAME, null)

    fun getUserRoleId(): String? = prefs.getString(KEY_USER_ROLE_ID, null)

    fun isOfflineSession(): Boolean = prefs.getBoolean(KEY_OFFLINE_MODE, false)

    fun isLoggedIn(): Boolean {
        return !getAccessToken().isNullOrEmpty() ||
                (isOfflineSession() && !getUserEmail().isNullOrEmpty())
    }

    fun clearAll() {
        prefs.edit().clear().apply()
    }

    private fun sha256(input: String): String {
        val bytes = MessageDigest.getInstance("SHA-256").digest(input.toByteArray(Charsets.UTF_8))
        return bytes.joinToString("") { "%02x".format(it) }
    }

    companion object {
        private const val SECURE_PREFS_FILE = "zivastock_secure_tokens"
        private const val FALLBACK_PREFS_FILE = "zivastock_secure_tokens_fallback"

        private const val KEY_ACCESS_TOKEN = "access_token"
        private const val KEY_REFRESH_TOKEN = "refresh_token"
        private const val KEY_USER_ID = "user_id"
        private const val KEY_USER_EMAIL = "user_email"
        private const val KEY_USER_NAME = "user_name"
        private const val KEY_USER_ROLE_ID = "user_role_id"
        private const val KEY_PASSWORD_HASH = "password_hash"
        private const val KEY_OFFLINE_MODE = "offline_mode"
    }
}
