import os
import re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(BASE, "app", "src", "main")
JAVA = os.path.join(SRC, "java", "com", "zivastock")
RES = os.path.join(SRC, "res")


def write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Created {path}")


FEATURES = [
    ("login", "Login", "Login"),
    ("firstcount", "FirstCount", "First Count"),
    ("secondcount", "SecondCount", "Second Count"),
    ("products", "Products", "Products"),
    ("butcheryfnv", "ButcheryFnV", "Butchery FnV"),
    ("consolidation", "Consolidation", "Comparison"),
    ("permissions", "Permissions", "User Permissions"),
    ("sync", "Sync", "Sync Status"),
    ("reports", "Reports", "Reports"),
]

# Package directories
for feat, _, _ in FEATURES:
    os.makedirs(os.path.join(JAVA, "ui", feat), exist_ok=True)

os.makedirs(os.path.join(JAVA, "work"), exist_ok=True)
os.makedirs(os.path.join(RES, "navigation"), exist_ok=True)

# MainActivity
write(
    os.path.join(JAVA, "MainActivity.kt"),
    '''package com.zivastock

import android.os.Bundle
import androidx.activity.viewModels
import androidx.appcompat.app.AppCompatActivity
import androidx.core.view.GravityCompat
import androidx.drawerlayout.widget.DrawerLayout
import androidx.navigation.NavController
import androidx.navigation.fragment.NavHostFragment
import androidx.navigation.ui.AppBarConfiguration
import androidx.navigation.ui.navigateUp
import androidx.navigation.ui.setupActionBarWithNavController
import androidx.navigation.ui.setupWithNavController
import com.google.android.material.bottomnavigation.BottomNavigationView
import com.google.android.material.navigation.NavigationView
import com.zivastock.databinding.ActivityMainBinding
import dagger.hilt.android.AndroidEntryPoint

@AndroidEntryPoint
class MainActivity : AppCompatActivity() {

    private lateinit var binding: ActivityMainBinding
    private val viewModel: MainViewModel by viewModels()

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

        navView.setNavigationItemSelectedListener { item ->
            when (item.itemId) {
                R.id.permissionsFragment -> navController.navigate(R.id.permissionsFragment)
                R.id.reportsFragment -> navController.navigate(R.id.reportsFragment)
                R.id.syncFragment -> navController.navigate(R.id.syncFragment)
                R.id.logout -> viewModel.logout()
            }
            drawerLayout.closeDrawer(GravityCompat.START)
            true
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
}
'''
)

# MainViewModel
write(
    os.path.join(JAVA, "MainViewModel.kt"),
    '''package com.zivastock

import androidx.lifecycle.ViewModel
import com.zivastock.data.local.preferences.SharedPreferencesManager
import dagger.hilt.android.lifecycle.HiltViewModel
import javax.inject.Inject

@HiltViewModel
class MainViewModel @Inject constructor(
    private val prefs: SharedPreferencesManager
) : ViewModel() {

    fun logout() {
        prefs.clear()
        // UI observer should react and navigate to login
    }
}
'''
)

# Fragments and ViewModels
for folder, name, title in FEATURES:
    fragment = f"""package com.zivastock.ui.{folder}

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.fragment.app.Fragment
import androidx.fragment.app.viewModels
import com.zivastock.databinding.Fragment{name}Binding
import dagger.hilt.android.AndroidEntryPoint

@AndroidEntryPoint
class {name}Fragment : Fragment() {{

    private var _binding: Fragment{name}Binding? = null
    private val binding get() = _binding!!
    private val viewModel: {name}ViewModel by viewModels()

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {{
        _binding = Fragment{name}Binding.inflate(inflater, container, false)
        return binding.root
    }}

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {{
        super.onViewCreated(view, savedInstanceState)
        binding.screenTitle.text = "{title}"
    }}

    override fun onDestroyView() {{
        super.onDestroyView()
        _binding = null
    }}
}}
"""
    write(os.path.join(JAVA, "ui", folder, f"{name}Fragment.kt"), fragment)

    viewmodel = f"""package com.zivastock.ui.{folder}

import androidx.lifecycle.ViewModel
import dagger.hilt.android.lifecycle.HiltViewModel
import javax.inject.Inject

@HiltViewModel
class {name}ViewModel @Inject constructor(
) : ViewModel() {{
    // TODO: implement {name} business logic
}}
"""
    write(os.path.join(JAVA, "ui", folder, f"{name}ViewModel.kt"), viewmodel)

