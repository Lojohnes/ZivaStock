package com.zivastock.ui.login

import android.os.Bundle
import android.text.InputType
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.EditText
import android.widget.LinearLayout
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import androidx.fragment.app.Fragment
import androidx.fragment.app.viewModels
import androidx.navigation.fragment.findNavController
import com.zivastock.R
import com.zivastock.databinding.FragmentLoginBinding
import dagger.hilt.android.AndroidEntryPoint

@AndroidEntryPoint
class LoginFragment : Fragment() {

    private var _binding: FragmentLoginBinding? = null
    private val binding get() = _binding!!
    private val viewModel: LoginViewModel by viewModels()

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentLoginBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        binding.btnLogin.setOnClickListener {
            val email = binding.etEmail.text.toString().trim()
            val password = binding.etPassword.text.toString()
            viewModel.login(email, password)
        }

        binding.tvRegister.setOnClickListener {
            showRegistrationDialog()
        }

        viewModel.loginState.observe(viewLifecycleOwner) { state ->
            when (state) {
                is LoginViewModel.LoginState.Loading -> showLoading()
                is LoginViewModel.LoginState.AlreadyLoggedIn -> navigateToFirstCount()
                is LoginViewModel.LoginState.Success -> {
                    hideLoading()
                    if (state.isOffline) {
                        Toast.makeText(requireContext(), R.string.offline_login_success, Toast.LENGTH_SHORT).show()
                    }
                    navigateToFirstCount()
                }
                is LoginViewModel.LoginState.Error -> {
                    hideLoading()
                    binding.tvError.text = state.message
                    binding.tvError.visibility = View.VISIBLE
                }
                else -> hideLoading()
            }
        }
    }

    private fun showRegistrationDialog() {
        val container = LinearLayout(requireContext()).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(48, 0, 48, 0)
        }
        val firstName = EditText(requireContext()).apply { hint = "First name" }
        val lastName = EditText(requireContext()).apply { hint = "Last name" }
        val email = EditText(requireContext()).apply {
            hint = "Email"
            inputType = InputType.TYPE_CLASS_TEXT or InputType.TYPE_TEXT_VARIATION_EMAIL_ADDRESS
        }
        val password = EditText(requireContext()).apply {
            hint = "Password (8+ characters)"
            inputType = InputType.TYPE_CLASS_TEXT or InputType.TYPE_TEXT_VARIATION_PASSWORD
        }
        container.addView(firstName)
        container.addView(lastName)
        container.addView(email)
        container.addView(password)

        val dialog = AlertDialog.Builder(requireContext())
            .setTitle("Create account")
            .setView(container)
            .setNegativeButton("Cancel", null)
            .setPositiveButton("Register", null)
            .create()
        dialog.setOnShowListener {
            dialog.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener {
                if (firstName.text.isNullOrBlank() || lastName.text.isNullOrBlank() || email.text.isNullOrBlank() || password.text.length < 8) {
                    Toast.makeText(requireContext(), "Complete all fields; password must be at least 8 characters", Toast.LENGTH_SHORT).show()
                    return@setOnClickListener
                }
                dialog.dismiss()
                viewModel.register(firstName.text.toString(), lastName.text.toString(), email.text.toString(), password.text.toString())
            }
        }
        dialog.show()
    }

    private fun showLoading() {
        binding.progressBar.visibility = View.VISIBLE
        binding.btnLogin.isEnabled = false
        binding.tvError.visibility = View.GONE
    }

    private fun hideLoading() {
        binding.progressBar.visibility = View.GONE
        binding.btnLogin.isEnabled = true
    }

    private fun navigateToFirstCount() {
        findNavController().popBackStack(R.id.loginFragment, true)
        findNavController().navigate(R.id.dashboardFragment)
    }

    override fun onDestroyView() {
        super.onDestroyView()
        viewModel.resetState()
        _binding = null
    }
}
