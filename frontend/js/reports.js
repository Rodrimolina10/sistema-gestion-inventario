// ===================================
// REPORTES - COMPLETO
// ===================================

let userId = null;

document.addEventListener('DOMContentLoaded', async () => {
    if (!Auth.isAuthenticated()) {
        window.location.href = '/login.html';
        return;
    }

    const user = Auth.getUser();
    userId = user?.id;

    if (!userId) {
        alert('Error: No se pudo obtener el ID del usuario');
        Auth.logout();
        return;
    }

    document.getElementById('userName').textContent = user.username;

    document.getElementById('logoutBtn').addEventListener('click', () => {
        if (confirm('¿Cerrar sesión?')) {
            Auth.logout();
        }
    });

    const menuToggle = document.getElementById('menuToggle');
    const sidebar = document.getElementById('sidebar');
    if (menuToggle && sidebar) {
        menuToggle.addEventListener('click', () => {
            sidebar.classList.toggle('active');
        });
    }

    await loadStats();
    await loadTopProducts();
});

async function loadStats() {
    try {
        const response = await fetch(`${API_CONFIG.BASE_URL}/usuario/${userId}/inventario/estadisticas`, {
            headers: {
                'x-access-token': Auth.getToken()
            }
        });

        if (!response.ok) throw new Error('Error al cargar estadísticas');

        const data = await response.json();

        document.getElementById('totalProducts').textContent = data.total_products || 0;
        document.getElementById('totalStock').textContent = data.total_units || 0;
        document.getElementById('lowStock').textContent = data.low_stock || 0;
        document.getElementById('outStock').textContent = data.out_of_stock || 0;

    } catch (error) {
        console.error('Error:', error);
    }
}

async function loadTopProducts() {
    const table = document.getElementById('topProducts');
    
    try {
        const response = await fetch(`${API_CONFIG.BASE_URL}/usuario/${userId}/informes/articulos-populares?limit=10`, {
            headers: {
                'x-access-token': Auth.getToken()
            }
        });

        if (!response.ok) throw new Error('Error al cargar productos');

        const data = await response.json();
        const products = data.data || [];

        // Filtrar solo productos que tienen pedidos (total_ordered > 0)
        const orderedProducts = products.filter(p => p.total_ordered > 0);

        if (orderedProducts.length === 0) {
            table.innerHTML = '<tr><td colspan="2" class="empty-state">No hay datos de compras aún</td></tr>';
            return;
        }

        table.innerHTML = orderedProducts.map(p => `
            <tr>
                <td><strong>${p.name}</strong></td>
                <td><span class="badge badge-primary">${p.total_ordered} unidades</span></td>
            </tr>
        `).join('');

    } catch (error) {
        console.error('Error:', error);
        table.innerHTML = '<tr><td colspan="2" class="empty-state error">Error al cargar productos</td></tr>';
    }
}