# WorkManager worker
write(
    os.path.join(JAVA, "work", "SyncWorker.kt"),
    '''package com.zivastock.work

import android.content.Context
import androidx.hilt.work.HiltWorker
import androidx.work.CoroutineWorker
import androidx.work.WorkerParameters
import com.zivastock.data.repository.SyncRepository
import dagger.assisted.Assisted
import dagger.assisted.AssistedInject

@HiltWorker
class SyncWorker @AssistedInject constructor(
    @Assisted context: Context,
    @Assisted params: WorkerParameters,
    private val syncRepository: SyncRepository
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        return try {
            syncRepository.pushPending()
            syncRepository.pullLatest()
            Result.success()
        } catch (e: Exception) {
            Result.retry()
        }
    }
}
'''
)

# activity_main.xml
write(
    os.path.join(RES, "layout", "activity_main.xml"),
    '''<?xml version="1.0" encoding="utf-8"?>
<androidx.drawerlayout.widget.DrawerLayout
    xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    xmlns:tools="http://schemas.android.com/tools"
    android:id="@+id/drawer_layout"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    tools:openDrawer="start">

    <androidx.coordinatorlayout.widget.CoordinatorLayout
        android:layout_width="match_parent"
        android:layout_height="match_parent">

        <com.google.android.material.appbar.AppBarLayout
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:theme="@style/ThemeOverlay.Material3.Dark.ActionBar">

            <com.google.android.material.appbar.MaterialToolbar
                android:id="@+id/toolbar"
                android:layout_width="match_parent"
                android:layout_height="?attr/actionBarSize"
                android:background="@color/primary"
                app:navigationIcon="@drawable/ic_menu"
                app:title="ZivaStock"
                app:titleTextColor="@color/text_on_primary" />
        </com.google.android.material.appbar.AppBarLayout>

        <androidx.fragment.app.FragmentContainerView
            android:id="@+id/nav_host_fragment"
            android:name="androidx.navigation.fragment.NavHostFragment"
            android:layout_width="match_parent"
            android:layout_height="match_parent"
            android:layout_marginTop="?attr/actionBarSize"
            android:layout_marginBottom="?attr/actionBarSize"
            app:defaultNavHost="true"
            app:navGraph="@navigation/nav_graph" />

        <com.google.android.material.bottomnavigation.BottomNavigationView
            android:id="@+id/bottom_navigation"
            android:layout_width="match_parent"
            android:layout_height="?attr/actionBarSize"
            android:layout_gravity="bottom"
            android:background="@color/primary"
            app:itemIconTint="@color/text_on_primary"
            app:itemTextColor="@color/text_on_primary"
            app:menu="@menu/bottom_nav_menu" />
    </androidx.coordinatorlayout.widget.CoordinatorLayout>

    <com.google.android.material.navigation.NavigationView
        android:id="@+id/nav_view"
        android:layout_width="wrap_content"
        android:layout_height="match_parent"
        android:layout_gravity="start"
        android:background="@color/surface"
        app:headerLayout="@layout/nav_header_main"
        app:menu="@menu/drawer_menu" />
</androidx.drawerlayout.widget.DrawerLayout>
'''
)

# nav_header_main.xml
write(
    os.path.join(RES, "layout", "nav_header_main.xml"),
    '''<?xml version="1.0" encoding="utf-8"?>
<LinearLayout
    xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="120dp"
    android:background="@color/primary"
    android:gravity="bottom|start"
    android:orientation="vertical"
    android:padding="16dp">

    <TextView
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="ZivaStock"
        android:textColor="@color/text_on_primary"
        android:textSize="24sp"
        android:textStyle="bold" />
</LinearLayout>
'''
)

