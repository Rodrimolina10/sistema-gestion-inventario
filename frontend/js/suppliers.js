// ===================================
// PROVEEDORES - CON MEJORA 3 IMPLEMENTADA
// ===================================

let userId = null;
let currentSupplierId = null;

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

    // MODAL PROVEEDOR
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

    // MODAL VINCULAR PRODUCTOS (MEJORA 3)
    setupLinkModal();

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

        // MEJORA 3: Agregado botón para vincular productos
        table.innerHTML = suppliers.map(sup => `
            <tr>
                <td><strong>${sup.name}</strong></td>
                <td>${sup.contact || '-'}</td>
                <td>${sup.phone || '-'}</td>
                <td>${sup.email || '-'}</td>
                <td>
                    <span class="badge badge-info" style="cursor:pointer" 
                          onclick="showSupplierProducts(${sup.id}, '${sup.name.replace(/'/g, "\\'")}')">
                        ${sup.product_count} productos
                    </span>
                </td>
                <td>
                    <button class="btn-icon" onclick="openLinkModal(${sup.id}, '${sup.name.replace(/'/g, "\\'")}')" title="Vincular Producto">🔗</button>
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


// =============================================
// MEJORA 3: FUNCIONES PARA VINCULAR PRODUCTOS
// =============================================

function setupLinkModal() {
    // Crear el modal dinámicamente si no existe
    if (!document.getElementById('linkProductModal')) {
        const modalHtml = `
            <div id="linkProductModal" class="modal" style="display:none;">
                <div class="modal-content">
                    <div class="modal-header">
                        <h2 id="linkModalTitle">Vincular Producto</h2>
                        <button class="modal-close" id="closeLinkModal">×</button>
                    </div>
                    <div style="padding: 20px;">
                        <div class="form-group">
                            <label>Seleccionar Producto:</label>
                            <select id="productSelect" class="form-control" style="width:100%; padding:10px; margin-top:5px;">
                                <option value="">-- Cargando --</option>
                            </select>
                        </div>
                        <button class="btn btn-primary" style="margin-top:10px;" onclick="linkSelectedProduct()">Vincular Producto</button>
                        
                        <hr style="margin: 20px 0;">
                        
                        <h4>Productos vinculados:</h4>
                        <ul id="linkedProductsList" style="list-style:none; padding:0;"></ul>
                    </div>
                    <div class="modal-footer">
                        <button class="btn btn-secondary" id="closeLinkBtn">Cerrar</button>
                    </div>
                </div>
            </div>
        `;
        document.body.insertAdjacentHTML('beforeend', modalHtml);
    }

    // Configurar eventos
    document.getElementById('closeLinkModal')?.addEventListener('click', closeLinkModal);
    document.getElementById('closeLinkBtn')?.addEventListener('click', closeLinkModal);
    
    document.getElementById('linkProductModal')?.addEventListener('click', (e) => {
        if (e.target.id === 'linkProductModal') {
            closeLinkModal();
        }
    });
}

function closeLinkModal() {
    document.getElementById('linkProductModal').style.display = 'none';
    currentSupplierId = null;
}

// Abrir modal para vincular productos a un proveedor
window.openLinkModal = async function(supplierId, supplierName) {
    currentSupplierId = supplierId;
    
    document.getElementById('linkModalTitle').textContent = `Vincular Producto a: ${supplierName}`;
    document.getElementById('linkProductModal').style.display = 'flex';
    
    // Cargar productos disponibles
    await loadProductsForSelect();
    
    // Cargar productos ya vinculados
    await loadLinkedProducts(supplierId);
};

// Cargar productos en el selector
async function loadProductsForSelect() {
    const select = document.getElementById('productSelect');
    select.innerHTML = '<option value="">-- Cargando --</option>';
    
    try {
        const response = await fetch(`${API_CONFIG.BASE_URL}/usuario/${userId}/articulos`, {
            headers: { 'x-access-token': Auth.getToken() }
        });
        
        const data = await response.json();
        const products = data.data || [];
        
        if (products.length === 0) {
            select.innerHTML = '<option value="">-- No hay productos --</option>';
            return;
        }
        
        select.innerHTML = '<option value="">-- Seleccionar --</option>' +
            products.map(p => `<option value="${p.id}">${p.name} - $${p.price}</option>`).join('');
        
    } catch (error) {
        console.error('Error:', error);
        select.innerHTML = '<option value="">-- Error --</option>';
    }
}

// Cargar productos ya vinculados a un proveedor
async function loadLinkedProducts(supplierId) {
    const list = document.getElementById('linkedProductsList');
    list.innerHTML = '<li>Cargando...</li>';
    
    try {
        const response = await fetch(
            `${API_CONFIG.BASE_URL}/usuario/${userId}/distribuidores/${supplierId}/productos`,
            { headers: { 'x-access-token': Auth.getToken() } }
        );
        
        const data = await response.json();
        const products = data.data || [];
        
        if (products.length === 0) {
            list.innerHTML = '<li style="color:#666;">No hay productos vinculados</li>';
            return;
        }
        
        list.innerHTML = products.map(p => `
            <li style="padding:8px 0; border-bottom:1px solid #eee; display:flex; justify-content:space-between; align-items:center;">
                <span>${p.name} - $${p.price.toFixed(2)}</span>
                <button class="btn-icon" onclick="unlinkProduct(${supplierId}, ${p.id})" title="Desvincular">❌</button>
            </li>
        `).join('');
        
    } catch (error) {
        console.error('Error:', error);
        list.innerHTML = '<li style="color:red;">Error al cargar</li>';
    }
}

// Vincular producto seleccionado
window.linkSelectedProduct = async function() {
    const productId = document.getElementById('productSelect').value;
    
    if (!productId) {
        alert('Selecciona un producto');
        return;
    }
    
    try {
        const response = await fetch(
            `${API_CONFIG.BASE_URL}/usuario/${userId}/proveedores/${currentSupplierId}/productos/${productId}`,
            {
                method: 'POST',
                headers: { 'x-access-token': Auth.getToken() }
            }
        );
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Error al vincular');
        }
        
        UI.showSuccess('✅ Producto vinculado');
        document.getElementById('productSelect').value = '';
        await loadLinkedProducts(currentSupplierId);
        await loadSuppliers();
        
    } catch (error) {
        alert(error.message);
    }
};

// Desvincular producto
window.unlinkProduct = async function(supplierId, productId) {
    if (!confirm('¿Desvincular este producto?')) return;
    
    try {
        const response = await fetch(
            `${API_CONFIG.BASE_URL}/usuario/${userId}/proveedores/${supplierId}/productos/${productId}`,
            {
                method: 'DELETE',
                headers: { 'x-access-token': Auth.getToken() }
            }
        );
        
        if (!response.ok) {
            throw new Error('Error al desvincular');
        }
        
        UI.showSuccess('✅ Producto desvinculado');
        await loadLinkedProducts(supplierId);
        await loadSuppliers();
        
    } catch (error) {
        alert(error.message);
    }
};

// Mostrar productos de un proveedor
window.showSupplierProducts = async function(supplierId, supplierName) {
    try {
        const response = await fetch(
            `${API_CONFIG.BASE_URL}/usuario/${userId}/distribuidores/${supplierId}/productos`,
            { headers: { 'x-access-token': Auth.getToken() } }
        );
        
        const data = await response.json();
        const products = data.data || [];
        
        let message = `Productos de "${supplierName}":\n\n`;
        
        if (products.length === 0) {
            message += 'No hay productos vinculados.';
        } else {
            products.forEach((p, i) => {
                message += `${i + 1}. ${p.name} - $${p.price.toFixed(2)}\n`;
            });
        }
        
        alert(message);
        
    } catch (error) {
        alert('Error al cargar productos');
    }
};

console.log('✅ Script de proveedores cargado');
