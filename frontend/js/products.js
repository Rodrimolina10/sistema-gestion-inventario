// ===================================
// PRODUCTOS - CON EDITAR COMPLETO
// ===================================

let userId = null;
let editingId = null;

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

    // MODAL
    const modal = document.getElementById('productModal');
    const form = document.getElementById('productForm');
    const newBtn = document.getElementById('newProductBtn');
    const closeBtn = document.getElementById('closeModal');
    const cancelBtn = document.getElementById('cancelBtn');

    newBtn.addEventListener('click', () => {
        openModal();
    });

    closeBtn.addEventListener('click', () => {
        closeModal();
    });

    cancelBtn.addEventListener('click', () => {
        closeModal();
    });

    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            closeModal();
        }
    });

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        await saveProduct();
    });

    await loadCategories();
    await loadProducts();
});

function openModal(product = null) {
    editingId = product?.id || null;
    document.getElementById('modalTitle').textContent = product ? 'Editar Producto' : 'Nuevo Producto';
    document.getElementById('productName').value = product?.name || '';
    document.getElementById('productPrice').value = product?.price || '';
    document.getElementById('productCategory').value = product?.category_id || '';
    
    // Ocultar campo de cantidad si estamos editando
    const quantityGroup = document.getElementById('quantityGroup');
    if (quantityGroup) {
        quantityGroup.style.display = product ? 'none' : 'block';
    }
    
    document.getElementById('productModal').style.display = 'flex';
}

function closeModal() {
    document.getElementById('productModal').style.display = 'none';
    document.getElementById('productForm').reset();
    editingId = null;
}

async function loadCategories() {
    try {
        const response = await fetch(`${API_CONFIG.BASE_URL}/usuario/${userId}/clasificaciones`, {
            headers: {
                'x-access-token': Auth.getToken()
            }
        });

        if (response.ok) {
            const data = await response.json();
            const select = document.getElementById('productCategory');
            select.innerHTML = '<option value="">Sin categoría</option>' +
                (data.data || []).map(cat => `<option value="${cat.id}">${cat.name}</option>`).join('');
        }
    } catch (error) {
        console.error('Error cargando categorías:', error);
    }
}

async function loadProducts() {
    const table = document.getElementById('productsTable');
    try {
        const response = await fetch(`${API_CONFIG.BASE_URL}/usuario/${userId}/articulos`, {
            headers: {
                'x-access-token': Auth.getToken()
            }
        });

        if (!response.ok) {
            throw new Error('Error al cargar productos');
        }

        const data = await response.json();
        const products = data.data || [];

        if (products.length === 0) {
            table.innerHTML = '<tr><td colspan="6" class="empty-state">No hay productos. Crea uno nuevo.</td></tr>';
            return;
        }

        table.innerHTML = products.map(prod => `
            <tr>
                <td><strong>${prod.name}</strong></td>
                <td>-</td>
                <td>$${parseFloat(prod.price).toFixed(2)}</td>
                <td>${prod.category_name || 'Sin categoría'}</td>
                <td><span class="badge ${prod.stock <= 5 ? 'badge-warning' : 'badge-success'}">${prod.stock}</span></td>
                <td>
                    <button class="btn-icon" onclick="editProduct(${prod.id})" title="Editar">✏️</button>
                    <button class="btn-icon" onclick="deleteProduct(${prod.id})" title="Eliminar">🗑️</button>
                </td>
            </tr>
        `).join('');

    } catch (error) {
        console.error('Error:', error);
        table.innerHTML = '<tr><td colspan="6" class="empty-state error">Error al cargar productos</td></tr>';
    }
}

async function saveProduct() {
    const name = document.getElementById('productName').value.trim();
    const price = parseFloat(document.getElementById('productPrice').value);
    const category_id = document.getElementById('productCategory').value || null;
    const quantity = editingId ? 0 : parseInt(document.getElementById('productQuantity')?.value || 0);

    if (!name) {
        alert('El nombre es requerido');
        return;
    }

    if (isNaN(price) || price < 0) {
        alert('El precio debe ser un número válido');
        return;
    }

    try {
        const url = editingId 
            ? `${API_CONFIG.BASE_URL}/usuario/${userId}/articulos/${editingId}`
            : `${API_CONFIG.BASE_URL}/usuario/${userId}/articulos`;
        
        const method = editingId ? 'PUT' : 'POST';

        const body = {
            name,
            price,
            category_id
        };

        // Solo agregar quantity al crear
        if (!editingId) {
            body.quantity = quantity;
        }

        const response = await fetch(url, {
            method,
            headers: {
                'Content-Type': 'application/json',
                'x-access-token': Auth.getToken()
            },
            body: JSON.stringify(body)
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Error al guardar');
        }

        UI.showSuccess(editingId ? '✅ Producto actualizado' : '✅ Producto creado');
        closeModal();
        await loadProducts();

    } catch (error) {
        console.error('Error:', error);
        alert(error.message || 'Error al guardar producto');
    }
}

window.editProduct = async (id) => {
    try {
        const response = await fetch(`${API_CONFIG.BASE_URL}/usuario/${userId}/articulos`, {
            headers: {
                'x-access-token': Auth.getToken()
            }
        });

        const data = await response.json();
        const product = data.data.find(p => p.id === id);

        if (product) {
            openModal(product);
        }
    } catch (error) {
        alert('Error al cargar producto');
    }
};

window.deleteProduct = async (id) => {
    if (!confirm('¿Eliminar este producto?')) return;

    try {
        const response = await fetch(`${API_CONFIG.BASE_URL}/usuario/${userId}/articulos/${id}`, {
            method: 'DELETE',
            headers: {
                'x-access-token': Auth.getToken()
            }
        });

        if (!response.ok) {
            throw new Error('Error al eliminar');
        }

        UI.showSuccess('✅ Producto eliminado');
        await loadProducts();

    } catch (error) {
        console.error('Error:', error);
        alert('Error al eliminar producto');
    }
};