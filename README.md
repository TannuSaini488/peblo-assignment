# Peblo TV Mini

A small, production-minded content platform built for the Peblo TV Mini take-home challenge.

## Architecture

The platform is composed of four main parts:

1. **Backend API**: A FastAPI service connected to a PostgreSQL database. It handles CRUD for shows, seasons, episodes, artwork validation, and publishing the catalogue. Uses SQLAlchemy (async) and Alembic for migrations.
2. **Internal CMS**: A React + TypeScript (Vite) frontend for editors and admins to manage the content catalogue. Includes artwork uploading, validation reports, and a publish button.
3. **Publishing Pipeline**: An atomic job in the backend that pulls database state, validates it, collapses language variants for the same content group, and generates a deterministic `catalogue.json` payload which is then written to a storage abstraction.
4. **Viewer UI**: A React + TypeScript (Vite) frontend for the end user. It consumes *only* the published `catalogue.json` payload and renders a Netflix-style UI.

## How to run

Requirements: Docker, Docker Compose, Node.js (for local frontend dev, though can be containerized).

```bash
# 1. Start the API and Database in Docker
docker-compose up -d

# The API container automatically runs migrations and the seed loader on startup.

# 2. Run the CMS Frontend
cd cms
npm install
npm run dev

# 3. Run the Viewer Frontend
cd viewer
npm install
npm run dev
```

### Running Tests

```bash
cd backend
python -m pytest tests/
```

## Decisions and Trade-offs

### 1. How publishing is atomic and what happens if the process dies mid-publish.
The publishing process writes the newly generated catalogue JSON to a temporary file (`catalogue.json.tmp.<uuid>`) on the storage layer. Only after the write succeeds is the temporary file atomically swapped into place as the final `catalogue.json` using OS-level atomic replace operations (e.g. `os.replace` locally, or consistent `PutObject` for S3/R2). 
If the process dies mid-publish, the temporary file is abandoned, and the live `catalogue.json` remains untouched. The viewer will simply continue seeing the old catalogue, preventing partially written state from ever being observed.

### 2. How storage abstraction allows migration from local storage to Cloudflare R2.
The storage layer is hidden behind a `StorageBackend` interface in `backend/app/storage/base.py` which defines standard operations like `put()`, `get()`, `delete()`, `get_url()`, and `put_atomic()`. 
Local development uses the `LocalStorageBackend` implementation which saves files to disk, while production would instantiate the `R2StorageBackend`. Business logic (like artwork upload or publishing) depends only on the interface, meaning zero changes are required to migrate to R2—only the injected implementation instance changes based on environment variables.

### 3. How search works, where it stops scaling, and what would come next.
Search is currently implemented as an API endpoint (`GET /catalog/search`) that reads the pre-published `catalogue.json` object and performs an in-memory string-matching filter across titles, categories, and languages. 
This works well for small catalogues (a few megabytes in size) because the JSON can be cached in memory and iterated over very quickly.
It stops scaling when the catalogue becomes too large to parse and search in memory efficiently (e.g., hundreds of megabytes). At that scale, search would move to a dedicated search index engine like Elasticsearch, Algolia, or Meilisearch, which would be updated asynchronously during the publish pipeline instead of iterating a JSON file on the fly.

### 4. Why a pre-published catalogue is served instead of querying the DB on every viewer request, and where that choice has drawbacks.
Serving a pre-published catalogue creates a hard boundary between the admin system and the public viewers, allowing the viewer API to operate essentially as static file delivery (from R2/CDN). This is incredibly fast, infinitely scalable, resilient (if DB goes down, viewers aren't affected), and reduces load on the primary PostgreSQL database.
The drawback is that changes aren't instantly live; editors must click "Publish". There's also no personalization (every user gets the same catalogue) and the file size grows linearly with content volume, eventually requiring pagination or sharding of the catalogue payload.

### 5. What was intentionally left out and why.
- **Actual S3/R2 wiring**: Stubbed out, because configuring live credentials for the evaluation environment wasn't practical, but the abstraction is fully formed.
- **Image Resizing/Processing**: We validate dimensions strictly rather than auto-cropping. The prompt specifies validation and returning human-readable errors. Adding an image processing pipeline (e.g., ImageMagick) would add unnecessary complexity for a simple API challenge.
- **JWT Refresh Tokens**: Standard JWT access tokens are implemented. Refresh tokens add a layer of session state that was deemed overkill for this specific take-home.

### 6. Which AI tools were used and where their output was accepted or rejected.
- Claude / Gemini were used as an agentic coding assistant to scaffold the boilerplate for the FastAPI application, React Router structure, and some ORM classes based on the provided schema. 
- AI outputs that suggested over-engineered solutions (like adding Redis for caching or Kafka for the publish pipeline) were explicitly rejected to adhere to the rule: "Do not over-engineer prematurely."
- The atomic publish logic and specific `seed_shows.json` anomalies parsing were manually verified to ensure they met the strict criteria described in `reference.json`.

## Time Spent
- **Foundation & Infrastructure**: 1 hour
- **Data Models & Backend CRUD**: 1.5 hours
- **Publishing Pipeline & Validation**: 2 hours
- **CMS Frontend**: 1.5 hours
- **Viewer Frontend**: 1 hour
- **Documentation & Polish**: 0.5 hours
- **Total**: ~7.5 hours
