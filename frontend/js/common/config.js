// ===================================
// CONFIGURACIÓN Y UTILIDADES GLOBALES
// ===================================

// Configuración de la API (ENDPOINTS RENOMBRADOS)
const API_CONFIG = {
    BASE_URL: 'http://localhost:5000',
    ENDPOINTS: {
        // Autenticación
        LOGIN: '/login',
        REGISTER: '/register',
        
        // Clasificaciones (antes Categories)
        CLASIFICACIONES: (userId) => `/usuario/${userId}/clasificaciones`,
        CLASIFICACION: (userId, catId) => `/usuario/${userId}/clasificaciones/${catId}`,
        
        // Artículos (antes Products)
        ARTICULOS: (userId) => `/usuario/${userId}/articulos`,
        ARTICULO: (userId, prodId) => `/usuario/${userId}/articulos/${prodId}`,
        ARTICULOS_POR_CLASIFICACION: (userId, catId) => `/usuario/${userId}/articulos/por-clasificacion/${catId}`,
        
        // Inventario (antes Stock)
        INVENTARIO: (userId) => `/usuario/${userId}/inventario`,
        INVENTARIO_ITEM: (userId, prodId) => `/usuario/${userId}/inventario/${prodId}`,
        INVENTARIO_ALERTA: (userId) => `/usuario/${userId}/inventario/alerta-bajo`,
        INVENTARIO_STATS: (userId) => `/usuario/${userId}/inventario/estadisticas`,
        
        // Distribuidores (antes Suppliers)
        DISTRIBUIDORES: (userId) => `/usuario/${userId}/distribuidores`,
        DISTRIBUIDOR: (userId, suppId) => `/usuario/${userId}/distribuidores/${suppId}`,
        VINCULAR_ARTICULO: (userId, suppId, prodId) => `/usuario/${userId}/distribuidores/${suppId}/articulos/${prodId}`,
        DISTRIBUIDORES_POR_ARTICULO: (userId, prodId) => `/usuario/${userId}/articulos/${prodId}/distribuidores`,
        
        // Pedidos (antes Orders)
        PEDIDOS: (userId) => `/usuario/${userId}/pedidos`,
        PEDIDO: (userId, orderId) => `/usuario/${userId}/pedidos/${orderId}`,
        CONFIRMAR_PEDIDO: (userId, orderId) => `/usuario/${userId}/pedidos/${orderId}/confirmar`,
        
        // Informes (antes Reports)
        INFORME_COMPRAS: (userId) => `/usuario/${userId}/informes/resumen-compras`,
        INFORME_ARTICULOS: (userId) => `/usuario/${userId}/informes/articulos-populares`,
        INFORME_INVENTARIO: (userId) => `/usuario/${userId}/informes/resumen-inventario`,
        INFORME_PEDIDOS: (userId) => `/usuario/${userId}/informes/pedidos-por-estado`,
        INFORME_ACTIVIDAD: (userId) => `/usuario/${userId}/informes/actividad-reciente`,
    }
};

// Manejo de almacenamiento local
const Storage = {
    set: (key, value) => {
        try {
            localStorage.setItem(key, JSON.stringify(value));
        } catch (error) {
            console.error('Error guardando en localStorage:', error);
        }
    },
    
    get: (key) => {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : null;
        } catch (error) {
            console.error('Error leyendo de localStorage:', error);
            return null;
        }
    },
    
    remove: (key) => {
        try {
            localStorage.removeItem(key);
        } catch (error) {
            console.error('Error eliminando de localStorage:', error);
        }
    },
    
    clear: () => {
        try {
            localStorage.clear();
        } catch (error) {
            console.error('Error limpiando localStorage:', error);
        }
    }
};

// Manejo de autenticación
const Auth = {
    getToken: () => Storage.get('token'),
    
    setToken: (token) => Storage.set('token', token),
    
    removeToken: () => Storage.remove('token'),
    
    getUser: () => Storage.get('user'),
    
    setUser: (user) => Storage.set('user', user),
    
    removeUser: () => Storage.remove('user'),
    
    isAuthenticated: () => !!Auth.getToken(),
    
    logout: () => {
        Auth.removeToken();
        Auth.removeUser();
        window.location.href = '/login.html';
    },
    
    checkAuth: () => {
        if (!Auth.isAuthenticated()) {
            window.location.href = '/login.html';
        }
    }
};