# Fragment placeholder layouts
for folder, name, title in FEATURES:
    if folder == "firstcount":
        layout = '''<?xml version="1.0" encoding="utf-8"?>
<ScrollView
    xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:fillViewport="true">

    <LinearLayout
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:orientation="vertical"
        android:padding="16dp">

        <TextView
            android:id="@+id/screenTitle"
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:textSize="20sp"
            android:textStyle="bold"
            android:textColor="@color/text_primary"
            android:layout_marginBottom="16dp" />

        <com.google.android.material.textfield.TextInputLayout
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:hint="File No"
            style="@style/Widget.Material3.TextInputLayout.OutlinedBox.ExposedDropdownMenu">

            <com.google.android.material.textfield.MaterialAutoCompleteTextView
                android:id="@+id/spinnerFileNo"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:inputType="none" />
        </com.google.android.material.textfield.TextInputLayout>

        <com.google.android.material.textfield.TextInputLayout
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:layout_marginTop="12dp"
            android:hint="Location *"
            style="@style/Widget.Material3.TextInputLayout.OutlinedBox.ExposedDropdownMenu">

            <com.google.android.material.textfield.MaterialAutoCompleteTextView
                android:id="@+id/spinnerLocation"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:inputType="none" />
        </com.google.android.material.textfield.TextInputLayout>

        <com.google.android.material.textfield.TextInputLayout
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:layout_marginTop="12dp"
            android:hint="Barcode *"
            app:endIconDrawable="@drawable/ic_qr_code"
            app:endIconMode="custom"
            style="@style/Widget.Material3.TextInputLayout.OutlinedBox">

            <com.google.android.material.textfield.TextInputEditText
                android:id="@+id/etBarcode"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:inputType="text" />
        </com.google.android.material.textfield.TextInputLayout>

        <com.google.android.material.textfield.TextInputLayout
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:layout_marginTop="12dp"
            android:hint="ProductName *"
            app:helperText="##WRONG PRODUCT CODE##"
            style="@style/Widget.Material3.TextInputLayout.OutlinedBox">

            <com.google.android.material.textfield.TextInputEditText
                android:id="@+id/etProductName"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:enabled="false"
                android:inputType="text" />
        </com.google.android.material.textfield.TextInputLayout>

        <com.google.android.material.textfield.TextInputLayout
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:layout_marginTop="12dp"
            android:hint="FirstCountQty *"
            style="@style/Widget.Material3.TextInputLayout.OutlinedBox">

            <com.google.android.material.textfield.TextInputEditText
                android:id="@+id/etQuantity"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:inputType="numberDecimal"
                android:text="0.00" />
        </com.google.android.material.textfield.TextInputLayout>

        <LinearLayout
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:layout_marginTop="24dp"
            android:orientation="horizontal">

            <com.google.android.material.button.MaterialButton
                android:id="@+id/btnCancel"
                android:layout_width="0dp"
                android:layout_height="wrap_content"
                android:layout_weight="1"
                android:layout_marginEnd="8dp"
                android:backgroundTint="@color/text_secondary"
                android:text="Cancel" />

            <com.google.android.material.button.MaterialButton
                android:id="@+id/btnSave"
                android:layout_width="0dp"
                android:layout_height="wrap_content"
                android:layout_weight="1"
                android:layout_marginStart="8dp"
                android:text="Save" />
        </LinearLayout>
    </LinearLayout>
</ScrollView>
'''
    elif folder == "secondcount":
        layout = '''<?xml version="1.0" encoding="utf-8"?>
<ScrollView
    xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:fillViewport="true">

    <LinearLayout
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:orientation="vertical"
        android:padding="16dp">

        <TextView
            android:id="@+id/screenTitle"
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:textSize="20sp"
            android:textStyle="bold"
            android:textColor="@color/text_primary"
            android:layout_marginBottom="16dp" />

        <com.google.android.material.textfield.TextInputLayout
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:hint="File No"
            style="@style/Widget.Material3.TextInputLayout.OutlinedBox.ExposedDropdownMenu">

            <com.google.android.material.textfield.MaterialAutoCompleteTextView
                android:id="@+id/spinnerFileNo"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:inputType="none" />
        </com.google.android.material.textfield.TextInputLayout>

        <com.google.android.material.textfield.TextInputLayout
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:layout_marginTop="12dp"
            android:hint="Location *"
            style="@style/Widget.Material3.TextInputLayout.OutlinedBox.ExposedDropdownMenu">

            <com.google.android.material.textfield.MaterialAutoCompleteTextView
                android:id="@+id/spinnerLocation"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:inputType="none" />
        </com.google.android.material.textfield.TextInputLayout>

        <com.google.android.material.textfield.TextInputLayout
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:layout_marginTop="12dp"
            android:hint="Barcode *"
            app:endIconDrawable="@drawable/ic_qr_code"
            app:endIconMode="custom"
            style="@style/Widget.Material3.TextInputLayout.OutlinedBox">

            <com.google.android.material.textfield.TextInputEditText
                android:id="@+id/etBarcode"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:inputType="text" />
        </com.google.android.material.textfield.TextInputLayout>

        <com.google.android.material.textfield.TextInputLayout
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:layout_marginTop="12dp"
            android:hint="ProductName *"
            style="@style/Widget.Material3.TextInputLayout.OutlinedBox">

            <com.google.android.material.textfield.TextInputEditText
                android:id="@+id/etProductName"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:enabled="false"
                android:inputType="text" />
        </com.google.android.material.textfield.TextInputLayout>

        <com.google.android.material.textfield.TextInputLayout
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:layout_marginTop="12dp"
            android:hint="SecondCountQty *"
            style="@style/Widget.Material3.TextInputLayout.OutlinedBox">

            <com.google.android.material.textfield.TextInputEditText
                android:id="@+id/etQuantity"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:inputType="numberDecimal"
                android:text="0.00" />
        </com.google.android.material.textfield.TextInputLayout>

        <LinearLayout
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:layout_marginTop="24dp"
            android:orientation="horizontal">

            <com.google.android.material.button.MaterialButton
                android:id="@+id/btnCancel"
                android:layout_width="0dp"
                android:layout_height="wrap_content"
                android:layout_weight="1"
                android:layout_marginEnd="8dp"
                android:backgroundTint="@color/text_secondary"
                android:text="Cancel" />

            <com.google.android.material.button.MaterialButton
                android:id="@+id/btnSave"
                android:layout_width="0dp"
                android:layout_height="wrap_content"
                android:layout_weight="1"
                android:layout_marginStart="8dp"
                android:text="Save" />
        </LinearLayout>
    </LinearLayout>
</ScrollView>
'''
    else:
        layout = f'''<?xml version="1.0" encoding="utf-8"?>
<LinearLayout
    xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical"
    android:padding="16dp">

    <TextView
        android:id="@+id/screenTitle"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:textSize="20sp"
        android:textStyle="bold"
        android:textColor="@color/text_primary" />

    <androidx.recyclerview.widget.RecyclerView
        android:id="@+id/recyclerView"
        android:layout_width="match_parent"
        android:layout_height="0dp"
        android:layout_weight="1"
        android:layout_marginTop="8dp" />

    <com.google.android.material.floatingactionbutton.FloatingActionButton
        android:id="@+id/fabAdd"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_gravity="end"
        android:layout_margin="16dp"
        android:contentDescription="Add" />
</LinearLayout>
'''
    write(os.path.join(RES, "layout", f"fragment_{folder}.xml"), layout)

