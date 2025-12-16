// ===================================
// ÓRDENES - COMPLETO
// ===================================

let userId = null;
let orderItems = [];

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
    const modal = document.getElementById('orderModal');
    const form = document.getElementById('orderForm');
    const newBtn = document.getElementById('newOrderBtn');
    const closeBtn = document.getElementById('closeModal');
    const cancelBtn = document.getElementById('cancelBtn');
    const addProductBtn = document.getElementById('addProductBtn');

    newBtn.addEventListener('click', async () => {
        await loadProductsForOrder();
        orderItems = [];
        updateOrderItemsDisplay();
        modal.style.display = 'flex';
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

    addProductBtn.addEventListener('click', () => {
        addProductToOrder();
    });

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        await createOrder();
    });

    await loadOrders();
});

function closeModal() {
    document.getElementById('orderModal').style.display = 'none';
    document.getElementById('orderForm').reset();
    orderItems = [];
    updateOrderItemsDisplay();
}

async function loadProductsForOrder() {
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

        const select = document.getElementById('orderProduct');
        
        if (products.length === 0) {
            select.innerHTML = '<option value="">No hay productos disponibles</option>';
            return;
        }

        select.innerHTML = '<option value="">Seleccionar producto</option>' +
            products.map(p => `<option value="${p.id}" data-name="${p.name}">${p.name} ($${p.price})</option>`).join('');

    } catch (error) {
        console.error('Error:', error);
        alert('Error al cargar productos');
    }
}

function addProductToOrder() {
    const select = document.getElementById('orderProduct');
    const quantity = parseInt(document.getElementById('orderQuantity').value);

    if (!select.value) {
        alert('Selecciona un producto');
        return;
    }

    if (isNaN(quantity) || quantity <= 0) {
        alert('La cantidad debe ser mayor a 0');
        return;
    }

    const productId = parseInt(select.value);
    const productName = select.options[select.selectedIndex].getAttribute('data-name');

    // Verificar si ya está agregado
    const existingIndex = orderItems.findIndex(item => item.product_id === productId);
    if (existingIndex >= 0) {
        orderItems[existingIndex].quantity += quantity;
    } else {
        orderItems.push({
            product_id: productId,
            product_name: productName,
            quantity: quantity
        });
    }

    updateOrderItemsDisplay();
    document.getElementById('orderQuantity').value = 1;
}

function updateOrderItemsDisplay() {
    const container = document.getElementById('orderItems');

    if (orderItems.length === 0) {
        container.innerHTML = '<p style="color: #6b7280; text-align: center; padding: 1rem;">No hay productos agregados</p>';
        return;
    }

    container.innerHTML = `
        <div style="border: 1px solid #e5e7eb; border-radius: 8px; padding: 1rem; margin-top: 1rem;">
            <h3 style="margin: 0 0 1rem 0; font-size: 0.875rem; color: #374151;">Productos en la orden:</h3>
            ${orderItems.map((item, index) => `
                <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.5rem; border-bottom: 1px solid #f3f4f6;">
                    <div>
                        <strong>${item.product_name}</strong>
                        <span style="color: #6b7280;"> x ${item.quantity}</span>
                    </div>
                    <button type="button" onclick="removeOrderItem(${index})" style="background: #ef4444; color: white; border: none; padding: 0.25rem 0.75rem; border-radius: 4px; cursor: pointer;">
                        Quitar
                    </button>
                </div>
            `).join('')}
        </div>
    `;
}

window.removeOrderItem = (index) => {
    orderItems.splice(index, 1);
    updateOrderItemsDisplay();
};

async function createOrder() {
    if (orderItems.length === 0) {
        alert('Debes agregar al menos un producto');
        return;
    }

    try {
        const response = await fetch(`${API_CONFIG.BASE_URL}/usuario/${userId}/pedidos`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'x-access-token': Auth.getToken()
            },
            body: JSON.stringify({ items: orderItems })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Error al crear orden');
        }

        UI.showSuccess('✅ Orden creada exitosamente');
        closeModal();
        await loadOrders();

    } catch (error) {
        console.error('Error:', error);
        alert(error.message || 'Error al crear orden');
    }
}

async function loadOrders() {
    const table = document.getElementById('ordersTable');
    try {
        const response = await fetch(`${API_CONFIG.BASE_URL}/usuario/${userId}/pedidos`, {
            headers: {
                'x-access-token': Auth.getToken()
            }
        });

        if (!response.ok) {
            throw new Error('Error al cargar órdenes');
        }

        const data = await response.json();
        const orders = data.data || [];

        if (orders.length === 0) {
            table.innerHTML = '<tr><td colspan="5" class="empty-state">No hay órdenes. Crea una nueva.</td></tr>';
            return;
        }

        table.innerHTML = orders.map(order => {
            let statusBadge = '';
            if (order.status === 'pending') {
                statusBadge = '<span class="badge badge-warning">Pendiente</span>';
            } else if (order.status === 'completed') {
                statusBadge = '<span class="badge badge-success">Completada</span>';
            }

            return `
                <tr>
                    <td><strong>#${order.id}</strong></td>
                    <td>${order.order_date}</td>
                    <td>${order.product_count} productos</td>
                    <td>${statusBadge}</td>
                    <td>
                        ${order.status === 'pending' ? `<button class="btn-icon" onclick="confirmOrder(${order.id})" title="Confirmar orden">✅</button>` : ''}
                        <button class="btn-icon" onclick="deleteOrder(${order.id})" title="Eliminar">🗑️</button>
                    </td>
                </tr>
            `;
        }).join('');

    } catch (error) {
        console.error('Error:', error);
        table.innerHTML = '<tr><td colspan="5" class="empty-state error">Error al cargar órdenes</td></tr>';
    }
}

window.confirmOrder = async (id) => {
    if (!confirm('¿Confirmar esta orden? Esto actualizará el stock de los productos.')) return;

    try {
        const response = await fetch(`${API_CONFIG.BASE_URL}/usuario/${userId}/pedidos/${id}/confirmar`, {
            method: 'PUT',
            headers: {
                'x-access-token': Auth.getToken()
            }
        });

        if (!response.ok) {
            throw new Error('Error al confirmar orden');
        }

        UI.showSuccess('✅ Orden confirmada y stock actualizado');
        await loadOrders();

    } catch (error) {
        console.error('Error:', error);
        alert('Error al confirmar orden');
    }
};

window.deleteOrder = async (id) => {
    if (!confirm('¿Eliminar esta orden?')) return;

    try {
        const response = await fetch(`${API_CONFIG.BASE_URL}/usuario/${userId}/pedidos/${id}`, {
            method: 'DELETE',
            headers: {
                'x-access-token': Auth.getToken()
            }
        });

        if (!response.ok) {
            throw new Error('Error al eliminar');
        }

        UI.showSuccess('✅ Orden eliminada');
        await loadOrders();

    } catch (error) {
        console.error('Error:', error);
        alert('Error al eliminar orden');
    }
};