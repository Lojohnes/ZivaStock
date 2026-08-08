package com.zivastock.presentation.counting

import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.recyclerview.widget.RecyclerView
import com.zivastock.data.local.database.entities.CountEntity
import com.zivastock.databinding.ItemCountBinding

class CountsAdapter(private var counts: List<CountEntity>) :
    RecyclerView.Adapter<CountsAdapter.CountViewHolder>() {

    inner class CountViewHolder(private val binding: ItemCountBinding) :
        RecyclerView.ViewHolder(binding.root) {
        fun bind(count: CountEntity) {
            binding.tvProductId.text = "Product #${count.productId}"
            binding.tvQuantity.text = "Qty: ${count.quantity}"
            binding.tvSyncStatus.text = if (count.isSynced) "Synced" else "Pending"
        }
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): CountViewHolder {
        val binding = ItemCountBinding.inflate(LayoutInflater.from(parent.context), parent, false)
        return CountViewHolder(binding)
    }

    override fun onBindViewHolder(holder: CountViewHolder, position: Int) {
        holder.bind(counts[position])
    }

    override fun getItemCount(): Int = counts.size

    fun updateCounts(newCounts: List<CountEntity>) {
        counts = newCounts
        notifyDataSetChanged()
    }
}
