package com.zivastock.ui.consolidation

import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import com.zivastock.databinding.ItemConsolidationBinding

/**
 * RecyclerView adapter for the consolidation / comparison list.
 */
class ConsolidationAdapter : ListAdapter<ConsolidationItem, ConsolidationAdapter.ConsolidationViewHolder>(DiffCallback()) {

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ConsolidationViewHolder {
        val binding = ItemConsolidationBinding.inflate(
            LayoutInflater.from(parent.context),
            parent,
            false
        )
        return ConsolidationViewHolder(binding)
    }

    override fun onBindViewHolder(holder: ConsolidationViewHolder, position: Int) {
        holder.bind(getItem(position))
    }

    inner class ConsolidationViewHolder(
        private val binding: ItemConsolidationBinding
    ) : RecyclerView.ViewHolder(binding.root) {

        fun bind(item: ConsolidationItem) {
            binding.tvProduct.text = item.product
            binding.tvFirstCount.text = item.firstCount.toString()
            binding.tvSecondCount.text = item.secondCount.toString()
            binding.tvDifference.text = item.difference.toString()
        }
    }

    private class DiffCallback : DiffUtil.ItemCallback<ConsolidationItem>() {
        override fun areItemsTheSame(oldItem: ConsolidationItem, newItem: ConsolidationItem): Boolean {
            return oldItem.product == newItem.product
        }

        override fun areContentsTheSame(oldItem: ConsolidationItem, newItem: ConsolidationItem): Boolean {
            return oldItem == newItem
        }
    }
}

/**
 * UI model for a consolidated count row.
 */
data class ConsolidationItem(
    val product: String,
    val firstCount: Double,
    val secondCount: Double,
    val difference: Double
)
