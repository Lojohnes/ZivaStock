package com.zivastock.ui.products

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Toast
import androidx.core.widget.doAfterTextChanged
import androidx.fragment.app.Fragment
import androidx.fragment.app.viewModels
import com.zivastock.R
import com.zivastock.databinding.FragmentProductsBinding
import dagger.hilt.android.AndroidEntryPoint

@AndroidEntryPoint
class ProductsFragment : Fragment() {

    private var _binding: FragmentProductsBinding? = null
    private val binding get() = _binding!!
    private val viewModel: ProductsViewModel by viewModels()
    private val adapter by lazy { ProductsAdapter() }

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentProductsBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        binding.screenTitle.text = getString(R.string.title_products)
        binding.recyclerView.adapter = adapter

        binding.etSearch.doAfterTextChanged { text ->
            viewModel.setSearchQuery(text?.toString().orEmpty())
        }

        binding.fabAdd.setOnClickListener {
            Toast.makeText(requireContext(), "Add product flow TBD", Toast.LENGTH_SHORT).show()
        }

        viewModel.products.observe(viewLifecycleOwner) { entities ->
            adapter.submitList(entities.map { it.toProductItem() })
        }

        viewModel.syncState.observe(viewLifecycleOwner) { state ->
            when (state) {
                is ProductsViewModel.SyncState.Loading -> binding.progressBar.visibility = View.VISIBLE
                is ProductsViewModel.SyncState.Success -> {
                    binding.progressBar.visibility = View.GONE
                    viewModel.onSyncHandled()
                }
                is ProductsViewModel.SyncState.Error -> {
                    binding.progressBar.visibility = View.GONE
                    viewModel.onSyncHandled()
                }
                else -> binding.progressBar.visibility = View.GONE
            }
        }
    }

    private fun com.zivastock.data.local.database.v2.entities.ProductEntity.toProductItem(): ProductItem {
        return ProductItem(
            code = productCode ?: barcode,
            barcode = barcode,
            productCode = productCode,
            description = description,
            unitOfMeasure = unitOfMeasure,
            qtyOnHand = systemQuantity,
            unitCost = unitCost
        )
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
