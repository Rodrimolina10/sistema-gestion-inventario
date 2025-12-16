# Sistema de Gestión de Inventario

Sistema web completo para la gestión de inventario desarrollado con Flask (Backend) y HTML/CSS/JavaScript (Frontend).

## 📋 Descripción

Este proyecto permite gestionar el inventario de productos de una empresa, incluyendo:

- Registro e inicio de sesión de usuarios con autenticación JWT
- Gestión de categorías de productos
- Gestión de productos con precios y categorización
- Control de stock con alertas de inventario bajo
- Gestión de proveedores
- Órdenes de compra con actualización automática de stock
- Reportes y estadísticas del inventario

## 🛠️ Requisitos

- [Python 3.x](https://www.python.org/downloads/)
- [Git](https://git-scm.com/)
- [XAMPP](https://www.apachefriends.org/es/download.html) (para MySQL)

## 📦 Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/Rodrimolina10/proyecto-gestion-inventario-upso.git
cd proyecto-gestion-inventario-upso/PROYECTO-FINAL-COMPLETO
```

### 2. Configurar el Backend

```bash
cd backend
py -3 -m venv .venv
.venv\Scripts\activate
pip install -r settings/requirements.txt
```

### 3. Configurar la Base de Datos

1. Iniciar XAMPP y activar MySQL
2. Abrir phpMyAdmin (http://localhost/phpmyadmin)
3. Ejecutar los scripts SQL en orden:
   - `settings/create_db.sql`
   - `settings/create_user.sql`
   - `settings/schema.sql`

### 4. Configurar Variables de Entorno

Crear archivo `.env` en la carpeta `backend/` con:

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=flask_user
DB_PASSWORD=flask_password
DB_NAME=flask_app_db
PORT=5000
HOST=localhost
JWT_SECRET_KEY=tu_clave_secreta
```

### 5. Ejecutar el Sistema

**Backend:**
```bash
cd backend
python main.py
```

**Frontend:**
Abrir `frontend/login.html` en el navegador.

## 📁 Estructura del Proyecto

```
PROYECTO-FINAL-COMPLETO/
├── backend/
│   ├── api/
│   │   ├── db/
│   │   │   └── db_config.py
│   │   ├── models/
│   │   │   ├── categories.py
│   │   │   ├── orders.py
│   │   │   ├── products.py
│   │   │   ├── reports.py
│   │   │   ├── stock.py
│   │   │   ├── supplier.py
│   │   │   └── user.py
│   │   ├── routes/
│   │   │   ├── categories.py
│   │   │   ├── orders.py
│   │   │   ├── products.py
│   │   │   ├── reports.py
│   │   │   ├── stock.py
│   │   │   ├── supplier.py
│   │   │   └── user.py
│   │   ├── utils/
│   │   │   └── security.py
│   │   └── __init__.py
│   ├── settings/
│   │   ├── create_db.sql
│   │   ├── create_user.sql
│   │   ├── requirements.txt
│   │   └── schema.sql
│   ├── .env
│   └── main.py
├── frontend/
│   ├── css/
│   │   ├── auth.css
│   │   ├── dashboard.css
│   │   ├── modal.css
│   │   └── styles.css
│   ├── js/
│   │   ├── common/
│   │   │   └── config.js
│   │   ├── categories.js
│   │   ├── dashboard.js
│   │   ├── orders.js
│   │   ├── products.js
│   │   ├── reports.js
│   │   ├── stock.js
│   │   └── suppliers.js
│   ├── pages/
│   │   ├── categories.html
│   │   ├── dashboard.html
│   │   ├── orders.html
│   │   ├── products.html
│   │   ├── reports.html
│   │   ├── stock.html
│   │   └── suppliers.html
│   ├── login.html
│   └── register.html
├── diagramas/
│   ├── User.png
│   ├── Category.png
│   ├── Product.png
│   ├── Stock.png
│   ├── Supplier.png
│   └── Order.png
├── Documentacion.pdf
├── MANUAL_USUARIO.md
├── MANUAL_TECNICO.md
└── README.md
```

## 🔌 API Endpoints

### Usuarios
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/registro` | Registrar nuevo usuario |
| POST | `/login` | Iniciar sesión |

### Categorías
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/usuario/{id}/clasificaciones` | Listar categorías |
| POST | `/usuario/{id}/clasificaciones` | Crear categoría |
| PUT | `/usuario/{id}/clasificaciones/{cat_id}` | Actualizar categoría |
| DELETE | `/usuario/{id}/clasificaciones/{cat_id}` | Eliminar categoría |

### Productos
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/usuario/{id}/articulos` | Listar productos |
| POST | `/usuario/{id}/articulos` | Crear producto |
| PUT | `/usuario/{id}/articulos/{prod_id}` | Actualizar producto |
| DELETE | `/usuario/{id}/articulos/{prod_id}` | Eliminar producto |

### Stock
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/usuario/{id}/inventario` | Ver inventario |
| PUT | `/usuario/{id}/inventario/{prod_id}` | Actualizar stock |
| GET | `/usuario/{id}/inventario/bajo` | Productos con stock bajo |

### Proveedores
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/usuario/{id}/proveedores` | Listar proveedores |
| POST | `/usuario/{id}/proveedores` | Crear proveedor |
| DELETE | `/usuario/{id}/proveedores/{sup_id}` | Eliminar proveedor |

### Órdenes
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/usuario/{id}/pedidos` | Listar órdenes |
| POST | `/usuario/{id}/pedidos` | Crear orden |
| PUT | `/usuario/{id}/pedidos/{ord_id}/confirmar` | Confirmar orden |
| DELETE | `/usuario/{id}/pedidos/{ord_id}` | Eliminar orden |

### Reportes
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/usuario/{id}/reportes/estadisticas` | Estadísticas generales |
| GET | `/usuario/{id}/reportes/mas-pedidos` | Productos más pedidos |

## 🛡️ Tecnologías Utilizadas

### Backend
- Python 3.x
- Flask
- Flask-CORS
- PyJWT
- mysql-connector-python
- python-dotenv
- Werkzeug

### Frontend
- HTML5
- CSS3
- JavaScript (Vanilla)
- Fetch API

### Base de Datos
- MySQL
- XAMPP

## 📊 Diagramas

Los diagramas UML de secuencia se encuentran en la carpeta `/diagramas/` y muestran el flujo de cada módulo del sistema.

## 📄 Documentación

- `Documentacion.pdf` - Documentación completa del proyecto
- `MANUAL_USUARIO.md` - Manual de usuario
- `MANUAL_TECNICO.md` - Manual técnico

## 📝 Licencia

Proyecto desarrollado para la materia Proyecto Informático - UPSO 2024