# nav_graph.xml
destinations = "\n".join(
    f'    <fragment\n        android:id="@+id/{folder}Fragment"\n        android:name="com.zivastock.ui.{folder}.{name}Fragment"\n        android:label="{title}"\n        tools:layout="@layout/fragment_{folder}" />'
    for folder, name, title in FEATURES
)
nav_graph = f'''<?xml version="1.0" encoding="utf-8"?>
<navigation
    xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    xmlns:tools="http://schemas.android.com/tools"
    android:id="@+id/nav_graph"
    app:startDestination="@id/loginFragment">

    <action
        android:id="@+id/action_global_login"
        app:destination="@id/loginFragment"
        app:popUpTo="@id/nav_graph"
        app:popUpToInclusive="true" />

{destinations}
</navigation>
'''
write(os.path.join(RES, "navigation", "nav_graph.xml"), nav_graph)

# Menus
write(
    os.path.join(RES, "menu", "bottom_nav_menu.xml"),
    '''<?xml version="1.0" encoding="utf-8"?>
<menu xmlns:android="http://schemas.android.com/apk/res/android">
    <item
        android:id="@+id/firstCountFragment"
        android:icon="@drawable/ic_first_count"
        android:title="FirstCount" />
    <item
        android:id="@+id/productsFragment"
        android:icon="@drawable/ic_products"
        android:title="Products" />
    <item
        android:id="@+id/secondCountFragment"
        android:icon="@drawable/ic_second_count"
        android:title="SecondCount" />
    <item
        android:id="@+id/butcheryFnVFragment"
        android:icon="@drawable/ic_butchery"
        android:title="ButcheryFnV" />
</menu>
'''
)

