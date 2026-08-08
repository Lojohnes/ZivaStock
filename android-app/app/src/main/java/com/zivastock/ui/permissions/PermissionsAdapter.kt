package com.zivastock.ui.permissions

import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import com.zivastock.databinding.ItemPermissionBinding

/**
 * RecyclerView adapter for the user permissions / roles list.
 */
class PermissionsAdapter : ListAdapter<PermissionItem, PermissionsAdapter.PermissionViewHolder>(DiffCallback()) {

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): PermissionViewHolder {
        val binding = ItemPermissionBinding.inflate(
            LayoutInflater.from(parent.context),
            parent,
            false
        )
        return PermissionViewHolder(binding)
    }

    override fun onBindViewHolder(holder: PermissionViewHolder, position: Int) {
        holder.bind(getItem(position))
    }

    inner class PermissionViewHolder(
        private val binding: ItemPermissionBinding
    ) : RecyclerView.ViewHolder(binding.root) {

        fun bind(item: PermissionItem) {
            binding.tvRoleName.text = item.roleName
            binding.tvRoleDescription.text = item.description
        }
    }

    private class DiffCallback : DiffUtil.ItemCallback<PermissionItem>() {
        override fun areItemsTheSame(oldItem: PermissionItem, newItem: PermissionItem): Boolean {
            return oldItem.roleName == newItem.roleName
        }

        override fun areContentsTheSame(oldItem: PermissionItem, newItem: PermissionItem): Boolean {
            return oldItem == newItem
        }
    }
}

/**
 * UI model for a role/permission row.
 */
data class PermissionItem(
    val roleName: String,
    val description: String
)
