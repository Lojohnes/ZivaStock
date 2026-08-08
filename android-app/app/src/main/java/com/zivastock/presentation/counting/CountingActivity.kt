package com.zivastock.presentation.counting

import android.content.Intent
import android.os.Bundle
import android.view.Menu
import android.view.MenuItem
import android.widget.Toast
import androidx.activity.result.contract.ActivityResultContracts
import androidx.activity.viewModels
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import androidx.recyclerview.widget.LinearLayoutManager
import com.zivastock.R
import com.zivastock.databinding.ActivityCountingBinding
import com.zivastock.presentation.login.LoginActivity
import com.zivastock.presentation.scanner.ScannerActivity
import com.zivastock.presentation.sync.SyncStatusActivity
import dagger.hilt.android.AndroidEntryPoint
import kotlinx.coroutines.launch

@AndroidEntryPoint
class CountingActivity : AppCompatActivity() {

    private lateinit var binding: ActivityCountingBinding
    private val viewModel: CountingViewModel by viewModels()
    private lateinit var countsAdapter: CountsAdapter

    private val scannerLauncher = registerForActivityResult(
        ActivityResultContracts.StartActivityForResult()
    ) { result ->
        if (result.resultCode == RESULT_OK) {
            val barcode = result.data?.getStringExtra(ScannerActivity.EXTRA_BARCODE) ?: return@registerForActivityResult
            viewModel.onBarcodeScanned(barcode)
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityCountingBinding.inflate(layoutInflater)
        setContentView(binding.root)

        setSupportActionBar(binding.toolbar)

        countsAdapter = CountsAdapter(emptyList())
        binding.recyclerCounts.apply {
            layoutManager = LinearLayoutManager(this@CountingActivity)
            adapter = countsAdapter
        }

        binding.fabScan.setOnClickListener {
            scannerLauncher.launch(Intent(this, ScannerActivity::class.java))
        }

        binding.btnSaveCount.setOnClickListener {
            val product = viewModel.scannedProduct.value
            val quantity = binding.etQuantity.text.toString().toDoubleOrNull()
            if (product == null) {
                Toast.makeText(this, "Scan a product first", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }
            if (quantity == null) {
                Toast.makeText(this, "Enter a valid quantity", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }
            viewModel.saveCount(product.id, quantity)
        }

        viewModel.scannedProduct.observe(this) { product ->
            if (product != null) {
                binding.tvProductInfo.text = "${product.barcode}\n${product.description}"
                binding.tvProductInfo.visibility = android.view.View.VISIBLE
            } else {
                binding.tvProductInfo.visibility = android.view.View.GONE
            }
        }

        viewModel.saveState.observe(this) { state ->
            when (state) {
                is CountingViewModel.SaveState.Success -> {
                    binding.etQuantity.setText("")
                    binding.tvProductInfo.visibility = android.view.View.GONE
                    Toast.makeText(this, "Count saved", Toast.LENGTH_SHORT).show()
                }
                is CountingViewModel.SaveState.Error -> {
                    Toast.makeText(this, state.message, Toast.LENGTH_LONG).show()
                }
                else -> {}
            }
        }

        viewModel.counts.observe(this) { counts ->
            countsAdapter.updateCounts(counts)
        }

        viewModel.userName.observe(this) { name ->
            supportActionBar?.subtitle = "Hello, $name"
        }

        // Default session and section for demo
        viewModel.setLocation(sessionId = 1, sectionId = 1)
    }

    override fun onCreateOptionsMenu(menu: Menu?): Boolean {
        menuInflater.inflate(R.menu.menu_counting, menu)
        return true
    }

    override fun onOptionsItemSelected(item: MenuItem): Boolean {
        return when (item.itemId) {
            R.id.action_sync -> {
                startActivity(Intent(this, SyncStatusActivity::class.java))
                true
            }
            R.id.action_logout -> {
                AlertDialog.Builder(this)
                    .setTitle("Logout")
                    .setMessage("Are you sure you want to logout?")
                    .setPositiveButton("Logout") { _, _ ->
                        lifecycleScope.launch {
                            viewModel.logout()
                            startActivity(Intent(this@CountingActivity, LoginActivity::class.java))
                            finish()
                        }
                    }
                    .setNegativeButton("Cancel", null)
                    .show()
                true
            }
            else -> super.onOptionsItemSelected(item)
        }
    }
}
