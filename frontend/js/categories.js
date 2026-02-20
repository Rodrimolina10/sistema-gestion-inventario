// ===================================
// CATEGORÍAS - CON MEJORAS IMPLEMENTADAS
// ===================================

let userId = null;
let editingCategoryId = null; // Para saber si estamos creando o editando

document.addEventListener('DOMContentLoaded', () => {
    console.log('🔵 Iniciando categorías...');
    
    // Verificar autenticación
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

    console.log('✅ User ID:', userId);

    // Mostrar nombre de usuario
    document.getElementById('userName').textContent = user.username;

    // Configurar logout
    document.getElementById('logoutBtn').addEventListener('click', () => {
        if (confirm('¿Cerrar sesión?')) {
            Auth.logout();
        }
    });

    // Configurar toggle del sidebar
    const menuToggle = document.getElementById('menuToggle');
    const sidebar = document.getElementById('sidebar');
    if (menuToggle && sidebar) {
        menuToggle.addEventListener('click', () => {
            sidebar.classList.toggle('active');
        });
    }

    // MODAL
    const modal = document.getElementById('categoryModal');
    const closeBtn = document.getElementById('closeModal');
    const cancelBtn = document.getElementById('cancelBtn');
    const form = document.getElementById('categoryForm');

    // Botón nueva categoría
    const newBtn = document.getElementById('newCategoryBtn');
    if (newBtn) {
        newBtn.addEventListener('click', (e) => {
            e.preventDefault();
            openModal();
        });
    }

    // Función para abrir modal en modo CREAR
    function openModal() {
        editingCategoryId = null; // No estamos editando
        document.getElementById('modalTitle').textContent = 'Nueva Categoría';
        document.getElementById('categoryName').value = '';
        document.getElementById('categoryDesc').value = '';
        modal.style.display = 'flex';
    }

    // Función para cerrar modal
    function closeModal() {
        modal.style.display = 'none';
        editingCategoryId = null;
        form.reset();
    }

    // Cerrar modal con X
    if (closeBtn) {
        closeBtn.addEventListener('click', closeModal);
    }

    // Cerrar modal con botón Cancelar
    if (cancelBtn) {
        cancelBtn.addEventListener('click', closeModal);
    }

    // Cerrar al hacer click fuera del modal
    if (modal) {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                closeModal();
            }
        });
    }

    // Submit del formulario - CREAR o EDITAR según corresponda
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const name = document.getElementById('categoryName').value.trim();
        const descripcion = document.getElementById('categoryDesc').value.trim();

        if (!name) {
            alert('El nombre es requerido');
            return;
        }

        try {
            let url = `${API_CONFIG.BASE_URL}/usuario/${userId}/clasificaciones`;
            let method = 'POST';

            // Si estamos editando, cambiar a PUT y agregar el ID a la URL
            if (editingCategoryId) {
                url += `/${editingCategoryId}`;
                method = 'PUT';
            }

            const response = await fetch(url, {
                method: method,
                headers: {
                    'Content-Type': 'application/json',
                    'x-access-token': Auth.getToken()
                },
                body: JSON.stringify({ name, descripcion })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Error al guardar');
            }

            // Mostrar mensaje según la acción
            if (editingCategoryId) {
                UI.showSuccess('✅ Categoría actualizada exitosamente');
            } else {
                UI.showSuccess('✅ Categoría creada exitosamente');
            }

            closeModal();
            await loadCategories();

        } catch (error) {
            console.error('❌ Error:', error);
            alert(error.message || 'Error al guardar categoría');
        }
    });

    // Cargar categorías al inicio
    loadCategories();
});

// Función para cargar y mostrar todas las categorías
async function loadCategories() {
    const table = document.getElementById('categoriesTable');

    try {
        const response = await fetch(`${API_CONFIG.BASE_URL}/usuario/${userId}/clasificaciones`, {
            headers: {
                'x-access-token': Auth.getToken()
            }
        });

        if (!response.ok) {
            throw new Error('Error al cargar categorías');
        }

        const data = await response.json();
        const categories = data.data || [];

        if (categories.length === 0) {
            table.innerHTML = '<tr><td colspan="4" class="empty-state">No hay categorías. Crea una nueva.</td></tr>';
            return;
        }

        table.innerHTML = categories.map(cat => `
            <tr>
                <td><strong>${cat.name}</strong></td>
                <td>${cat.descripcion || '-'}</td>
                <td><span class="badge badge-info">${cat.product_count || 0} productos</span></td>
                <td>
                    <button class="btn-icon" onclick="editCategory(${cat.id})" title="Editar">✏️</button>
                    <button class="btn-icon" onclick="deleteCategory(${cat.id})" title="Eliminar">🗑️</button>
                </td>
            </tr>
        `).join('');

    } catch (error) {
        console.error('❌ Error:', error);
        table.innerHTML = '<tr><td colspan="4" class="empty-state error">Error al cargar categorías</td></tr>';
    }
}

// MEJORA 1: Función para editar categoría
window.editCategory = async (id) => {
    console.log('🟡 Editando categoría:', id);

    try {
        // Obtener los datos actuales de la categoría desde el servidor
        const response = await fetch(
            `${API_CONFIG.BASE_URL}/usuario/${userId}/clasificaciones/${id}`,
            {
                headers: { 'x-access-token': Auth.getToken() }
            }
        );

        if (!response.ok) {
            throw new Error('No se pudo obtener la categoría');
        }

        const data = await response.json();
        const category = data.data;

        // Cargar los datos en el formulario
        document.getElementById('categoryName').value = category.name;
        document.getElementById('categoryDesc').value = category.descripcion || '';

        // Cambiar el título del modal
        document.getElementById('modalTitle').textContent = 'Editar Categoría';

        // Guardar el ID para saber que estamos editando
        editingCategoryId = id;

        // Mostrar el modal
        document.getElementById('categoryModal').style.display = 'flex';

    } catch (error) {
        console.error('❌ Error:', error);
        alert('Error al cargar la categoría para editar');
    }
};

// Función para eliminar categoría
window.deleteCategory = async (id) => {
    if (!confirm('¿Eliminar esta categoría?')) return;

    try {
        const response = await fetch(`${API_CONFIG.BASE_URL}/usuario/${userId}/clasificaciones/${id}`, {
            method: 'DELETE',
            headers: {
                'x-access-token': Auth.getToken()
            }
        });

        if (!response.ok) {
            throw new Error('Error al eliminar');
        }

        UI.showSuccess('✅ Categoría eliminada');
        await loadCategories();

    } catch (error) {
        console.error('❌ Error:', error);
        alert('Error al eliminar categoría');
    }
};

console.log('✅ Script de categorías cargado');
