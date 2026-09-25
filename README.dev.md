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

## Publicar detrás del reverse proxy compartido

El modo local anterior sigue siendo el predeterminado: no requiere cambios en
`.env`, y el frontend y Keycloak continúan en `/`, en `localhost:4321` y
`localhost:8080` (o el puerto local definido en `KEYCLOAK_PORT`). Para publicar
detrás del proxy con los prefijos preservados, agrega estas variables a `.env`
y usa también el overlay `docker-compose.public.yml`:

```dotenv
PUBLIC_BASE_PATH=/speech-dashboard
DASHBOARD_URL=https://agents-dev.hugosantiago.dev/speech-dashboard
KEYCLOAK_PUBLIC_ISSUER_URL=https://agents-dev.hugosantiago.dev/speech-dashboard-auth/realms/speech
KEYCLOAK_ISSUER_URL=https://agents-dev.hugosantiago.dev/speech-dashboard-auth/realms/speech
KC_HOSTNAME=https://agents-dev.hugosantiago.dev/speech-dashboard-auth
KC_HTTP_RELATIVE_PATH=/speech-dashboard-auth
KC_PROXY_HEADERS=xforwarded
FRONTEND_KEYCLOAK_ISSUER_URL=http://keycloak:8080/realms/speech
KEYCLOAK_JWKS_BASE_URL=http://keycloak:8080/realms/speech
```

Inicia la pila con ambos archivos:

```sh
docker compose -f docker-compose.dev.yml -f docker-compose.public.yml up
```

Recrea los servicios después de cambiar el entorno. `KEYCLOAK_PUBLIC_ISSUER_URL` es el issuer usado en redirects del
navegador y por el backend para validar el claim `iss`; debe coincidir con el
issuer que Keycloak publica. `FRONTEND_KEYCLOAK_ISSUER_URL` se mantiene como
`http://keycloak:8080/realms/speech`, porque es la dirección interna usada para
intercambio de tokens. `KEYCLOAK_JWKS_BASE_URL` también permanece en
`http://keycloak:8080/realms/speech` para que el backend descargue JWKS por la
red interna. `KC_PROXY_HEADERS=xforwarded` hace que Keycloak respete los
encabezados reenviados por Caddy; ese proxy conserva el prefijo y Keycloak lo
sirve desde `KC_HTTP_RELATIVE_PATH`.
