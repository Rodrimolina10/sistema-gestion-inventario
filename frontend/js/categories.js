// ===================================
// CATEGORÍAS - VERSIÓN SIMPLE
// ===================================

let userId = null;

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

    console.log('🔵 Modal:', modal ? 'Encontrado' : 'NO ENCONTRADO');

    // Buscar botón de todas las formas posibles
    let newBtn = document.getElementById('newCategoryBtn');
    if (!newBtn) {
        newBtn = document.querySelector('.btn-primary');
        console.log('🔵 Botón encontrado con querySelector');
    }
    if (!newBtn) {
        newBtn = document.querySelector('button[id*="Category"]');
        console.log('🔵 Botón encontrado con búsqueda parcial');
    }

    console.log('🔵 Botón Nueva Categoría:', newBtn ? 'Encontrado' : 'NO ENCONTRADO');
    
    if (newBtn) {
        console.log('🔵 Registrando evento click...');
        
        // Método 1: addEventListener
        newBtn.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            console.log('🟢 Click en Nueva Categoría (addEventListener)');
            openModal();
        }, true); // true = captura en fase de captura
        
        // Método 2: onclick directo
        newBtn.onclick = (e) => {
            e.preventDefault();
            e.stopPropagation();
            console.log('🟢 Click directo en Nueva Categoría (onclick)');
            openModal();
            return false;
        };
        
        // Método 3: Agregar atributo onclick al HTML
        newBtn.setAttribute('onclick', 'openModalGlobal(); return false;');
        
        // Método 4: Mousedown como respaldo
        newBtn.addEventListener('mousedown', (e) => {
            console.log('🟡 MouseDown detectado');
            openModal();
        });
        
        console.log('✅ Todos los eventos registrados');
    } else {
        console.error('❌ NO SE ENCONTRÓ EL BOTÓN');
    }
    
    function openModal() {
        console.log('📂 Abriendo modal...');
        modal.style.display = 'flex';
        modal.style.opacity = '1';
        modal.style.visibility = 'visible';
        modal.style.zIndex = '9999';
        document.getElementById('categoryName').value = '';
        document.getElementById('categoryDesc').value = '';
    }
    
    // Hacer openModal global para que onclick del HTML funcione
    window.openModalGlobal = openModal;

    function openModal() {
        console.log('📂 Abriendo modal...');
        modal.style.display = 'flex';
        document.getElementById('categoryName').value = '';
        document.getElementById('categoryDesc').value = '';
    }

    // Cerrar modal
    if (closeBtn) {
        closeBtn.addEventListener('click', () => {
            console.log('🔴 Cerrando modal');
            modal.style.display = 'none';
        });
    }

    if (cancelBtn) {
        cancelBtn.addEventListener('click', () => {
            console.log('🔴 Cancelando');
            modal.style.display = 'none';
        });
    }

    // Cerrar al hacer click fuera
    if (modal) {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.style.display = 'none';
            }
        });
    }

    // Submit del formulario
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        console.log('🟡 Guardando categoría...');
        
        const name = document.getElementById('categoryName').value.trim();
        const descripcion = document.getElementById('categoryDesc').value.trim();

        if (!name) {
            alert('El nombre es requerido');
            return;
        }

        try {
            const response = await fetch(`${API_CONFIG.BASE_URL}/usuario/${userId}/clasificaciones`, {
                method: 'POST',
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

            console.log('✅ Categoría guardada');
            UI.showSuccess('✅ Categoría creada exitosamente');
            modal.style.display = 'none';
            form.reset();
            await loadCategories();

        } catch (error) {
            console.error('❌ Error:', error);
            alert(error.message || 'Error al guardar categoría');
        }
    });

    // Cargar categorías
    loadCategories();
});

async function loadCategories() {
    const table = document.getElementById('categoriesTable');
    console.log('🔵 Cargando categorías...');

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

        console.log('✅ Categorías cargadas:', categories.length);

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
                    <button class="btn-icon" onclick="editCategory(${cat.id}, '${cat.name}', '${cat.descripcion || ''}')" title="Editar">✏️</button>
                    <button class="btn-icon" onclick="deleteCategory(${cat.id})" title="Eliminar">🗑️</button>
                </td>
            </tr>
        `).join('');

    } catch (error) {
        console.error('❌ Error:', error);
        table.innerHTML = '<tr><td colspan="4" class="empty-state error">Error al cargar categorías</td></tr>';
    }
}

window.editCategory = (id, name, descripcion) => {
    console.log('🟡 Editando categoría:', id);
    alert('Editar no está implementado aún. Puedes eliminarlo y crear uno nuevo.');
};

window.deleteCategory = async (id) => {
    if (!confirm('¿Eliminar esta categoría?')) return;

    console.log('🔴 Eliminando categoría:', id);

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

        console.log('✅ Categoría eliminada');
        UI.showSuccess('✅ Categoría eliminada');
        await loadCategories();

    } catch (error) {
        console.error('❌ Error:', error);
        alert('Error al eliminar categoría');
    }
};

console.log('✅ Script de categorías cargado');