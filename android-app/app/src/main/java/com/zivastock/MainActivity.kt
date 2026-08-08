package com.zivastock

import android.os.Bundle
import androidx.activity.viewModels
import androidx.appcompat.app.AppCompatActivity
import androidx.core.view.GravityCompat
import androidx.core.view.forEach
import androidx.drawerlayout.widget.DrawerLayout
import androidx.lifecycle.lifecycleScope
import androidx.navigation.NavController
import androidx.navigation.fragment.NavHostFragment
import androidx.navigation.ui.AppBarConfiguration
import androidx.navigation.ui.navigateUp
import androidx.navigation.ui.setupActionBarWithNavController
import androidx.navigation.ui.setupWithNavController
import android.view.View
import com.google.android.material.bottomnavigation.BottomNavigationView
import com.google.android.material.navigation.NavigationView
import com.zivastock.data.rbac.PermissionManager
import com.zivastock.databinding.ActivityMainBinding
import dagger.hilt.android.AndroidEntryPoint
import kotlinx.coroutines.launch
import javax.inject.Inject

@AndroidEntryPoint
class MainActivity : AppCompatActivity() {

    private lateinit var binding: ActivityMainBinding
    private val viewModel: MainViewModel by viewModels()

    @Inject
    lateinit var permissionManager: PermissionManager

    private lateinit var navController: NavController
    private lateinit var appBarConfiguration: AppBarConfiguration
    private lateinit var drawerLayout: DrawerLayout

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        drawerLayout = binding.drawerLayout

        val toolbar = binding.toolbar
        setSupportActionBar(toolbar)

        val navHostFragment = supportFragmentManager
            .findFragmentById(R.id.nav_host_fragment) as NavHostFragment
        navController = navHostFragment.navController

        appBarConfiguration = AppBarConfiguration(
            setOf(
                R.id.dashboardFragment,
                R.id.firstCountFragment,
                R.id.productsFragment,
                R.id.secondCountFragment,
                R.id.butcheryFnVFragment
            ),
            drawerLayout
        )

        setupActionBarWithNavController(navController, appBarConfiguration)

        val bottomNav: BottomNavigationView = binding.bottomNavigation
        bottomNav.setupWithNavController(navController)

        val navView: NavigationView = binding.navView
        navView.setupWithNavController(navController)

        navController.addOnDestinationChangedListener { _, destination, _ ->
            when (destination.id) {
                R.id.loginFragment -> bottomNav.visibility = View.GONE
                else -> bottomNav.visibility = View.VISIBLE
            }
            lifecycleScope.launch {
                applyRoleBasedAccess()
            }
        }

        lifecycleScope.launch {
            permissionManager.ensureDefaults()
            applyRoleBasedAccess()
        }

        navView.setNavigationItemSelectedListener { item ->
            when (item.itemId) {
                R.id.dashboardFragment -> navController.navigate(R.id.dashboardFragment)
                R.id.permissionsFragment -> navController.navigate(R.id.permissionsFragment)
                R.id.reportsFragment -> navController.navigate(R.id.reportsFragment)
                R.id.syncFragment -> navController.navigate(R.id.syncFragment)
                R.id.logout -> viewModel.logout()
            }
            drawerLayout.closeDrawer(GravityCompat.START)
            true
        }

        viewModel.logoutEvent.observe(this) { shouldLogout ->
            if (shouldLogout) {
                viewModel.onLogoutHandled()
                navController.popBackStack(R.id.nav_graph, true)
                navController.navigate(R.id.action_global_login)
            }
        }
    }

    override fun onSupportNavigateUp(): Boolean {
        return navController.navigateUp(appBarConfiguration) || super.onSupportNavigateUp()
    }

    override fun onBackPressed() {
        if (drawerLayout.isDrawerOpen(GravityCompat.START)) {
            drawerLayout.closeDrawer(GravityCompat.START)
        } else {
            super.onBackPressed()
        }
    }

    private suspend fun applyRoleBasedAccess() {
        val allowed = permissionManager.getAllowedMenuIds()

        val bottomNav: BottomNavigationView = binding.bottomNavigation
        bottomNav.menu.forEach { item ->
            item.isVisible = allowed.contains(item.itemId)
        }

        val currentId = bottomNav.selectedItemId
        if (currentId != 0 && !allowed.contains(currentId)) {
            val firstAllowed = allowed.firstOrNull()
            if (firstAllowed != null) {
                bottomNav.selectedItemId = firstAllowed
            }
        }

        val navView: NavigationView = binding.navView
        navView.menu.forEach { item ->
            if (item.itemId == R.id.logout) return@forEach
            item.isVisible = allowed.contains(item.itemId)
        }
    }
}
