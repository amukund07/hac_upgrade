<<<<<<< HEAD
# Hackostic

Production-ready MERN restructuring of the existing learning experience.

## Structure

- `frontend/` - React + TypeScript UI, animations, routing, and Axios API clients
- `backend/` - Node.js + Express.js + MongoDB + Mongoose + JWT API

## Frontend

The UI stays intact and now talks to the backend through REST services.

Key setup:

- `frontend/src/lib/apiClient.ts`
- `frontend/src/context/AuthContext.tsx`
- `frontend/src/services/*.ts`

## Backend

The backend exposes auth, modules, lessons, quizzes, progress, leaderboard, and achievements APIs.

Key setup:

- `backend/src/app.ts`
- `backend/server.ts`
- `backend/src/models/*`

## Local Development

1. Install dependencies in the repo root so the frontend and backend workspaces are linked.
2. Set environment variables from `frontend/.env.example` and `backend/.env.example`.
3. Run `npm run dev:frontend` and `npm run dev:backend` from the root.

## Notes

- Supabase is removed from the frontend service layer.
- Existing pages, layout, animations, and routing are preserved.
- The backend seeds demo data on first start so the UI has content immediately.
=======
# hac_upgrade
upgrading 
>>>>>>> 9c05c89d0178bfdc17e4ff05ac60d9faead6095d
