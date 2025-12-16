// ===================================
// PROVEEDORES - SIMPLE
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

    // MODAL
    const modal = document.getElementById('supplierModal');
    const form = document.getElementById('supplierForm');
    const newBtn = document.getElementById('newSupplierBtn');
    const closeBtn = document.getElementById('closeModal');
    const cancelBtn = document.getElementById('cancelBtn');

    newBtn.addEventListener('click', () => {
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

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        await saveSupplier();
    });

    await loadSuppliers();
});

function closeModal() {
    document.getElementById('supplierModal').style.display = 'none';
    document.getElementById('supplierForm').reset();
}

async function loadSuppliers() {
    const table = document.getElementById('suppliersTable');
    try {
        const response = await fetch(`${API_CONFIG.BASE_URL}/usuario/${userId}/distribuidores`, {
            headers: {
                'x-access-token': Auth.getToken()
            }
        });

        if (!response.ok) {
            throw new Error('Error al cargar proveedores');
        }

        const data = await response.json();
        const suppliers = data.data || [];

        if (suppliers.length === 0) {
            table.innerHTML = '<tr><td colspan="6" class="empty-state">No hay proveedores. Crea uno nuevo.</td></tr>';
            return;
        }

        table.innerHTML = suppliers.map(sup => `
            <tr>
                <td><strong>${sup.name}</strong></td>
                <td>${sup.contact || '-'}</td>
                <td>${sup.phone || '-'}</td>
                <td>${sup.email || '-'}</td>
                <td><span class="badge badge-info">${sup.product_count} productos</span></td>
                <td>
                    <button class="btn-icon" onclick="deleteSupplier(${sup.id})" title="Eliminar">🗑️</button>
                </td>
            </tr>
        `).join('');

    } catch (error) {
        console.error('Error:', error);
        table.innerHTML = '<tr><td colspan="6" class="empty-state error">Error al cargar proveedores</td></tr>';
    }
}

async function saveSupplier() {
    const name = document.getElementById('supplierName').value.trim();
    const contact = document.getElementById('supplierContact')?.value.trim() || '';
    const phone = document.getElementById('supplierPhone').value.trim();
    const email = document.getElementById('supplierEmail').value.trim();

    if (!name) {
        alert('El nombre es requerido');
        return;
    }

    try {
        const response = await fetch(`${API_CONFIG.BASE_URL}/usuario/${userId}/distribuidores`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'x-access-token': Auth.getToken()
            },
            body: JSON.stringify({ name, contact, phone, email })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Error al guardar');
        }

        UI.showSuccess('✅ Proveedor creado exitosamente');
        closeModal();
        await loadSuppliers();

    } catch (error) {
        console.error('Error:', error);
        alert(error.message || 'Error al guardar proveedor');
    }
}

window.deleteSupplier = async (id) => {
    if (!confirm('¿Eliminar este proveedor?')) return;

    try {
        const response = await fetch(`${API_CONFIG.BASE_URL}/usuario/${userId}/distribuidores/${id}`, {
            method: 'DELETE',
            headers: {
                'x-access-token': Auth.getToken()
            }
        });

        if (!response.ok) {
            throw new Error('Error al eliminar');
        }

        UI.showSuccess('✅ Proveedor eliminado');
        await loadSuppliers();

    } catch (error) {
        console.error('Error:', error);
        alert('Error al eliminar proveedor');
    }
};