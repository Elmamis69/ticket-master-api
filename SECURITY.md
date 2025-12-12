# 🔒 Guía de Seguridad

## ⚠️ IMPORTANTE: Credenciales y Secretos

Este proyecto utiliza **variables de entorno** para todas las credenciales sensibles. **NUNCA** commits credenciales reales al repositorio.

---

## 📝 Configuración de Variables de Entorno

### 1. Crear archivo `.env` (local)

```bash
cp .env.example .env
```

### 2. Generar valores seguros

```bash
# Generar SECRET_KEY para JWT
openssl rand -hex 32

# Generar INFLUXDB_TOKEN
openssl rand -hex 32

# Generar contraseñas seguras
openssl rand -base64 24
```

### 3. Actualizar `.env` con valores reales

Edita el archivo `.env` y reemplaza todos los valores `CHANGE_THIS_*` con credenciales seguras.

**Ejemplo:**
```env
SECRET_KEY=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6
POSTGRES_PASSWORD=MyS3cur3P@ssw0rd!2024
INFLUXDB_PASSWORD=An0th3rS3cur3P@ss!
INFLUXDB_TOKEN=def789abc456xyz123qwe789rty456uio123asd456fgh789
```

---

## 🚫 Qué NO hacer

❌ **NO** commits el archivo `.env` al repositorio (ya está en `.gitignore`)
❌ **NO** uses contraseñas como "admin123", "password", "123456"
❌ **NO** incluyas credenciales en código fuente
❌ **NO** compartas el archivo `.env` por email/Slack/chat
❌ **NO** uses las mismas contraseñas en desarrollo y producción

---

## ✅ Mejores Prácticas

### Desarrollo

- ✅ Usa `.env.example` como plantilla (sin valores reales)
- ✅ Genera contraseñas únicas para cada servicio
- ✅ Usa el archivo `.env` solo en tu máquina local
- ✅ Documenta qué variables se necesitan en `.env.example`

### Producción

- ✅ Usa gestores de secretos (AWS Secrets Manager, Azure Key Vault, etc.)
- ✅ Rota las credenciales periódicamente
- ✅ Usa contraseñas de al menos 20 caracteres
- ✅ Habilita autenticación de dos factores (2FA) donde sea posible
- ✅ Audita accesos a credenciales
- ✅ Usa HTTPS/TLS en todas las conexiones

### Docker / CI/CD

```bash
# Pasar variables de entorno sin exponer valores
docker run -e SECRET_KEY="$SECRET_KEY" my-api

# GitHub Actions: usar secrets
${{ secrets.SECRET_KEY }}

# Docker Compose (producción)
docker-compose -f docker-compose.prod.yml up -d
# Las variables se leen del entorno del host
```

---

## 🔐 Seed Data (Datos Iniciales)

El script `seed_data.py` crea usuarios de prueba. **Para producción:**

1. **NO ejecutes el seed script** con contraseñas débiles
2. Usa variables de entorno para contraseñas de seed:

```bash
export SEED_ADMIN_PASSWORD="$(openssl rand -base64 24)"
export SEED_AGENT_PASSWORD="$(openssl rand -base64 24)"
export SEED_USER_PASSWORD="$(openssl rand -base64 24)"

docker-compose exec api python -m app.scripts.seed_data
```

3. Guarda las contraseñas generadas en un gestor de contraseñas

---

## 🛡️ GitGuardian / Secret Scanning

Si recibes una alerta de GitGuardian:

1. **Rota inmediatamente** todas las credenciales expuestas
2. **Elimina el archivo** del historial de Git:
   ```bash
   # Eliminar archivo del historial
   git filter-branch --force --index-filter \
     "git rm --cached --ignore-unmatch path/to/file" \
     --prune-empty --tag-name-filter cat -- --all
   
   # O usa git-filter-repo (más rápido)
   git filter-repo --path path/to/file --invert-paths
   ```
3. **Fuerza el push** (⚠️ reescribe historial):
   ```bash
   git push origin --force --all
   ```
4. **Notifica al equipo** para que hagan `git pull --rebase`

---

## 📋 Checklist de Seguridad

Antes de hacer deploy a producción:

- [ ] Todas las variables en `.env` tienen valores seguros
- [ ] `SECRET_KEY` es único y generado con `openssl rand -hex 32`
- [ ] Las contraseñas tienen al menos 20 caracteres
- [ ] El archivo `.env` NO está en el repositorio
- [ ] `.gitignore` incluye `.env` y `.env.local`
- [ ] Las credenciales de base de datos son diferentes a desarrollo
- [ ] HTTPS está habilitado en todos los endpoints públicos
- [ ] Los logs NO muestran contraseñas o tokens
- [ ] CORS está configurado correctamente (no usar `*` en producción)
- [ ] Rate limiting está habilitado

---

## 📞 Reporte de Vulnerabilidades

Si encuentras una vulnerabilidad de seguridad, por favor **NO** abras un issue público. 

Contacta al equipo de seguridad en: **security@ticketsystem.com**

---

## 📚 Referencias

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [FastAPI Security Best Practices](https://fastapi.tiangolo.com/tutorial/security/)
- [Docker Security](https://docs.docker.com/engine/security/)
- [12-Factor App Config](https://12factor.net/config)
