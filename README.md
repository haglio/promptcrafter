# PromptCrafter

A local-only Vite + React + TypeScript prototype for building positive and negative prompts from ordered controls.

## Stack

- Vite + React + TypeScript
- Vitest + Testing Library
- Config-driven prompt schema in `src/lib/schema.ts`

## Run locally

```bash
npm install
npm run dev
```

## Test

```bash
npm test
```

## Notes

- The prompt logic is schema-driven, so the random monster demo can be swapped for your real prompt taxonomy.
- Textareas stay bound to generated output until you flip **Unbind**.
- Every section and control has a 1-5 weight slider.
- Nested submenus are demonstrated under `Appendages > Wings`.
- Textareas are vertically resizable for more room.