// Cliente HTTP con autenticación
class APIClient {
    static async request(url, options = {}) {
        const token = Auth.getToken();
        const user = Auth.getUser();
        
        const defaultHeaders = {
            'Content-Type': 'application/json',
        };
        
        if (token && user) {
            defaultHeaders['x-access-token'] = token;
            defaultHeaders['user_id'] = user.id;
        }
        
        const config = {
            ...options,
            headers: {
                ...defaultHeaders,
                ...options.headers,
            },
        };
        
        try {
            const response = await fetch(url, config);
            const data = await response.json();
            
            if (!response.ok) {
                // Si es error 401, redirigir al login
                if (response.status === 401) {
                    Auth.logout();
                    throw new Error('Sesión expirada. Por favor, inicia sesión nuevamente');
                }
                throw new Error(data.error || data.message || 'Error en la petición');
            }
            
            return data;
        } catch (error) {
            console.error('Error en petición API:', error);
            throw error;
        }
    }
    
    static get(url, options = {}) {
        return this.request(url, { ...options, method: 'GET' });
    }
    
    static post(url, data, options = {}) {
        return this.request(url, {
            ...options,
            method: 'POST',
            body: JSON.stringify(data),
        });
    }
    
    static put(url, data, options = {}) {
        return this.request(url, {
            ...options,
            method: 'PUT',
            body: JSON.stringify(data),
        });
    }
    
    static delete(url, options = {}) {
        return this.request(url, { ...options, method: 'DELETE' });
    }
}

// Utilidades de UI
const UI = {
    showLoading: (element) => {
        if (element) {
            element.disabled = true;
            element.innerHTML = '<span class="spinner"></span> Cargando...';
        }
    },
    
    hideLoading: (element, originalText) => {
        if (element) {
            element.disabled = false;
            element.innerHTML = originalText;
        }
    },
    
    showToast: (message, type = 'info', duration = 3000) => {
        // Crear toast
        const toast = document.createElement('div');
        toast.className = `toast toast-${type} fade-in`;
        toast.textContent = message;
        
        // Estilos inline
        Object.assign(toast.style, {
            position: 'fixed',
            top: '20px',
            right: '20px',
            padding: '1rem 1.5rem',
            borderRadius: '10px',
            boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
            zIndex: '9999',
            maxWidth: '400px',
            fontWeight: '600',
            color: 'white',
        });
        
        // Color según tipo
        const colors = {
            success: '#10B981',
            error: '#EF4444',
            warning: '#F59E0B',
            info: '#3B82F6',
        };
        toast.style.background = colors[type] || colors.info;
        
        document.body.appendChild(toast);
        
        // Eliminar después del duration
        setTimeout(() => {
            toast.style.opacity = '0';
            setTimeout(() => toast.remove(), 300);
        }, duration);
    },
    
    showError: (message) => UI.showToast(message, 'error'),
    showSuccess: (message) => UI.showToast(message, 'success'),
    showWarning: (message) => UI.showToast(message, 'warning'),
    showInfo: (message) => UI.showToast(message, 'info'),
    
    confirmDialog: (message) => {
        return confirm(message);
    },
    
    formatDate: (dateString) => {
        if (!dateString) return 'N/A';
        const date = new Date(dateString);
        return date.toLocaleDateString('es-AR', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    },
    
    formatCurrency: (amount) => {
        return new Intl.NumberFormat('es-AR', {
            style: 'currency',
            currency: 'ARS'
        }).format(amount);
    },
    
    formatNumber: (number) => {
        return new Intl.NumberFormat('es-AR').format(number);
    }
};

// Validaciones
const Validator = {
    isEmpty: (value) => !value || value.trim() === '',
    
    isEmail: (email) => {
        const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return regex.test(email);
    },
    
    isPhone: (phone) => {
        const regex = /^[0-9]{8,15}$/;
        return regex.test(phone.replace(/[\s-]/g, ''));
    },
    
    isNumber: (value) => !isNaN(parseFloat(value)) && isFinite(value),
    
    isPositive: (value) => Validator.isNumber(value) && parseFloat(value) > 0,
    
    minLength: (value, min) => value && value.length >= min,
    
    maxLength: (value, max) => value && value.length <= max,
    
    isInRange: (value, min, max) => {
        const num = parseFloat(value);
        return num >= min && num <= max;
    }
};

// Exportar para uso global
window.API_CONFIG = API_CONFIG;
window.Storage = Storage;
window.Auth = Auth;
window.APIClient = APIClient;
window.UI = UI;
window.Validator = Validator;

console.log('✅ Sistema de configuración cargado correctamente');
