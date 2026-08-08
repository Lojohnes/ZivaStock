package com.zivastock.presentation.sync

import android.os.Bundle
import android.widget.Toast
import androidx.activity.viewModels
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.lifecycleScope
import androidx.lifecycle.repeatOnLifecycle
import com.zivastock.databinding.ActivitySyncStatusBinding
import com.zivastock.sync.SyncScheduler
import dagger.hilt.android.AndroidEntryPoint
import kotlinx.coroutines.launch

@AndroidEntryPoint
class SyncStatusActivity : AppCompatActivity() {

    private lateinit var binding: ActivitySyncStatusBinding
    private val viewModel: SyncStatusViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivitySyncStatusBinding.inflate(layoutInflater)
        setContentView(binding.root)

        setSupportActionBar(binding.toolbar)
        supportActionBar?.setDisplayHomeAsUpEnabled(true)

        binding.btnSyncNow.setOnClickListener {
            SyncScheduler.triggerImmediateSync(this)
            Toast.makeText(this, "Sync requested", Toast.LENGTH_SHORT).show()
        }

        lifecycleScope.launch {
            repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.syncStatus.collect { status ->
                    binding.tvPendingCounts.text = "Pending counts: ${status.pendingCounts}"
                    binding.tvLastSync.text = "Last sync: ${status.lastSync ?: "Never"}"
                    binding.tvIsOnline.text = "Online: ${status.isOnline}"
                }
            }
        }

        viewModel.refreshStatus()
    }

    override fun onSupportNavigateUp(): Boolean {
        finish()
        return true
    }
}
