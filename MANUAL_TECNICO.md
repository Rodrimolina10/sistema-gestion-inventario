# Manual Técnico
## Sistema de Gestión de Inventario

---

## Índice

1. [Arquitectura del Sistema](#1-arquitectura-del-sistema)
2. [Tecnologías Utilizadas](#2-tecnologías-utilizadas)
3. [Base de Datos](#3-base-de-datos)
4. [Backend - API REST](#4-backend---api-rest)
5. [Frontend](#5-frontend)
6. [Autenticación y Seguridad](#6-autenticación-y-seguridad)
7. [Configuración del Entorno](#7-configuración-del-entorno)
8. [Despliegue](#8-despliegue)

---

## 1. Arquitectura del Sistema

El sistema sigue una arquitectura **Cliente-Servidor** de tres capas:

```
┌─────────────────┐     HTTP/JSON      ┌─────────────────┐     SQL      ┌─────────────────┐
│                 │ ◄───────────────► │                 │ ◄──────────► │                 │
│    FRONTEND     │                    │     BACKEND     │              │     MySQL       │
│   (HTML/CSS/JS) │                    │   (Flask API)   │              │   (Database)    │
│                 │                    │                 │              │                 │
│  Puerto: 8000   │                    │  Puerto: 5000   │              │  Puerto: 3306   │
└─────────────────┘                    └─────────────────┘              └─────────────────┘
      CLIENTE                              SERVIDOR                        BASE DE DATOS
```

### Flujo de Datos:

1. El **usuario** interactúa con el Frontend (navegador)
2. El Frontend envía peticiones **HTTP** al Backend
3. El Backend procesa la lógica y consulta la **Base de Datos**
4. La respuesta viaja en formato **JSON** de vuelta al Frontend
5. El Frontend actualiza la interfaz con los datos recibidos

---

## 2. Tecnologías Utilizadas

### 2.1 Backend

| Tecnología | Versión | Propósito |
|------------|---------|-----------|
| Python | 3.x | Lenguaje de programación |
| Flask | 3.0.0 | Framework web |
| Flask-CORS | 4.0.0 | Manejo de Cross-Origin Resource Sharing |
| PyJWT | 2.8.0 | Generación y validación de JSON Web Tokens |
| mysql-connector-python | 8.2.0 | Driver de conexión a MySQL |
| python-dotenv | 1.0.0 | Carga de variables de entorno |
| Werkzeug | 3.0.1 | Utilidades WSGI y hashing de contraseñas |

### 2.2 Frontend

| Tecnología | Propósito |
|------------|-----------|
| HTML5 | Estructura de las páginas |
| CSS3 | Estilos y diseño responsive |
| JavaScript (ES6+) | Lógica del cliente y peticiones AJAX |
| Fetch API | Comunicación asíncrona con el backend |
| LocalStorage | Almacenamiento del token JWT |

### 2.3 Base de Datos

| Tecnología | Propósito |
|------------|-----------|
| MySQL 8.0 | Sistema gestor de base de datos relacional |
| phpMyAdmin | Interfaz web para administración de MySQL |

---

## 3. Base de Datos

### 3.1 Diagrama Entidad-Relación

```
┌─────────────┐       ┌─────────────────┐       ┌─────────────┐
│   users     │       │    products     │       │ categories  │
├─────────────┤       ├─────────────────┤       ├─────────────┤
│ id (PK)     │───┐   │ id (PK)         │   ┌───│ id (PK)     │
│ username    │   │   │ name            │   │   │ name        │
│ email       │   │   │ price           │   │   │ descripcion │
│ password    │   └──►│ user_id (FK)    │   │   │ user_id(FK) │
│ created_at  │       │ category_id(FK) │◄──┘   │ created_at  │
└─────────────┘       └─────────────────┘       └─────────────┘
                              │
                              ▼
                      ┌─────────────┐
                      │    stock    │
                      ├─────────────┤
                      │product_id(PK/FK)│
                      │ quantity    │
                      │ user_id(FK) │
                      └─────────────┘

┌─────────────────┐       ┌───────────────────┐       ┌─────────────┐
│ purchase_orders │       │  order_products   │       │  suppliers  │
├─────────────────┤       ├───────────────────┤       ├─────────────┤
│ id (PK)         │───┐   │ id (PK)           │       │ id (PK)     │
│ order_date      │   └──►│ order_id (FK)     │       │name_supplier│
│ received_date   │       │ product_id (FK)   │       │ phone       │
│ status          │       │ quantity          │       │ mail        │
│ user_id (FK)    │       └───────────────────┘       │ user_id(FK) │
└─────────────────┘                                   └─────────────┘
```

### 3.2 Tablas

#### users
| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | INT (PK) | Identificador único |
| username | VARCHAR(50) | Nombre de usuario |
| email | VARCHAR(100) | Correo electrónico |
| password | VARCHAR(255) | Contraseña hasheada |
| created_at | TIMESTAMP | Fecha de creación |

#### categories
| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | INT (PK) | Identificador único |
| name | VARCHAR(255) | Nombre de la categoría |
| descripcion | TEXT | Descripción |
| user_id | INT (FK) | Usuario propietario |
| created_at | TIMESTAMP | Fecha de creación |

#### products
| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | INT (PK) | Identificador único |
| name | VARCHAR(255) | Nombre del producto |
| price | DECIMAL(10,2) | Precio |
| category_id | INT (FK) | Categoría asociada |
| user_id | INT (FK) | Usuario propietario |
| created_at | TIMESTAMP | Fecha de creación |

#### stock
| Campo | Tipo | Descripción |
|-------|------|-------------|
| product_id | INT (PK/FK) | ID del producto |
| quantity | INT | Cantidad en stock |
| user_id | INT (FK) | Usuario propietario |
| last_updated | TIMESTAMP | Última actualización |

#### suppliers
| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | INT (PK) | Identificador único |
| name_supplier | VARCHAR(255) | Nombre del proveedor |
| phone | VARCHAR(20) | Teléfono |
| mail | VARCHAR(255) | Email |
| user_id | INT (FK) | Usuario propietario |

#### purchase_orders
| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | INT (PK) | Identificador único |
| order_date | DATE | Fecha del pedido |
| received_date | DATE | Fecha de recepción |
| status | ENUM | pending, completed, deleted |
| user_id | INT (FK) | Usuario propietario |

#### order_products
| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | INT (PK) | Identificador único |
| order_id | INT (FK) | ID de la orden |
| product_id | INT (FK) | ID del producto |
| quantity | INT | Cantidad pedida |

### 3.3 Triggers

```sql
-- Trigger: Crear stock automáticamente al insertar producto
CREATE TRIGGER after_product_insert
AFTER INSERT ON products
FOR EACH ROW
BEGIN
    INSERT INTO stock (product_id, quantity, user_id)
    VALUES (NEW.id, 0, NEW.user_id);
END
```

---

## 4. Backend - API REST

### 4.1 Estructura de Carpetas

```
backend/
├── api/
│   ├── __init__.py      # Inicialización de Flask y rutas
│   ├── db/
│   │   └── db_config.py # Configuración de conexión a BD
│   ├── models/          # Lógica de negocio
│   ├── routes/          # Definición de endpoints
│   └── utils/
│       └── security.py  # JWT y autenticación
├── settings/            # Scripts SQL y requirements
├── .env                 # Variables de entorno
└── main.py              # Punto de entrada
```

### 4.2 Patrón de Diseño

El backend implementa el patrón **MVC (Model-View-Controller)**:

- **Models** (`api/models/`): Contienen la lógica de negocio y acceso a datos
- **Routes** (`api/routes/`): Actúan como controladores, reciben peticiones y devuelven respuestas
- **Views**: El frontend actúa como la vista

### 4.3 Endpoints de la API

#### Autenticación

```
POST /register
Body: { "username": "...", "email": "...", "password": "..." }
Response: { "token": "...", "user_id": 1 }

POST /login
Body: { "username": "...", "password": "..." }
Response: { "token": "...", "user_id": 1, "username": "..." }
```

#### Categorías

```
GET    /usuario/{id}/clasificaciones          # Listar
POST   /usuario/{id}/clasificaciones          # Crear
PUT    /usuario/{id}/clasificaciones/{cat_id} # Actualizar
DELETE /usuario/{id}/clasificaciones/{cat_id} # Eliminar
```

#### Productos

```
GET    /usuario/{id}/articulos                # Listar
POST   /usuario/{id}/articulos                # Crear
PUT    /usuario/{id}/articulos/{prod_id}      # Actualizar
DELETE /usuario/{id}/articulos/{prod_id}      # Eliminar
```

#### Inventario

```
GET /usuario/{id}/inventario                  # Listar stock
PUT /usuario/{id}/inventario/{prod_id}        # Actualizar cantidad
GET /usuario/{id}/inventario/estadisticas     # Métricas
GET /usuario/{id}/inventario/alerta-bajo      # Stock bajo
```

#### Proveedores

```
GET    /usuario/{id}/distribuidores           # Listar
POST   /usuario/{id}/distribuidores           # Crear
DELETE /usuario/{id}/distribuidores/{sup_id}  # Eliminar
```

#### Órdenes

```
GET    /usuario/{id}/pedidos                        # Listar
POST   /usuario/{id}/pedidos                        # Crear
PUT    /usuario/{id}/pedidos/{order_id}/confirmar   # Confirmar
DELETE /usuario/{id}/pedidos/{order_id}             # Eliminar
```

### 4.4 Formato de Respuestas

**Éxito:**
```json
{
    "data": [...],
    "message": "Operación exitosa"
}
```

**Error:**
```json
{
    "error": "Descripción del error"
}
```

---

## 5. Frontend

### 5.1 Estructura de Carpetas

```
frontend/
├── css/
│   ├── auth.css        # Estilos login/registro
│   ├── dashboard.css   # Estilos dashboard
│   ├── modal.css       # Estilos modales
│   └── styles.css      # Estilos generales
├── js/
│   ├── common/
│   │   └── config.js   # Configuración global (Auth, API_CONFIG, UI)
│   ├── categories.js
│   ├── dashboard.js
│   ├── orders.js
│   ├── products.js
│   ├── reports.js
│   ├── stock.js
│   └── suppliers.js
├── pages/              # Páginas internas
├── login.html
└── register.html
```

### 5.2 Objetos Globales (config.js)

```javascript
// Configuración de la API
const API_CONFIG = {
    BASE_URL: 'http://localhost:5000'
};

// Manejo de autenticación
const Auth = {
    isAuthenticated(),  // Verifica si hay sesión
    getToken(),         // Obtiene el JWT
    getUser(),          // Obtiene datos del usuario
    logout()            // Cierra sesión
};

// Utilidades de UI
const UI = {
    showSuccess(message),  // Muestra notificación de éxito
    showError(message)     // Muestra notificación de error
};
```

### 5.3 Flujo de Autenticación

```
1. Usuario ingresa credenciales
2. Frontend envía POST /login
3. Backend valida y devuelve JWT
4. Frontend guarda token en localStorage
5. Cada petición incluye header: x-access-token
6. Backend valida token en cada request
```

---

## 6. Autenticación y Seguridad

### 6.1 JSON Web Token (JWT)

El sistema usa JWT para autenticación stateless:

```python
# Generación del token
token = jwt.encode({
    'user_id': user_id,
    'exp': datetime.utcnow() + timedelta(hours=12)
}, SECRET_KEY, algorithm='HS256')
```

### 6.2 Hash de Contraseñas

Las contraseñas se almacenan hasheadas usando Werkzeug:

```python
# Al registrar
password_hash = generate_password_hash(password)

# Al verificar
check_password_hash(stored_hash, provided_password)
```

### 6.3 CORS

Se permite comunicación entre frontend (8000) y backend (5000):

```python
CORS(app, resources={r"/*": {"origins": "*"}})
```

---

## 7. Configuración del Entorno

### 7.1 Variables de Entorno (.env)

```env
DB_HOST=localhost          # Host de MySQL
DB_PORT=3306               # Puerto de MySQL
DB_USER=gestion_inv_user   # Usuario de BD
DB_PASSWORD=clave_app      # Contraseña de BD
DB_NAME=gestion_inventario # Nombre de la BD
PORT=5000                  # Puerto del backend
HOST=localhost             # Host del backend
```

### 7.2 Dependencias (requirements.txt)

```
Flask==3.0.0
Flask-Cors==4.0.0
PyJWT==2.8.0
mysql-connector-python==8.2.0
python-dotenv==1.0.0
Werkzeug==3.0.1
```

---

## 8. Despliegue

### 8.1 Requisitos del Servidor

- Python 3.8+
- MySQL 8.0+
- 512 MB RAM mínimo
- Puertos 5000 y 8000 disponibles

### 8.2 Pasos de Despliegue Local

1. Clonar repositorio
2. Crear entorno virtual
3. Instalar dependencias
4. Configurar base de datos
5. Crear archivo .env
6. Ejecutar backend: `python main.py`
7. Ejecutar frontend: `python -m http.server 8000`

### 8.3 Logs y Debugging

El backend imprime logs en consola:
```
✅ Rutas de categorías cargadas correctamente
✅ Rutas de productos cargadas correctamente
...
127.0.0.1 - - [DATE] "GET /usuario/1/articulos HTTP/1.1" 200 -
```

Para debug del frontend, usar la consola del navegador (F12).

---

**© 2025 - Sistema de Gestión de Inventario - Documentación Técnica**