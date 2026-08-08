package com.zivastock.presentation.counting

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.zivastock.data.local.database.entities.CountEntity
import com.zivastock.data.local.database.entities.ProductEntity
import com.zivastock.data.local.preferences.SharedPreferencesManager
import com.zivastock.data.repository.AuthRepository
import com.zivastock.data.repository.CountRepository
import com.zivastock.data.repository.ProductRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.launch
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale
import java.util.UUID
import javax.inject.Inject

@HiltViewModel
class CountingViewModel @Inject constructor(
    private val productRepository: ProductRepository,
    private val countRepository: CountRepository,
    private val authRepository: AuthRepository,
    private val preferences: SharedPreferencesManager
) : ViewModel() {

    private val _scannedProduct = MutableLiveData<ProductEntity?>()
    val scannedProduct: LiveData<ProductEntity?> = _scannedProduct

    private val _saveState = MutableLiveData<SaveState>()
    val saveState: LiveData<SaveState> = _saveState

    private val _counts = MutableLiveData<List<CountEntity>>()
    val counts: LiveData<List<CountEntity>> = _counts

    private val _userName = MutableLiveData<String>()
    val userName: LiveData<String> = _userName

    private var userId: Int = 0
    private var sessionId: Int = 1
    private var sectionId: Int = 1

    init {
        viewModelScope.launch {
            val name = preferences.userName.first()
            _userName.value = name ?: "Counter"
            val id = preferences.userId.first()
            userId = id?.toIntOrNull() ?: 0
        }
    }

    fun setLocation(sessionId: Int, sectionId: Int) {
        this.sessionId = sessionId
        this.sectionId = sectionId
        loadCounts()
    }

    fun onBarcodeScanned(barcode: String) {
        viewModelScope.launch {
            val product = productRepository.getProductByBarcode(barcode)
            _scannedProduct.value = product
        }
    }

    fun saveCount(productId: Int, quantity: Double) {
        if (quantity < 0) {
            _saveState.value = SaveState.Error("Quantity must be 0 or more")
            return
        }

        viewModelScope.launch {
            val timestamp = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss'Z'", Locale.getDefault()).format(Date())
            val count = CountEntity(
                id = UUID.randomUUID().hashCode(),
                productId = productId,
                sectionId = sectionId,
                quantity = quantity,
                userId = userId,
                sessionId = sessionId,
                countedAt = timestamp,
                syncedAt = null,
                isSynced = false
            )
            countRepository.insertCount(count)
            _saveState.value = SaveState.Success
            loadCounts()
            _scannedProduct.value = null
        }
    }

    fun loadCounts() {
        viewModelScope.launch {
            val list = countRepository.getCountsBySessionAndSection(sessionId, sectionId)
            _counts.value = list
        }
    }

    fun logout() {
        viewModelScope.launch {
            authRepository.logout()
        }
    }

    sealed class SaveState {
        object Idle : SaveState()
        object Success : SaveState()
        data class Error(val message: String) : SaveState()
    }
}
