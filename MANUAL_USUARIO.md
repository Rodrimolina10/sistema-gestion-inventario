# Manual de Usuario
## Sistema de Gestión de Inventario

---

## Índice

1. [Introducción](#1-introducción)
2. [Acceso al Sistema](#2-acceso-al-sistema)
3. [Dashboard](#3-dashboard)
4. [Gestión de Categorías](#4-gestión-de-categorías)
5. [Gestión de Productos](#5-gestión-de-productos)
6. [Control de Inventario](#6-control-de-inventario)
7. [Gestión de Proveedores](#7-gestión-de-proveedores)
8. [Órdenes de Compra](#8-órdenes-de-compra)
9. [Reportes](#9-reportes)
10. [Cerrar Sesión](#10-cerrar-sesión)

---

## 1. Introducción

El **Sistema de Gestión de Inventario** es una aplicación web diseñada para administrar el stock de productos de manera eficiente. Permite controlar categorías, productos, proveedores y órdenes de compra, además de generar reportes en tiempo real.

### Requisitos para usar el sistema:
- Navegador web moderno (Chrome, Firefox, Edge)
- Conexión a internet o red local
- Credenciales de acceso (usuario y contraseña)

---

## 2. Acceso al Sistema

### 2.1 Registro de Usuario

Si es la primera vez que usa el sistema:

1. Abra el navegador y vaya a `http://localhost:8000/register.html`
2. Complete el formulario:
   - **Usuario**: Nombre de usuario único
   - **Email**: Correo electrónico válido
   - **Contraseña**: Mínimo 6 caracteres
3. Haga clic en **"Registrarse"**
4. Será redirigido automáticamente al Dashboard

<!-- CAPTURA: Agregar captura de la pantalla de registro -->

### 2.2 Inicio de Sesión

Si ya tiene una cuenta:

1. Abra el navegador y vaya a `http://localhost:8000/login.html`
2. Ingrese sus credenciales:
   - **Usuario**: Su nombre de usuario
   - **Contraseña**: Su contraseña
3. Haga clic en **"Iniciar Sesión"**

<!-- CAPTURA: Agregar captura de la pantalla de login -->

---

## 3. Dashboard

El Dashboard es la pantalla principal del sistema. Muestra un resumen general del inventario.

### Elementos del Dashboard:

| Elemento | Descripción |
|----------|-------------|
| **Total Productos** | Cantidad de productos registrados |
| **Total en Stock** | Suma de todas las unidades en inventario |
| **Stock Bajo** | Productos con 5 o menos unidades |
| **Sin Stock** | Productos con 0 unidades |

### Navegación:

En el menú lateral (sidebar) encontrará acceso a todos los módulos:
- 📊 Dashboard
- 🏷️ Categorías
- 📦 Productos
- 📈 Inventario
- 🚚 Proveedores
- 📋 Órdenes
- 📑 Reportes

<!-- CAPTURA: Agregar captura del Dashboard -->

---

## 4. Gestión de Categorías

Las categorías permiten organizar los productos por tipo o grupo.

### 4.1 Ver Categorías

1. En el menú lateral, haga clic en **"Categorías"**
2. Se mostrará una tabla con todas las categorías existentes

### 4.2 Crear Categoría

1. Haga clic en el botón **"➕ Nueva Categoría"**
2. Complete el formulario:
   - **Nombre**: Nombre de la categoría (obligatorio)
   - **Descripción**: Descripción opcional
3. Haga clic en **"Guardar"**

### 4.3 Eliminar Categoría

1. En la tabla de categorías, busque la categoría a eliminar
2. Haga clic en el ícono **🗑️** (Eliminar)
3. Confirme la acción

> ⚠️ **Nota**: Al eliminar una categoría, los productos asociados quedarán sin categoría.

<!-- CAPTURA: Agregar captura de la pantalla de categorías -->

---

## 5. Gestión de Productos

Los productos son los artículos que se almacenan en el inventario.

### 5.1 Ver Productos

1. En el menú lateral, haga clic en **"Productos"**
2. Se mostrará una tabla con todos los productos

### 5.2 Crear Producto

1. Haga clic en el botón **"➕ Nuevo Producto"**
2. Complete el formulario:
   - **Nombre**: Nombre del producto (obligatorio)
   - **Precio**: Precio del producto
   - **Categoría**: Seleccione una categoría
   - **Cantidad inicial**: Stock inicial del producto
3. Haga clic en **"Guardar"**

### 5.3 Editar Producto

1. En la tabla de productos, busque el producto a editar
2. Haga clic en el ícono **✏️** (Editar)
3. Modifique los datos necesarios
4. Haga clic en **"Guardar"**

### 5.4 Eliminar Producto

1. Haga clic en el ícono **🗑️** (Eliminar)
2. Confirme la acción

> ⚠️ **Nota**: Al eliminar un producto, también se elimina su stock asociado.

<!-- CAPTURA: Agregar captura de la pantalla de productos -->

---

## 6. Control de Inventario

El módulo de inventario permite ver y actualizar el stock de cada producto.

### 6.1 Ver Inventario

1. En el menú lateral, haga clic en **"Inventario"**
2. Se mostrará una tabla con:
   - Nombre del producto
   - Categoría
   - Stock actual
   - Estado (Normal, Stock bajo, Sin stock)

### 6.2 Actualizar Stock

1. Busque el producto en la tabla
2. Haga clic en el ícono **📝** (Editar stock)
3. Ingrese la nueva cantidad
4. Haga clic en **"Actualizar"**

### Estados del Stock:

| Estado | Condición | Color |
|--------|-----------|-------|
| ✅ Normal | Más de 5 unidades | Verde |
| ⚠️ Stock bajo | Entre 1 y 5 unidades | Amarillo |
| ❌ Sin stock | 0 unidades | Rojo |

<!-- CAPTURA: Agregar captura de la pantalla de inventario -->

---

## 7. Gestión de Proveedores

Los proveedores son las empresas o personas que suministran productos.

### 7.1 Ver Proveedores

1. En el menú lateral, haga clic en **"Proveedores"**
2. Se mostrará una tabla con todos los proveedores

### 7.2 Crear Proveedor

1. Haga clic en el botón **"➕ Nuevo Proveedor"**
2. Complete el formulario:
   - **Nombre**: Nombre del proveedor (obligatorio)
   - **Teléfono**: Número de contacto
   - **Email**: Correo electrónico
3. Haga clic en **"Guardar"**

### 7.3 Eliminar Proveedor

1. Haga clic en el ícono **🗑️** (Eliminar)
2. Confirme la acción

<!-- CAPTURA: Agregar captura de la pantalla de proveedores -->

---

## 8. Órdenes de Compra

Las órdenes de compra permiten registrar pedidos de productos y actualizar automáticamente el stock cuando se confirman.

### 8.1 Ver Órdenes

1. En el menú lateral, haga clic en **"Órdenes"**
2. Se mostrará una tabla con todas las órdenes
3. Cada orden muestra:
   - ID de la orden
   - Fecha
   - Cantidad de productos
   - Estado (Pendiente/Completada)

### 8.2 Crear Orden

1. Haga clic en el botón **"➕ Nueva Orden"**
2. En el formulario:
   - Seleccione un **producto** del listado
   - Ingrese la **cantidad** a pedir
   - Haga clic en **"Agregar Producto"**
   - Repita para agregar más productos si es necesario
3. Haga clic en **"Crear Orden"**

### 8.3 Confirmar Orden

Cuando reciba los productos físicamente:

1. Busque la orden en la tabla
2. Haga clic en el ícono **✅** (Confirmar)
3. Confirme la acción

> ✅ **Importante**: Al confirmar una orden, el stock de los productos se actualiza automáticamente sumando las cantidades pedidas.

### 8.4 Eliminar Orden

1. Haga clic en el ícono **🗑️** (Eliminar)
2. Confirme la acción

<!-- CAPTURA: Agregar captura de la pantalla de órdenes -->

---

## 9. Reportes

El módulo de reportes muestra estadísticas y métricas del inventario.

### 9.1 Ver Reportes

1. En el menú lateral, haga clic en **"Reportes"**
2. Se mostrarán las siguientes métricas:

| Métrica | Descripción |
|---------|-------------|
| **Total Productos** | Cantidad de productos en el sistema |
| **Total en Stock** | Suma de todas las unidades |
| **Stock Bajo** | Productos con pocas unidades |
| **Sin Stock** | Productos agotados |

### 9.2 Productos Más Solicitados

En la sección inferior se muestra una tabla con los productos que más se han pedido en las órdenes de compra, ordenados de mayor a menor.

<!-- CAPTURA: Agregar captura de la pantalla de reportes -->

---

## 10. Cerrar Sesión

Para salir del sistema de forma segura:

1. En el menú lateral, haga clic en **"🚪 Cerrar Sesión"**
2. Confirme la acción
3. Será redirigido a la pantalla de inicio de sesión

> 💡 **Recomendación**: Siempre cierre sesión cuando termine de usar el sistema, especialmente en computadoras compartidas.

---

## Soporte

Si experimenta problemas con el sistema:

1. Verifique que el servidor backend esté en ejecución
2. Verifique que XAMPP (Apache y MySQL) esté activo
3. Limpie la caché del navegador (Ctrl+Shift+R)
4. Revise la consola del navegador (F12) para ver errores

---

**© 2024 - Sistema de Gestión de Inventario - Proyecto Informático**