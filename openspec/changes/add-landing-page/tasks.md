## 1. Astro project scaffolding

- [x] 1.1 Initialize the Astro project at `frontend/` (default template, TypeScript); verify `npm run dev` starts and serves a page locally.
- [x] 1.2 Add basic project conventions (a `components/` and `pages/` layout, a shared `Layout.astro`); verify the dev server renders a page using the shared layout with no errors.

## 2. Landing page content

- [x] 2.1 Re-read `speech-app`'s current `README.md` (the sibling repo) to confirm the exact feature list and language before writing copy; verify the drafted feature section only makes claims present there.
- [x] 2.2 Build the hero section (product name, one-line value proposition, primary CTA); verify it renders correctly at both desktop and ~400px-wide viewport.
- [x] 2.3 Build the feature section from the confirmed feature list; verify each bullet traces back to a specific line in `speech-app`'s README.
- [x] 2.4 Build the pricing section with static copy for each plan tier (name, price, word-limit-per-period) matching the `add-plans-billing` catalog's initial seeded plans; verify the displayed limits match the seeded `plans` table values at the time of writing.
- [x] 2.5 Build the CTA section: a download link/button for speech-app and a sign-up/login link pointing at the Speech realm's hosted login page; verify both links resolve to the intended destinations.

## 3. Responsive and cross-check

- [x] 3.1 Verify the full page at both a desktop width and a ~400px phone width with no horizontal scrolling and no broken layout.
- [x] 3.2 Verify the page builds cleanly for production (`npm run build`) with no errors or broken links.
