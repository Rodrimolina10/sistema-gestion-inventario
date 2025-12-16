// ===================================
// LOGIN - CON RUTA CORREGIDA
// ===================================

document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('loginForm');
    const togglePassword = document.getElementById('togglePassword');
    const passwordInput = document.getElementById('password');
    
    // Toggle mostrar/ocultar contraseña
    if (togglePassword && passwordInput) {
        togglePassword.addEventListener('click', () => {
            const type = passwordInput.type === 'password' ? 'text' : 'password';
            passwordInput.type = type;
            togglePassword.textContent = type === 'password' ? '👁️' : '🙈';
        });
    }
    
    // Manejar submit del formulario
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const username = document.getElementById('username').value.trim();
            const password = document.getElementById('password').value;
            const loginButton = document.getElementById('loginButton');
            
            // Validaciones
            if (!username || !password) {
                UI.showError('Por favor completa todos los campos');
                return;
            }
            
            // Deshabilitar botón y mostrar loading
            const originalText = loginButton.innerHTML;
            UI.showLoading(loginButton);
            
            try {
                const response = await fetch(`${API_CONFIG.BASE_URL}/login`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ username, password })
                });
                
                const data = await response.json();
                
                if (!response.ok) {
                    throw new Error(data.error || 'Error al iniciar sesión');
                }
                
                // Guardar token
                Auth.setToken(data.token);
                
                // Guardar usuario con el formato esperado
                Auth.setUser({
                    id: data.user_id,
                    username: data.username
                });
                
                // También guardar en formato simple para compatibilidad
                localStorage.setItem('user_id', data.user_id);
                localStorage.setItem('username', data.username);
                
                UI.showSuccess('¡Inicio de sesión exitoso!');
                
                // Redireccionar después de 500ms
                setTimeout(() => {
                    window.location.href = '/pages/dashboard.html';
                }, 500);
                
            } catch (error) {
                console.error('Error:', error);
                UI.showError(error.message || 'Error al iniciar sesión. Verifica tus credenciales.');
                UI.hideLoading(loginButton, originalText);
            }
        });
    }
    
    // Si ya hay sesión, redireccionar
    if (Auth.isAuthenticated()) {
        window.location.href = '/pages/dashboard.html';
    }
});