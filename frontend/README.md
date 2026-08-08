# ZivaStock Frontend

React + TypeScript + Material UI dashboard for the ZivaStock stocktake system.

## Features

- Dashboard with KPIs and session progress
- Stocktake session management
- Product and user lists with DataGrid
- Reports generation and export
- JWT authentication with automatic token refresh
- Responsive layout with sidebar navigation

## Tech Stack

- React 18
- TypeScript
- Redux Toolkit
- Material UI 5
- MUI X DataGrid
- Axios
- Vite

## Getting Started

1. Install dependencies

```bash
npm install
```

2. Configure the API URL (optional)

```bash
cp .env.example .env
```

Default backend URL is `http://localhost:8000`.

3. Start the development server

```bash
npm run dev
```

The app will be available at `http://localhost:5173`.

## Build

```bash
npm run build
```

## Lint

```bash
npm run lint
```

## Project Structure

```
frontend/
├── src/
│   ├── components/   # Layout and common UI components
│   ├── pages/        # Dashboard, Stocktake, Products, Users, Reports, Login
│   ├── services/     # API client
│   ├── store/        # Redux store and slices
│   ├── hooks/        # Typed Redux hooks
│   └── theme.ts      # Material UI theme
├── package.json
├── tsconfig.json
└── vite.config.ts
```
