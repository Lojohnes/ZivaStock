package com.zivastock.ui.butcheryfnv

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.fragment.app.Fragment
import androidx.fragment.app.viewModels
import com.zivastock.databinding.FragmentButcheryFnVBinding
import dagger.hilt.android.AndroidEntryPoint

@AndroidEntryPoint
class ButcheryFnVFragment : Fragment() {

    private var _binding: FragmentButcheryFnVBinding? = null
    private val binding get() = _binding!!
    private val viewModel: ButcheryFnVViewModel by viewModels()

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentButcheryFnVBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        binding.screenTitle.text = getString(com.zivastock.R.string.title_butcheryfnv)
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
