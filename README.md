# First Try

A starter Next.js (App Router + TypeScript) project with an accompanying Express server. ESLint and Prettier are configured for consistent formatting.

## Getting started

1. Install dependencies (requires npm access):

```bash
npm install
```

2. Copy the environment template and customize values:

```bash
cp .env.example .env
```

3. Run the Next.js dev server:

```bash
npm run dev
```

4. In a separate terminal, start the Express server:

```bash
npm run server
```

The Express server reads `DB_URL` and `STORAGE_PATH` from `.env` and exposes a simple `/health` endpoint.

## Scripts
- `npm run dev` – start the Next.js development server.
- `npm run build` – build the Next.js app for production.
- `npm run start` – run the built Next.js app.
- `npm run lint` – lint the project with ESLint.
- `npm run server` – run the standalone Express server.

## Environment variables

See `.env.example` for required variables:
- `PORT` – port for the Express server (defaults to 4000).
- `DB_URL` – database connection string.
- `STORAGE_PATH` – path to on-disk storage used by the server.
