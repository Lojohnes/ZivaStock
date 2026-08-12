package com.zivastock.ui.products

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.text.InputType
import android.widget.EditText
import android.widget.LinearLayout
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import androidx.core.widget.doAfterTextChanged
import androidx.fragment.app.Fragment
import androidx.fragment.app.viewModels
import com.zivastock.R
import com.zivastock.data.remote.dto.v2.ProductCreateDto
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

        binding.fabAdd.setOnClickListener { showAddProductDialog() }

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

    private fun showAddProductDialog() {
        val container = LinearLayout(requireContext()).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(48, 0, 48, 0)
        }
        fun field(hint: String, type: Int = InputType.TYPE_CLASS_TEXT) = EditText(requireContext()).apply {
            this.hint = hint
            inputType = type
        }
        val barcode = field("Barcode *")
        val productCode = field("Product code")
        val description = field("Description *")
        val uom = field("Unit of measure", InputType.TYPE_CLASS_TEXT).apply { setText("EA") }
        val quantity = field("System quantity", InputType.TYPE_CLASS_NUMBER or InputType.TYPE_NUMBER_FLAG_DECIMAL)
        val cost = field("Unit cost", InputType.TYPE_CLASS_NUMBER or InputType.TYPE_NUMBER_FLAG_DECIMAL)
        listOf(barcode, productCode, description, uom, quantity, cost).forEach(container::addView)

        val dialog = AlertDialog.Builder(requireContext())
            .setTitle("Add product")
            .setView(container)
            .setNegativeButton("Cancel", null)
            .setPositiveButton("Save", null)
            .create()
        dialog.setOnShowListener {
            dialog.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener {
                if (barcode.text.isNullOrBlank() || description.text.isNullOrBlank()) {
                    Toast.makeText(requireContext(), "Barcode and description are required", Toast.LENGTH_SHORT).show()
                    return@setOnClickListener
                }
                dialog.dismiss()
                viewModel.createProduct(ProductCreateDto(
                    barcode = barcode.text.toString().trim(),
                    productCode = productCode.text.toString().trim().ifBlank { null },
                    description = description.text.toString().trim(),
                    unitOfMeasure = uom.text.toString().trim().ifBlank { "EA" },
                    systemQuantity = quantity.text.toString().toDoubleOrNull() ?: 0.0,
                    unitCost = cost.text.toString().toDoubleOrNull() ?: 0.0,
                ))
            }
        }
        dialog.show()
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
