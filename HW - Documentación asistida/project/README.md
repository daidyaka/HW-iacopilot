# InternetWhisper — Documentación técnica asistida por GitHub Copilot

InternetWhisper es un chatbot de IA capaz de buscar, procesar y responder con información en tiempo real desde Internet. Este README fue redactado con la asistencia de GitHub Copilot para documentar su arquitectura, flujo de datos, dependencias, configuración y ejecución.

---

## 1. Descripción del Proyecto
- Objetivo: Proveer respuestas dinámicas basadas en fuentes online (búsqueda, scraping, consolidación y razonamiento) en tiempo real.
- Componentes principales:
  - Frontend (FastAPI/Streamlit o similar): interfaz ligera para interactuar con el chatbot.
  - Orchestrator (Python): coordina flujo, llamadas al LLM, búsqueda y scraping.
  - Scraper (Python): obtiene contenido web de fuentes externas de forma segura.
  - Redis: caché/cola para respuestas, sesiones o datos temporales.
- Deploy local: vía `docker-compose` o ejecución en entorno Python.

---

## 2. Explicación Técnica

### Arquitectura general
- `src/frontend`: expone endpoints y/o UI para consultas del usuario.
- `src/orchestrator`: núcleo del sistema; administra solicitudes, integra el modelo LLM, orquesta búsqueda (`search`), scraping (`scraper`) y memoria (`redis`).
- `src/scraper`: lógica para obtener y normalizar contenido HTML/JSON desde la web.
- `redis_data/`: persistencia del estado de Redis (volumen mapeado por Docker).
- `docker-compose.yml`: define servicios (frontend, orchestrator, scraper, redis) y redes internas.

### Flujo de datos
1. Usuario envía consulta desde el Frontend.
2. Orchestrator valida, decide estrategia (buscar, scrapear, recuperar memoria).
3. Módulos de `search` y `scraper` obtienen contenido; resultados se normalizan.
4. Orchestrator construye el prompt para el LLM, combina contexto + fuentes.
5. LLM genera la respuesta; se almacena en Redis (cache/estado) y retorna al Frontend.

### Dependencias principales
- Python 3.10+ (ver `pyproject.toml` y `requirements.txt` en cada servicio).
- FastAPI/Flask/Streamlit para HTTP/UI (según cada subservicio).
- Redis (almacenamiento en memoria + persistencia en `redis_data/`).
- Clientes HTTP (requests, httpx) y parsing (BeautifulSoup4/Playwright según necesidad).
- Integración LLM (OpenAI API u otro proveedor configurable por variables de entorno).

---

## 3. Variables de Entorno
Configura estas variables antes de ejecutar (puedes usar `.env` o variables del sistema):

- `LLM_PROVIDER`: proveedor del modelo (ej. `openai`).
- `LLM_MODEL`: nombre del modelo (ej. `gpt-4o-mini`).
- `LLM_API_KEY`: clave del proveedor LLM.
- `SEARCH_PROVIDER`: proveedor de búsqueda (ej. `serper`, `google`, `bing`).
- `SEARCH_API_KEY`: clave del proveedor de búsqueda si aplica.
- `REDIS_URL`: URL de Redis (ej. `redis://redis:6379/0` en Docker, `redis://localhost:6379/0` local).
- `ORCHESTRATOR_LOG_LEVEL`: nivel de log (ej. `INFO`, `DEBUG`).
- `SCRAPER_USER_AGENT`: UA para scraping responsable.
- `TIMEOUT_SECONDS`: tiempo máximo por consulta.

Ejemplo `.env` (local):
```
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
LLM_API_KEY=sk-xxxx
SEARCH_PROVIDER=google
SEARCH_API_KEY=your-search-key
REDIS_URL=redis://localhost:6379/0
ORCHESTRATOR_LOG_LEVEL=INFO
SCRAPER_USER_AGENT=InternetWhisper/1.0 (+https://example.org)
TIMEOUT_SECONDS=30
```

---

## 4. Ejecución Local

### Opción A: Docker Compose
Requisitos: Docker Desktop instalado y activo.

```bash
# En el directorio project/
docker-compose up --build
# Detener
# docker-compose down
```
- Frontend: expone el puerto definido en `docker-compose.yml`.
- Orchestrator/Scraper: levantados como servicios internos; Redis accesible en red de compose.

