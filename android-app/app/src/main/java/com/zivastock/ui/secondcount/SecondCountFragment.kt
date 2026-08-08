package com.zivastock.ui.secondcount

import android.content.Intent
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ArrayAdapter
import android.widget.Toast
import androidx.activity.result.contract.ActivityResultContracts
import androidx.fragment.app.Fragment
import androidx.fragment.app.viewModels
import com.zivastock.R
import com.zivastock.databinding.FragmentSecondCountBinding
import com.zivastock.presentation.scanner.ScannerActivity
import com.zivastock.sync.SyncScheduler
import dagger.hilt.android.AndroidEntryPoint

@AndroidEntryPoint
class SecondCountFragment : Fragment() {

    private var _binding: FragmentSecondCountBinding? = null
    private val binding get() = _binding!!
    private val viewModel: SecondCountViewModel by viewModels()

    private val barcodeLauncher = registerForActivityResult(ActivityResultContracts.StartActivityForResult()) { result ->
        if (result.resultCode == android.app.Activity.RESULT_OK) {
            val barcode = result.data?.getStringExtra(ScannerActivity.EXTRA_BARCODE)
            if (!barcode.isNullOrBlank()) {
                binding.etBarcode.setText(barcode)
                viewModel.onBarcodeScanned(barcode)
            }
        }
    }

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentSecondCountBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        binding.screenTitle.text = getString(R.string.title_secondcount)

        setupSpinners()
        setupQuantityControls()
        setupBarcodeScan()

        binding.btnSave.setOnClickListener { saveSecondCount() }
        binding.btnCancel.setOnClickListener { clearForm() }

        viewModel.product.observe(viewLifecycleOwner) { product ->
            if (product != null) {
                binding.etProductName.setText(product.description)
                binding.etUnit.setText(product.unitOfMeasure)
                binding.etSystemQuantity.setText(product.systemQuantity.toString())
            }
        }

        viewModel.wrongProduct.observe(viewLifecycleOwner) { isWrong ->
            if (isWrong) {
                binding.etProductName.setText("##WRONG PRODUCT CODE##")
                binding.etUnit.text?.clear()
                binding.etSystemQuantity.text?.clear()
            } else if (viewModel.product.value == null) {
                binding.etProductName.text?.clear()
                binding.etUnit.text?.clear()
                binding.etSystemQuantity.text?.clear()
            }
        }

        viewModel.locations.observe(viewLifecycleOwner) { locations ->
            val adapter = ArrayAdapter(requireContext(), android.R.layout.simple_dropdown_item_1line, locations.map { it.name })
            binding.spinnerLocation.setAdapter(adapter)
        }

        viewModel.shelves.observe(viewLifecycleOwner) { shelves ->
            val adapter = ArrayAdapter(requireContext(), android.R.layout.simple_dropdown_item_1line, shelves.map { it.name })
            binding.spinnerShelf.setAdapter(adapter)
        }

        viewModel.sections.observe(viewLifecycleOwner) { sections ->
            val adapter = ArrayAdapter(requireContext(), android.R.layout.simple_dropdown_item_1line, sections.map { it.name })
            binding.spinnerSection.setAdapter(adapter)
        }

        viewModel.saveResult.observe(viewLifecycleOwner) { result ->
            result.onSuccess {
                Toast.makeText(requireContext(), "Second count saved", Toast.LENGTH_SHORT).show()
                SyncScheduler.triggerImmediateSync(requireContext().applicationContext)
                clearForm()
            }
            result.onFailure { error ->
                Toast.makeText(requireContext(), "Save failed: ${error.message}", Toast.LENGTH_LONG).show()
            }
        }
    }

    private fun setupSpinners() {
        binding.spinnerLocation.setOnItemClickListener { _, _, position, _ ->
            viewModel.locations.value?.getOrNull(position)?.id?.let { locationId ->
                viewModel.onLocationSelected(locationId)
                binding.spinnerShelf.text?.clear()
                binding.spinnerSection.text?.clear()
            }
        }

        binding.spinnerShelf.setOnItemClickListener { _, _, position, _ ->
            viewModel.shelves.value?.getOrNull(position)?.id?.let { shelfId ->
                viewModel.onShelfSelected(shelfId)
                binding.spinnerSection.text?.clear()
            }
        }
    }

    private fun setupQuantityControls() {
        binding.etQuantityLayout.setStartIconOnClickListener {
            adjustQuantity(-1.0)
        }

        binding.etQuantityLayout.setEndIconOnClickListener {
            adjustQuantity(1.0)
        }
    }

    private fun adjustQuantity(delta: Double) {
        val current = binding.etQuantity.text.toString().toDoubleOrNull() ?: 0.0
        binding.etQuantity.setText((current + delta).coerceAtLeast(0.0).toString())
    }

    private fun setupBarcodeScan() {
        binding.etBarcodeLayout.setEndIconOnClickListener {
            barcodeLauncher.launch(Intent(requireContext(), ScannerActivity::class.java))
        }
    }

    private fun saveSecondCount() {
        val sectionId = viewModel.sections.value
            ?.find { it.name == binding.spinnerSection.text.toString() }
            ?.id ?: 0L

        val quantity = binding.etQuantity.text.toString().toDoubleOrNull() ?: 0.0

        viewModel.saveCount(
            fileNumber = binding.spinnerFileNo.text.toString(),
            shelfSectionId = sectionId,
            quantity = quantity,
            remarks = binding.etRemarks.text.toString()
        )
    }

    private fun clearForm() {
        binding.etQuantity.setText("0.00")
        binding.etBarcode.text?.clear()
        binding.etProductName.text?.clear()
        binding.etUnit.text?.clear()
        binding.etSystemQuantity.text?.clear()
        binding.etRemarks.text?.clear()
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
