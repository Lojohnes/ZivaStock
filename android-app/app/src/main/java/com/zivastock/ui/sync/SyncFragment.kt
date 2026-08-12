package com.zivastock.ui.sync

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.fragment.app.Fragment
import androidx.fragment.app.viewModels
import com.zivastock.databinding.FragmentSyncBinding
import dagger.hilt.android.AndroidEntryPoint

@AndroidEntryPoint
class SyncFragment : Fragment() {

    private var _binding: FragmentSyncBinding? = null
    private val binding get() = _binding!!
    private val viewModel: SyncViewModel by viewModels()

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentSyncBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        binding.screenTitle.text = getString(com.zivastock.R.string.title_sync)
        binding.btnSyncNow.setOnClickListener { viewModel.sync() }
        viewModel.state.observe(viewLifecycleOwner) { state ->
            binding.btnSyncNow.isEnabled = state !is SyncViewModel.SyncState.Loading
            binding.tvSyncStatus.text = when (state) {
                is SyncViewModel.SyncState.Loading -> "Synchronizing products and counts..."
                is SyncViewModel.SyncState.Success -> state.message
                is SyncViewModel.SyncState.Error -> "Sync failed: ${state.message}"
                SyncViewModel.SyncState.Idle -> "Ready to synchronize"
            }
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
