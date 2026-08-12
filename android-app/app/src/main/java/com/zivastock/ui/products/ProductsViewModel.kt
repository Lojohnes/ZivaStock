package com.zivastock.ui.products

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.asLiveData
import androidx.lifecycle.switchMap
import androidx.lifecycle.viewModelScope
import com.zivastock.data.local.database.v2.entities.ProductEntity
import com.zivastock.data.repository.v2.ProductRepository
import com.zivastock.data.remote.dto.v2.ProductCreateDto
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class ProductsViewModel @Inject constructor(
    private val repository: ProductRepository
) : ViewModel() {

    private val _searchQuery = MutableLiveData("")

    val products: LiveData<List<ProductEntity>> = _searchQuery.switchMap { query ->
        repository.search(query).asLiveData()
    }

    private val _syncState = MutableLiveData<SyncState>(SyncState.Idle)
    val syncState: LiveData<SyncState> = _syncState

    init {
        sync()
    }

    fun setSearchQuery(query: String) {
        _searchQuery.value = query
    }

    fun createProduct(product: ProductCreateDto) {
        viewModelScope.launch {
            _syncState.value = SyncState.Loading
            val result = repository.createProduct(product)
            _syncState.value = result.fold(
                onSuccess = { SyncState.Success(1) },
                onFailure = { SyncState.Error(it.message ?: "Product creation failed") }
            )
        }
    }

    fun sync() {
        viewModelScope.launch {
            _syncState.value = SyncState.Loading
            val result = repository.fetchFromServer()
            _syncState.value = result.fold(
                onSuccess = { SyncState.Success(it) },
                onFailure = { SyncState.Error(it.message ?: "Sync failed") }
            )
        }
    }

    fun onSyncHandled() {
        _syncState.value = SyncState.Idle
    }

    sealed class SyncState {
        object Idle : SyncState()
        object Loading : SyncState()
        data class Success(val count: Int) : SyncState()
        data class Error(val message: String) : SyncState()
    }
}
