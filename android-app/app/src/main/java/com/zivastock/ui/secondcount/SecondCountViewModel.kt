package com.zivastock.ui.secondcount

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.asLiveData
import androidx.lifecycle.viewModelScope
import com.zivastock.data.local.database.v2.entities.LocationEntity
import com.zivastock.data.local.database.v2.entities.ProductEntity
import com.zivastock.data.local.database.v2.entities.SecondCountEntity
import com.zivastock.data.local.database.v2.entities.ShelfEntity
import com.zivastock.data.local.database.v2.entities.ShelfSectionEntity
import com.zivastock.data.local.database.v2.entities.StocktakeSessionEntity
import com.zivastock.data.local.preferences.SecureTokenManager
import com.zivastock.data.repository.v2.ProductRepository
import com.zivastock.data.repository.v2.SecondCountRepository
import com.zivastock.data.repository.v2.SessionRepository
import com.zivastock.data.session.SessionManager
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.launch
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale
import javax.inject.Inject

@HiltViewModel
class SecondCountViewModel @Inject constructor(
    private val secondCountRepository: SecondCountRepository,
    private val productRepository: ProductRepository,
    private val sessionRepository: SessionRepository,
    private val sessionManager: SessionManager,
    private val secureTokenManager: SecureTokenManager
) : ViewModel() {

    val activeSession: LiveData<StocktakeSessionEntity?> = sessionManager.activeSessionLiveData

    private val _locations = MutableLiveData<List<LocationEntity>>(emptyList())
    val locations: LiveData<List<LocationEntity>> = _locations

    private val _shelves = MutableLiveData<List<ShelfEntity>>(emptyList())
    val shelves: LiveData<List<ShelfEntity>> = _shelves

    private val _sections = MutableLiveData<List<ShelfSectionEntity>>(emptyList())
    val sections: LiveData<List<ShelfSectionEntity>> = _sections

    private val _product = MutableLiveData<ProductEntity?>(null)
    val product: LiveData<ProductEntity?> = _product

    private val _wrongProduct = MutableLiveData(false)
    val wrongProduct: LiveData<Boolean> = _wrongProduct

    private val _saveResult = MutableLiveData<Result<Long>>()
    val saveResult: LiveData<Result<Long>> = _saveResult

    val allCounts: LiveData<List<SecondCountEntity>> = secondCountRepository.getAll().asLiveData()

    private val dateFormat = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss", Locale.getDefault())

    init {
        loadCatalog()
    }

    private fun loadCatalog() {
        viewModelScope.launch {
            val session = sessionManager.activeSession.first()
            val locationId = session?.locationId

            _locations.value = if (locationId != null && locationId != 0L) {
                listOfNotNull(sessionRepository.getLocationById(locationId))
            } else {
                sessionRepository.getAllLocations().first()
            }

            _shelves.value = if (locationId != null && locationId != 0L) {
                sessionRepository.getShelvesForLocation(locationId)
            } else {
                emptyList()
            }
            _sections.value = sessionRepository.getSectionsForShelves(_shelves.value.orEmpty().map { it.id })
        }
    }

    fun onLocationSelected(locationId: Long) {
        viewModelScope.launch {
            _shelves.value = sessionRepository.getShelvesForLocation(locationId)
            _sections.value = emptyList()
        }
    }

    fun onShelfSelected(shelfId: Long) {
        viewModelScope.launch {
            _sections.value = sessionRepository.getSectionsForShelves(listOf(shelfId))
        }
    }

    fun onBarcodeScanned(barcode: String) {
        viewModelScope.launch {
            val found = productRepository.getByBarcode(barcode)
            if (found != null) {
                _product.value = found
                _wrongProduct.value = false
            } else {
                _product.value = null
                _wrongProduct.value = true
            }
        }
    }

    fun activeSessionId(): Long? = sessionManager.activeSessionId()

    fun defaultShelfSectionId(): Long = sections.value?.firstOrNull()?.id ?: 0L

    fun saveCount(
        fileNumber: String?,
        sectionNumber: String?,
        shelfSectionId: Long,
        quantity: Double,
        remarks: String?
    ) {
        viewModelScope.launch {
            val selectedProduct = _product.value
            val sessionId = sessionManager.activeSessionId() ?: activeSession.value?.id ?: 0L
            val userId = secureTokenManager.getUserId()?.toLongOrNull() ?: 0L

            val entity = SecondCountEntity(
                id = 0,
                sessionId = sessionId,
                productId = selectedProduct?.id ?: 0L,
                shelfSectionId = shelfSectionId,
                userId = userId,
                firstCountId = null,
                fileNumber = fileNumber?.takeIf { it.isNotBlank() },
                sectionNumber = sectionNumber?.takeIf { it.isNotBlank() },
                remarks = remarks?.takeIf { it.isNotBlank() },
                quantity = quantity,
                clientId = null,
                deviceId = null,
                source = "mobile",
                countedAt = dateFormat.format(Date()),
                isSynced = false,
                syncedAt = null
            )

            val result = runCatching { secondCountRepository.save(entity) }
            _saveResult.postValue(result)
        }
    }
}
