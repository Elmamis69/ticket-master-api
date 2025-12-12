# 🚀 GUÍA DE IMPLEMENTACIÓN - Fase 2: Autenticación

## 📝 Ejemplos y Hints para implementar

### 1️⃣ Modelo User (app/models/user.py)

```python
# Ejemplo de cómo definir las columnas:

id = Column(Integer, primary_key=True, index=True)
email = Column(String(255), unique=True, index=True, nullable=False)
password_hash = Column(String(255), nullable=False)
full_name = Column(String(100), nullable=False)
role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
is_active = Column(Boolean, default=True, nullable=False)
created_at = Column(DateTime(timezone=True), server_default=func.now())
updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

---

### 2️⃣ Schemas User (app/schemas/user.py)

```python
# UserBase
class UserBase(BaseModel):
    email: EmailStr
    full_name: str


# UserCreate
class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    role: Optional[UserRole] = UserRole.USER


# UserUpdate
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8)
    is_active: Optional[bool] = None


# UserInDB
class UserInDB(UserBase):
    id: int
    role: UserRole
    is_active: bool
    created_at: datetime
    password_hash: str
    
    class Config:
        from_attributes = True


# UserResponse
class UserResponse(UserBase):
    id: int
    role: UserRole
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
```

---

### 3️⃣ Routes Auth (app/api/v1/routes_auth.py)

#### Endpoint: `/register`

```python
@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    # 1. Verificar si el email ya existe
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail = "Email already registered"
        )
    
    # 2. Hashear la contraseña
    hashed_password = get_password_hash(user_data.password)
    
    # 3. Crear el nuevo usuario
    new_user = User(
        email=user_data.email,
        full_name=user_data.full_name,
        password_hash=hashed_password,
        role=user_data.role
    )
    
    # 4. Guardar en la base de datos
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # 5. Retornar el usuario (sin password_hash)
    return new_user
```

#### Endpoint: `/login`

```python
@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # 1. Buscar usuario por email (form_data.username contiene el email)
    user = db.query(User).filter(User.email == form_data.username).first()
    
    # 2. Verificar si existe y si la contraseña es correcta
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail = "Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 3. Verificar si el usuario está activo
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail = "Inactive user"
        )
    
    # 4. Crear el token JWT
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)},  # "sub" es el subject del JWT
        expires_delta=access_token_expires
    )
    
    # 5. Retornar el token
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
```

#### Endpoint: `/me`

```python
@router.get("/me", response_model=UserResponse)
def get_current_user_info(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    # 1. Decodificar el token
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail = "Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 2. Extraer el user_id del payload
    user_id: str = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail = "Could not validate credentials"
        )
    
    # 3. Buscar el usuario en la base de datos
    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail = "User not found"
        )
    
    # 4. Retornar el usuario
    return user
```

---

## 🧪 Cómo probar tu código

### 1. Crear la migración de base de datos

```bash
# Dentro del contenedor
docker-compose exec api alembic revision --autogenerate -m "Create users table"

# Aplicar la migración
docker-compose exec api alembic upgrade head
```

### 2. Probar con curl o Postman

#### Registrar un usuario:
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "full_name": "Admin User",
    "password": "admin12345",
    "role": "ADMIN"
  }'
```

#### Login:
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@example.com&password=admin12345"
```

#### Obtener usuario actual:
```bash
# Usa el token que obtuviste del login
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### 3. Probar en Swagger UI
Abre: http://localhost:8000/docs

---

## 📚 Funciones útiles que ya tienes disponibles

### De `app.core.security`:
- `get_password_hash(password: str) -> str` - Hashea una contraseña
- `verify_password(plain_password: str, hashed_password: str) -> bool` - Verifica una contraseña
- `create_access_token(data: dict, expires_delta: Optional[timedelta]) -> str` - Crea un JWT
- `decode_access_token(token: str) -> Optional[dict]` - Decodifica un JWT

### De SQLAlchemy:
- `db.query(Model).filter(Model.field == value).first()` - Buscar un registro
- `db.query(Model).filter(Model.field == value).all()` - Buscar todos los registros
- `db.add(instance)` - Agregar un registro
- `db.commit()` - Guardar cambios
- `db.refresh(instance)` - Refrescar instancia con datos de BD

---

## 🎯 Checklist

- [ ] Completar modelo User con todas las columnas
- [ ] Completar todos los schemas Pydantic
- [ ] Implementar endpoint /register
- [ ] Implementar endpoint /login
- [ ] Implementar endpoint /me
- [ ] Crear migración de base de datos
- [ ] Probar todos los endpoints

---

## 💡 Tips

1. **Siempre usa `password_hash` en el modelo, nunca `password`**
2. **El campo `sub` en el JWT debe contener el `user_id` como string**
3. **Usa `EmailStr` de Pydantic para validar emails automáticamente**
4. **No retornes nunca `password_hash` en las respuestas de la API**
5. **Usa `Config.from_attributes = True` para que Pydantic pueda leer modelos SQLAlchemy**

---

¡Ahora codifica! 🚀
