// ===================================
// REGISTER - CON RUTA CORREGIDA
// ===================================

document.addEventListener('DOMContentLoaded', () => {
    const registerForm = document.getElementById('registerForm');
    const togglePassword = document.getElementById('togglePassword');
    const toggleConfirmPassword = document.getElementById('toggleConfirmPassword');
    const passwordInput = document.getElementById('password');
    const confirmPasswordInput = document.getElementById('confirmPassword');
    
    // Toggle mostrar/ocultar contraseña
    if (togglePassword && passwordInput) {
        togglePassword.addEventListener('click', () => {
            const type = passwordInput.type === 'password' ? 'text' : 'password';
            passwordInput.type = type;
            togglePassword.textContent = type === 'password' ? '👁️' : '🙈';
        });
    }
    
    if (toggleConfirmPassword && confirmPasswordInput) {
        toggleConfirmPassword.addEventListener('click', () => {
            const type = confirmPasswordInput.type === 'password' ? 'text' : 'password';
            confirmPasswordInput.type = type;
            toggleConfirmPassword.textContent = type === 'password' ? '👁️' : '🙈';
        });
    }
    
    // Manejar submit del formulario
    if (registerForm) {
        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const username = document.getElementById('username').value.trim();
            const password = document.getElementById('password').value;
            const confirmPassword = confirmPasswordInput ? confirmPasswordInput.value : password;
            const registerButton = document.getElementById('registerButton');
            
            // Validaciones
            if (!username || !password) {
                UI.showError('Por favor completa todos los campos');
                return;
            }
            
            if (username.length < 3) {
                UI.showError('El usuario debe tener al menos 3 caracteres');
                return;
            }
            
            if (password.length < 4) {
                UI.showError('La contraseña debe tener al menos 4 caracteres');
                return;
            }
            
            if (confirmPasswordInput && password !== confirmPassword) {
                UI.showError('Las contraseñas no coinciden');
                return;
            }
            
            // Deshabilitar botón y mostrar loading
            const originalText = registerButton.innerHTML;
            UI.showLoading(registerButton);
            
            try {
                const response = await fetch(`${API_CONFIG.BASE_URL}/register`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ username, password })
                });
                
                const data = await response.json();
                
                if (!response.ok) {
                    throw new Error(data.error || 'Error al registrarse');
                }
                
                UI.showSuccess('¡Registro exitoso! Redirigiendo al login...');
                
                // Redireccionar después de 2 segundos
                setTimeout(() => {
                    window.location.href = '/login.html';
                }, 2000);
                
            } catch (error) {
                console.error('Error:', error);
                UI.showError(error.message || 'Error al registrarse. El usuario puede estar en uso.');
                UI.hideLoading(registerButton, originalText);
            }
        });
    }
    
    // Si ya hay sesión, redireccionar
    if (Auth.isAuthenticated()) {
        window.location.href = '/pages/dashboard.html';
    }
});