// ===================================
// DASHBOARD - VERSIÓN ESTABLE
// ===================================

document.addEventListener('DOMContentLoaded', async () => {
    // Verificar autenticación
    if (!Auth.isAuthenticated()) {
        window.location.href = '/login.html';
        return;
    }

    const user = Auth.getUser();
    const userId = user?.id;

    if (!userId) {
        console.error('No se pudo obtener el ID del usuario');
        // NO redirigir, solo mostrar error
        showEmptyState();
        return;
    }

    // Mostrar nombre de usuario
    const userNameElement = document.getElementById('userName');
    if (userNameElement) {
        userNameElement.textContent = user.username || 'Usuario';
    }

    // Configurar botón de logout
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', () => {
            if (confirm('¿Estás seguro de que quieres cerrar sesión?')) {
                Auth.logout();
            }
        });
    }

    // Toggle sidebar en móvil
    const menuToggle = document.getElementById('menuToggle');
    const sidebar = document.getElementById('sidebar');
    
    if (menuToggle && sidebar) {
        menuToggle.addEventListener('click', () => {
            sidebar.classList.toggle('active');
        });
        
        // Cerrar sidebar al hacer click fuera
        document.addEventListener('click', (e) => {
            if (window.innerWidth <= 768) {
                if (!sidebar.contains(e.target) && !menuToggle.contains(e.target)) {
                    sidebar.classList.remove('active');
                }
            }
        });
    }

    // Cargar estadísticas
    await loadDashboardStats(userId);
});

async function loadDashboardStats(userId) {
    try {
        const response = await fetch(`${API_CONFIG.BASE_URL}/usuario/${userId}/informes/resumen-inventario`, {
            headers: {
                'x-access-token': Auth.getToken(),
                'user_id': userId
            }
        });

        if (!response.ok) {
            throw new Error('Error al cargar estadísticas');
        }

        const data = await response.json();

        // Actualizar cards de estadísticas
        updateStats(data);
        
        // Cargar tabla de productos con stock bajo
        loadLowStockTable(data.low_stock_products || []);
        
        // Cargar gráfico de categorías
        loadCategoriesChart(data.by_category || {});
        
    } catch (error) {
        console.error('Error cargando estadísticas:', error);
        showEmptyState();
    }
}

function updateStats(data) {
    const stats = {
        totalProducts: data.total_products || 0,
        totalStock: data.total_units || 0,
        lowStockItems: data.low_stock_count || 0,
        outOfStock: data.out_of_stock_count || 0
    };
    
    document.getElementById('totalProducts').textContent = stats.totalProducts;
    document.getElementById('totalStock').textContent = stats.totalStock;
    document.getElementById('lowStockItems').textContent = stats.lowStockItems;
    document.getElementById('outOfStock').textContent = stats.outOfStock;
}

function loadLowStockTable(products) {
    const tableBody = document.getElementById('lowStockTable');
    
    if (!products || products.length === 0) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="4" class="empty-state">
                    📦 <strong>No hay productos con stock bajo</strong>
                    <br><br>
                    <small>Esto es bueno, significa que tu inventario está bien abastecido.</small>
                    <br>
                    <small>Si aún no tienes productos, ve a <a href="/pages/categories.html">Categorías</a> y <a href="/pages/products.html">Productos</a> para comenzar.</small>
                </td>
            </tr>
        `;
        return;
    }

    tableBody.innerHTML = products.slice(0, 5).map(product => `
        <tr>
            <td><strong>${product.nombre || product.name}</strong></td>
            <td>${product.categoria || product.category || 'Sin categoría'}</td>
            <td>
                <span class="badge ${product.cantidad === 0 || product.stock === 0 ? 'badge-danger' : 'badge-warning'}">
                    ${product.cantidad || product.stock || 0} unidades
                </span>
            </td>
            <td>
                ${(product.cantidad === 0 || product.stock === 0)
                    ? '<span class="badge badge-danger">Sin stock</span>'
                    : '<span class="badge badge-warning">Stock bajo</span>'
                }
            </td>
        </tr>
    `).join('');
}

function loadCategoriesChart(byCategory) {
    const chartContainer = document.getElementById('categoriesChart');
    
    if (!byCategory || Object.keys(byCategory).length === 0) {
        chartContainer.innerHTML = `
            <p class="loading">
                📊 <strong>No hay productos por categoría</strong>
                <br><br>
                <small>Comienza agregando categorías y productos para ver estadísticas aquí.</small>
            </p>
        `;
        return;
    }

    // Crear gráfico simple de barras
    const maxValue = Math.max(...Object.values(byCategory));
    
    chartContainer.innerHTML = `
        <div class="bar-chart">
            ${Object.entries(byCategory).map(([category, count]) => {
                const percentage = (count / maxValue) * 100;
                return `
                    <div class="bar-item">
                        <div class="bar-label">
                            <span><strong>${category}</strong></span>
                            <span>${count} productos</span>
                        </div>
                        <div class="bar-container">
                            <div class="bar-fill" style="width: ${percentage}%"></div>
                        </div>
                    </div>
                `;
            }).join('')}
        </div>
    `;
}

function showEmptyState() {
    // Actualizar estadísticas a 0
    document.getElementById('totalProducts').textContent = '0';
    document.getElementById('totalStock').textContent = '0';
    document.getElementById('lowStockItems').textContent = '0';
    document.getElementById('outOfStock').textContent = '0';
    
    // Mostrar mensaje amigable en la tabla
    document.getElementById('lowStockTable').innerHTML = `
        <tr>
            <td colspan="4" class="empty-state">
                🎉 <strong>¡Bienvenido a tu Sistema de Inventario!</strong>
                <br><br>
                <strong>Para comenzar:</strong>
                <br>
                1️⃣ Ve a <a href="/pages/categories.html" style="color: var(--accent-color); font-weight: 600;">Categorías</a> y crea tu primera categoría
                <br>
                2️⃣ Luego ve a <a href="/pages/products.html" style="color: var(--accent-color); font-weight: 600;">Productos</a> y agrega productos
                <br>
                3️⃣ Vuelve aquí para ver tus estadísticas
            </td>
        </tr>
    `;
    
    // Mostrar mensaje en el gráfico
    document.getElementById('categoriesChart').innerHTML = `
        <p class="loading">
            📊 <strong>Tus estadísticas aparecerán aquí</strong>
            <br><br>
            <small>Una vez que agregues productos, verás gráficos y análisis de tu inventario.</small>
        </p>
    `;
}