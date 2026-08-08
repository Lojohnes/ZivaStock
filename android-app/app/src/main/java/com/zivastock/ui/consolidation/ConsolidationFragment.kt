package com.zivastock.ui.consolidation

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.fragment.app.Fragment
import androidx.fragment.app.viewModels
import com.zivastock.R
import com.zivastock.databinding.FragmentConsolidationBinding
import dagger.hilt.android.AndroidEntryPoint

@AndroidEntryPoint
class ConsolidationFragment : Fragment() {

    private var _binding: FragmentConsolidationBinding? = null
    private val binding get() = _binding!!
    private val viewModel: ConsolidationViewModel by viewModels()
    private val adapter by lazy { ConsolidationAdapter() }

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentConsolidationBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        binding.screenTitle.text = getString(R.string.title_consolidation)
        binding.recyclerView.adapter = adapter

        // TODO: load from ViewModel / repository once count data is wired
        adapter.submitList(
            listOf(
                ConsolidationItem("Bananas 1kg", 12.0, 12.0, 0.0),
                ConsolidationItem("Apples 1kg", 8.0, 7.0, -1.0),
                ConsolidationItem("Carrots 500g", 15.0, 15.0, 0.0),
                ConsolidationItem("Beef Steak 1kg", 6.0, 5.0, -1.0)
            )
        )
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
