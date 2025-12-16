// ===================================
// INVENTARIO/STOCK - SIMPLE
// ===================================

let userId = null;
let editingProductId = null;

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
    const modal = document.getElementById('stockModal');
    const form = document.getElementById('stockForm');
    const closeBtn = document.getElementById('closeModal');
    const cancelBtn = document.getElementById('cancelBtn');

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
        await updateStock();
    });

    await loadInventory();
});

function openModal(product) {
    editingProductId = product.id;
    document.getElementById('productName').value = product.name;
    document.getElementById('currentStock').value = product.quantity;
    document.getElementById('newStock').value = product.quantity;
    document.getElementById('stockModal').style.display = 'flex';
}

function closeModal() {
    document.getElementById('stockModal').style.display = 'none';
    document.getElementById('stockForm').reset();
    editingProductId = null;
}

async function loadInventory() {
    const table = document.getElementById('stockTable');
    try {
        const response = await fetch(`${API_CONFIG.BASE_URL}/usuario/${userId}/inventario`, {
            headers: {
                'x-access-token': Auth.getToken()
            }
        });

        if (!response.ok) {
            throw new Error('Error al cargar inventario');
        }

        const data = await response.json();
        const items = data.data || [];

        if (items.length === 0) {
            table.innerHTML = '<tr><td colspan="5" class="empty-state">No hay productos en inventario</td></tr>';
            return;
        }

        table.innerHTML = items.map(item => {
            let statusBadge = '';
            let statusClass = '';
            
            if (item.quantity === 0) {
                statusBadge = '❌ Sin stock';
                statusClass = 'badge-danger';
            } else if (item.quantity <= 5) {
                statusBadge = '⚠️ Stock bajo';
                statusClass = 'badge-warning';
            } else {
                statusBadge = '✅ Normal';
                statusClass = 'badge-success';
            }

            return `
                <tr>
                    <td><strong>${item.name}</strong></td>
                    <td>${item.category_name || 'Sin categoría'}</td>
                    <td><span class="badge ${statusClass}">${item.quantity} unidades</span></td>
                    <td><span class="badge ${statusClass}">${statusBadge}</span></td>
                    <td>
                        <button class="btn-icon" onclick="editStock(${item.id}, '${item.name}', ${item.quantity})" title="Actualizar stock">📝</button>
                    </td>
                </tr>
            `;
        }).join('');

    } catch (error) {
        console.error('Error:', error);
        table.innerHTML = '<tr><td colspan="5" class="empty-state error">Error al cargar inventario</td></tr>';
    }
}

async function updateStock() {
    const newStock = parseInt(document.getElementById('newStock').value);

    if (isNaN(newStock) || newStock < 0) {
        alert('La cantidad debe ser un número válido mayor o igual a 0');
        return;
    }

    try {
        const response = await fetch(`${API_CONFIG.BASE_URL}/usuario/${userId}/inventario/${editingProductId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'x-access-token': Auth.getToken()
            },
            body: JSON.stringify({ quantity: newStock })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Error al actualizar stock');
        }

        UI.showSuccess('✅ Stock actualizado correctamente');
        closeModal();
        await loadInventory();

    } catch (error) {
        console.error('Error:', error);
        alert(error.message || 'Error al actualizar stock');
    }
}

window.editStock = (id, name, currentStock) => {
    openModal({ id, name, quantity: currentStock });
};