### Opción B: Entorno Python (sin Docker)
Requisitos: Python 3.10+, Redis en local.

```bash
# En project/src/orchestrator
python -m venv .venv
. .venv/Scripts/Activate.ps1   # Windows PowerShell
pip install -r requirements.txt
set REDIS_URL=redis://localhost:6379/0
set LLM_PROVIDER=openai
set LLM_MODEL=gpt-4o-mini
set LLM_API_KEY=sk-xxxx
python main.py
```

Para el Frontend:
```bash
# En project/src/frontend
python -m venv .venv
. .venv/Scripts/Activate.ps1
pip install -r requirements.txt
python main.py
```

---

## 5. Definición OpenAPI (v3.0)
La API del Orchestrator expone un endpoint para consultas. Adapta rutas si tu implementación difiere.

```yaml
openapi: 3.0.3
info:
  title: InternetWhisper Orchestrator API
  version: "1.0.0"
  description: API para consultas en tiempo real a InternetWhisper
servers:
  - url: http://localhost:8000
paths:
  /api/query:
    post:
      summary: Ejecuta una consulta y retorna respuesta enriquecida
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                question:
                  type: string
                  description: Pregunta del usuario
                max_results:
                  type: integer
                  default: 5
                enable_scrape:
                  type: boolean
                  default: true
                include_sources:
                  type: boolean
                  default: true
              required: [question]
      responses:
        '200':
          description: Respuesta generada por el LLM con fuentes
          content:
            application/json:
              schema:
                type: object
                properties:
                  answer:
                    type: string
                  sources:
                    type: array
                    items:
                      type: object
                      properties:
                        title:
                          type: string
                        url:
                          type: string
                        snippet:
                          type: string
                  metadata:
                    type: object
                    properties:
                      duration_ms:
                        type: integer
                      tokens_used:
                        type: integer
        '400':
          description: Petición inválida
        '500':
          description: Error interno
```

---

## 6. Ejemplos de Interacción

Ejemplo 1 — Consulta factual con fuentes:
```json
POST /api/query
{
  "question": "¿Cuál fue el último reporte de inflación en la UE?",
  "max_results": 3,
  "enable_scrape": true,
  "include_sources": true
}
```
Respuesta (resumen):
```json
{
  "answer": "La inflación interanual en la UE fue X% según Eurostat...",
  "sources": [
    {"title": "Eurostat - News release", "url": "https://ec.europa.eu/...", "snippet": "Annual inflation..."},
    {"title": "Reuters", "url": "https://www.reuters.com/...", "snippet": "EU inflation..."}
  ],
  "metadata": {"duration_ms": 2140, "tokens_used": 1320}
}
```

Ejemplo 2 — Pregunta de síntesis con razonamiento:
```json
{
  "question": "Compara previsiones de crecimiento 2026 de la OCDE y FMI y explica diferencias",
  "max_results": 4,
  "enable_scrape": true,
  "include_sources": true
}
```

---

## 7. Buenas Prácticas
- Respetar robots.txt y términos de uso de los sitios consultados.
- Limitar la frecuencia de scraping; usar `SCRAPER_USER_AGENT` y tiempos de espera.
- Cachear resultados frecuentes con Redis para reducir llamadas repetidas.
- Registrar trazas (`ORCHESTRATOR_LOG_LEVEL=DEBUG`) durante depuración.
- Manejar timeouts y reintentos para proveedores externos.

---

## 8. Internacionalización (ES/EN)

### Resumen en Español
InternetWhisper orquesta búsqueda, scraping y LLM para responder en tiempo real con fuentes verificables. Se ejecuta con Docker o directamente con Python, y utiliza Redis para cache/estado.

### Summary in English
InternetWhisper orchestrates search, scraping, and an LLM to answer in real time with verifiable sources. Run via Docker or Python; uses Redis for cache/state.

---

## 9. Uso de GitHub Copilot
- Se utilizaron sugerencias de Copilot para estructurar secciones, redactar el esquema OpenAPI y ejemplos de variables de entorno.
- Comandos útiles en VS Code: `/explain` para entender módulos, `/doc` para generar descripciones, `/fix` para ajustes.
- Consejo: Usa comentarios "Sugerencia Copilot:" para documentar contribuciones automáticas.

---

## 10. Licencia
Consulta `LICENSE` en el directorio `project/` para detalles.
