package com.zivastock.ui.products

import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import com.zivastock.databinding.ItemProductBinding

/**
 * RecyclerView adapter for the products list.
 */
class ProductsAdapter : ListAdapter<ProductItem, ProductsAdapter.ProductViewHolder>(DiffCallback()) {

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ProductViewHolder {
        val binding = ItemProductBinding.inflate(
            LayoutInflater.from(parent.context),
            parent,
            false
        )
        return ProductViewHolder(binding)
    }

    override fun onBindViewHolder(holder: ProductViewHolder, position: Int) {
        holder.bind(getItem(position))
    }

    inner class ProductViewHolder(
        private val binding: ItemProductBinding
    ) : RecyclerView.ViewHolder(binding.root) {

        fun bind(item: ProductItem) {
            binding.tvDescription.text = item.description
            binding.tvCode.text = "Barcode: ${item.barcode}  •  Product code: ${item.productCode ?: "-"}"
            binding.tvQty.text = "System qty: ${item.qtyOnHand}"
            binding.tvUom.text = "UOM: ${item.unitOfMeasure}"
            binding.tvCost.text = "Unit cost: ${item.unitCost}"
        }
    }

    private class DiffCallback : DiffUtil.ItemCallback<ProductItem>() {
        override fun areItemsTheSame(oldItem: ProductItem, newItem: ProductItem): Boolean {
            return oldItem.code == newItem.code
        }

        override fun areContentsTheSame(oldItem: ProductItem, newItem: ProductItem): Boolean {
            return oldItem == newItem
        }
    }
}

/**
 * UI model for a product row.
 */
data class ProductItem(
    val code: String,
    val barcode: String,
    val productCode: String?,
    val description: String,
    val unitOfMeasure: String,
    val qtyOnHand: Double,
    val unitCost: Double,
)
