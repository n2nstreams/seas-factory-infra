# AGENTS Guidelines for This Repository

1. Use the Development Server, not npm run build
Always use npm run dev (or pnpm dev, yarn dev, etc.) while iterating on the application. This starts Next.js in development mode with hot-reload enabled.
Do not run npm run build inside the agent session. Running the production build command switches the .next folder to production assets which disables hot reload and can leave the development server in an inconsistent state. If a production build is required, do it outside of the interactive agent workflow.

2. Keep Dependencies in Sync
If you add or update dependencies remember to:
Update the appropriate lockfile (package-lock.json, pnpm-lock.yaml, yarn.lock).
Re-start the development server so that Next.js picks up the changes.

3. Coding Conventions
Prefer TypeScript (.tsx/.ts) for new components and utilities.
Co-locate component-specific styles in the same folder as the component when practical.

4. Useful Commands Recap
Command Purpose
npm run dev: Start the Next.js dev server with HMR.
npm run lint: Run ESLint checks.
npm run test: Execute the test suite (if present).
npm run build: Production build – do not run during agent sessions