write(
    os.path.join(RES, "menu", "drawer_menu.xml"),
    '''<?xml version="1.0" encoding="utf-8"?>
<menu xmlns:android="http://schemas.android.com/apk/res/android">
    <group android:checkableBehavior="single">
        <item
            android:id="@+id/permissionsFragment"
            android:icon="@android:drawable/ic_menu_manage"
            android:title="User Permissions" />
        <item
            android:id="@+id/reportsFragment"
            android:icon="@android:drawable/ic_menu_report_image"
            android:title="Reports" />
        <item
            android:id="@+id/syncFragment"
            android:icon="@android:drawable/ic_menu_rotate"
            android:title="Sync Status" />
    </group>
    <item
        android:id="@+id/logout"
        android:icon="@android:drawable/ic_lock_power_off"
        android:title="Logout" />
</menu>
'''
)

# Drawables
write(
    os.path.join(RES, "drawable", "ic_menu.xml"),
    '''<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="24dp"
    android:height="24dp"
    android:viewportWidth="24"
    android:viewportHeight="24">
    <path
        android:fillColor="#FFFFFF"
        android:pathData="M3,6h18v2H3V6zM3,11h18v2H3V11zM3,16h18v2H3V16z" />
</vector>
'''
)

write(
    os.path.join(RES, "drawable", "ic_qr_code.xml"),
    '''<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="24dp"
    android:height="24dp"
    android:viewportWidth="24"
    android:viewportHeight="24">
    <path
        android:fillColor="#757575"
        android:pathData="M3,11h8V3H3V11zM5,5h4v4H5V5zM3,21h8v-8H3V21zM5,15h4v4H5V15zM13,3v8h8V3H13zM19,9h-4V5h4V9zM13,13h2v2h-2V13zM15,15h2v2h-2V15zM13,17h2v2h-2V17zM17,13h2v2h-2V13zM19,15h2v2h-2V15zM17,17h2v2h-2V17zM15,19h2v2h-2V19zM19,19h2v2h-2V19z" />
</vector>
'''
)

for icon, path_data in [
    ("ic_first_count", "M12,2C6.48,2 2,6.48 2,12s4.48,10 10,10 10,-4.48 10,-10S17.52,2 12,2zM12,20c-4.41,0 -8,-3.59 -8,-8s3.59,-8 8,-8 8,3.59 8,8 -3.59,8 -8,8z"),
    ("ic_second_count", "M9,16.17L4.83,12l-1.42,1.41L9,19 21,7l-1.41,-1.41z"),
    ("ic_products", "M12,2l-5.5,9h11z M17.5,9L12,22l5.5,-9H17.5z"),
    ("ic_butchery", "M12,2C6.48,2 2,6.48 2,12s4.48,10 10,10 10,-4.48 10,-10S17.52,2 12,2z"),
]:
    write(
        os.path.join(RES, "drawable", f"{icon}.xml"),
        f'''<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="24dp"
    android:height="24dp"
    android:viewportWidth="24"
    android:viewportHeight="24">
    <path
        android:fillColor="#FFFFFF"
        android:pathData="{path_data}" />
</vector>
'''
    )

# strings.xml – generate a merged file by reading existing and appending
strings_path = os.path.join(RES, "values", "strings.xml")
existing = ""
if os.path.exists(strings_path):
    with open(strings_path, "r", encoding="utf-8") as f:
        existing = f.read()

# New feature strings
new_strings = "\n".join(
    f'    <string name="title_{folder}">{title}</string>'
    for folder, name, title in FEATURES
)
new_strings += '''\n    <string name="app_name">ZivaStock</string>
    <string name="login">Login</string>
    <string name="logout">Logout</string>
    <string name="save">Save</string>
    <string name="cancel">Cancel</string>
    <string name="search">Search</string>
    <string name="refresh">Refresh</string>
'''

if existing and existing.strip().endswith("</resources>"):
    existing = re.sub(r"\s*</resources>\s*$", "", existing)
    merged = f"{existing}\n{new_strings}\n</resources>\n"
else:
    merged = f'''<?xml version="1.0" encoding="utf-8"?>
<resources>
{new_strings}
</resources>
'''

with open(strings_path, "w", encoding="utf-8") as f:
    f.write(merged)
print(f"Updated {strings_path}")

print("\nAndroid project structure generated.")
