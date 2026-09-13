# Desarrollo local con Docker Compose

Este Compose incluye directamente el Compose fuente de Keycloak y levanta dos Postgres separados, Keycloak con el realm versionado,
el backend FastAPI en modo `--reload` y el frontend Astro con hot reload.

```sh
cp .env.dev.example .env
docker compose -f docker-compose.dev.yml up
```

Servicios:

- Frontend: <http://localhost:4321>
- Backend: <http://localhost:8000/health>
- Keycloak: <http://localhost:8080>

La primera vez, ejecuta las migraciones desde el contenedor del backend:

```sh
docker compose -f docker-compose.dev.yml exec backend uv run alembic upgrade head
```

Para detener y borrar también los datos locales:

```sh
docker compose -f docker-compose.dev.yml down -v
```

`KEYCLOAK_ISSUER_URL` es siempre el issuer público (`localhost`), porque debe
coincidir con el claim `iss` de los tokens. `KEYCLOAK_JWKS_BASE_URL` es la URL
interna (`keycloak`) que usa el backend sólo para descargar las llaves JWKS.
El frontend mantiene la misma separación: `FRONTEND_KEYCLOAK_ISSUER_URL` para
sus llamadas server-side y `KEYCLOAK_PUBLIC_ISSUER_URL` para redirects del
navegador. Fuera de Docker, `KEYCLOAK_JWKS_BASE_URL` puede omitirse y JWKS usa
`KEYCLOAK_ISSUER_URL` como fallback. Los secretos del archivo de ejemplo son
únicamente para desarrollo.

El flujo de login OAuth completo quedó verificado de punta a punta a través de
este Compose —redirect, login, callback y sesión—, no solamente mediante
healthchecks.
