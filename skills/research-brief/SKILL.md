---
name: research-brief
description: Produce a research, survey, retro-labeling, or analysis document as a markdown brief with a NanobananaPro infographic prepended at the top — both embedded for inline preview AND linked for full-size open. Use when the user asks for a research pass, framework survey, distribution analysis, audit, deck-clearing report, or any synthesis document that should be skimmable before drilling. Also use proactively when you are producing a multi-section analytical artifact (>500 words, structured findings, comparisons, or distributions) for the user to review.
---

# Research Brief

Standard shape for synthesis documents that the user will review by skimming first and drilling second. The brief is the prose; the infographic at the top encodes structure + key findings so the user can grasp the shape before reading.

## When to use

- The user asks for a research pass, survey, retro-labeling, distribution analysis, audit, deck-clearing report, or any multi-section synthesis.
- You are about to produce a >500-word analytical artifact with structured findings, comparisons, or distributions.
- The user says "make a brief", "draft a research doc", "summarize the landscape", "do a retro-pass", or similar.
- Proactive use: any time you would otherwise produce a long prose document with section headers and tables — convert it to a brief and add the infographic at the top.

## The required artifact shape

```
[infographic embed]
[infographic link — same target]

# Title

[brief lede: what this is, why it exists, what to take away]

## Sections with structured findings

[tables, distributions, comparisons — all INLINE in markdown, no JSON sidecars]

## Honest call / synthesis

[the takeaway; if the data doesn't support the hypothesis, say so]
```

## The image-tag-plus-link rule (non-negotiable)

The first two lines of the brief, before the title, MUST be:

```markdown
![Infographic summary of: <title>](./<basename>.infographic.png)
[Infographic summary of: <title>](./<basename>.infographic.png)
```

Why both:
- The `![...]` embed renders the image inline so the user sees it while skimming.
- The `[...]` link is clickable in Warp's markdown preview — clicking opens the image full-size so the user can zoom into infographic details that are unreadable at the embed scale.
- Without the link, the embed gives a small version with no zoom path — a known pain point.

## Workflow

### 1. Write the markdown brief first

Produce the brief at its final location (typically `docs/review-packets/<topic>/<NN>-<slug>.md` in the project, or wherever the user specifies). Do not generate the infographic before the prose is settled — the infographic encodes the prose.

Formatting rules:
- **INLINE all structured content.** Tables, distributions, code snippets, JSON schemas — render as markdown. Never link to a sidecar JSON file the user has to bounce to. The brief IS the rendered view.
- **Clickable file links.** Render local file paths as `[path](file:///abs/path)` markdown links, NOT as code-tag spans. The user reads in Warp's preview where code tags aren't clickable.
- **No emojis.**
- **Honest synthesis.** If the data contradicts the framing hypothesis, say so. Don't shape findings to fit the question.
- **Aim for skim-then-drill.** Front-load the takeaway; section headers should preview their findings.

### 2. Generate the infographic with NanobananaPro

Use Google's `gemini-3-pro-image-preview` model via the `@google/generative-ai` SDK. The model produces a single PNG from a prompt that includes the full document text.

#### Required: prompt structure

The prompt MUST include:
1. **The full document text** (truncate at ~15000 chars if needed, mark truncation).
2. **A framing paragraph** — what the document is and what the infographic should encode at a glance.
3. **Design constraints** (see "Design constraints" below).
4. **Instruction to use real numbers / labels from the document** — never invent values.

#### Design constraints (Ray's design north-star)

- **Landscape 16:9** so it fits at the top of a markdown file.
- **Warm color palette** — warm cream background, warm charcoal text, deeper accents. NOT dark mode. NOT corporate slick.
- **Title large at the top.**
- **Visual hierarchy reflects the document's actual structure** — sections, comparisons, distributions.
- **Real numbers and labels from the document only.** No inventions.
- **Diagram types as appropriate:** comparison tables, distribution bars, ladders, sankey-style flows, annotated stacks. Match the form to the content.
- **Clean sans-serif typography**, generous spacing, no clutter.
- **No emojis, no clipart.** Iconography only where it carries information.
- **Show the takeaway** — the reader should walk away with a single sentence in mind.

#### Implementation: the canonical script

Drop this into the project root or a `scratch/` folder as a `.ts` file, run with `tsx`, then delete. Requires `@google/generative-ai`, `dotenv`, `tsx`, and `GEMINI_API_KEY` in `.env`.

```typescript
import { readFileSync, writeFileSync } from 'fs';
import { resolve, basename, dirname } from 'path';
import { fileURLToPath } from 'url';
import { GoogleGenerativeAI } from '@google/generative-ai';
import 'dotenv/config';

const __dirname = dirname(fileURLToPath(import.meta.url));

const GEMINI_API_KEY = process.env.GEMINI_API_KEY;
if (!GEMINI_API_KEY) { console.error('GEMINI_API_KEY missing'); process.exit(1); }

const genAI = new GoogleGenerativeAI(GEMINI_API_KEY);
const model = genAI.getGenerativeModel({ model: 'gemini-3-pro-image-preview' });

// EDIT: one entry per brief to process
const FILES = [
  {
    path: resolve(__dirname, 'path/to/brief.md'),
    title: 'Brief Title Exactly As It Appears',
    framing: 'One paragraph describing what this brief is and what the infographic should encode at a glance. Reference the key findings, numbers, structural shape.',
  },
];

async function makeInfographic(file: typeof FILES[number]) {
  const md = readFileSync(file.path, 'utf-8');
  const trimmed = md.length > 15000 ? md.slice(0, 15000) + '\n[...truncated for prompt]' : md;
  const prompt = `Create a single landscape infographic (16:9) that visually summarizes this research document so a busy reader can grasp its structure and key findings at a glance — before reading the prose.

DOCUMENT TITLE: ${file.title}

FRAMING (the big picture the infographic should encode):
${file.framing}

FULL DOCUMENT TEXT (use this as ground truth for every claim, label, comparison, and number shown):
---
${trimmed}
---

DESIGN REQUIREMENTS:
- Landscape 16:9 layout, suitable for sticking at the top of a markdown file
- Title at the top, large and readable
- Visual hierarchy that reflects the document's actual structure (sections, comparisons, distributions)
- Use real numbers/percentages/labels from the document — never invent values
- Use diagrams, comparison tables, ladders, sankey-style flows, distribution bars, or annotated stacks as appropriate to the content
- Warm, comfortable, legible color palette (warm cream background, warm charcoal text, deeper accents) — NOT dark mode, NOT corporate slick
- Typography: clean sans-serif, generous spacing, no clutter
- No emojis, no clipart. Iconography ok only where it carries information
- Show the takeaway — what the reader should walk away believing

Generate the infographic now.`;

  console.log(`Generating: ${basename(file.path)}`);
  const response = await model.generateContent(prompt);
  const candidates = response.response.candidates;
  if (!candidates || candidates.length === 0) throw new Error('no candidates');
  let buf: Buffer | null = null;
  for (const part of candidates[0].content.parts) {
    if ((part as any).inlineData) { buf = Buffer.from((part as any).inlineData.data, 'base64'); break; }
  }
  if (!buf) throw new Error('no image data');

  const pngName = basename(file.path).replace(/\.md$/, '.infographic.png');
  const pngPath = resolve(dirname(file.path), pngName);
  writeFileSync(pngPath, buf);
  console.log(`Saved: ${pngPath}`);

  const existing = readFileSync(file.path, 'utf-8');
  if (existing.startsWith('![')) { console.log('Image tag already present, skipping'); return; }
  const header = `![Infographic summary of: ${file.title}](./${pngName})\n[Infographic summary of: ${file.title}](./${pngName})\n\n`;
  writeFileSync(file.path, header + existing);
  console.log(`Prepended embed+link to ${file.path}`);
}

(async () => {
  for (const f of FILES) {
    try { await makeInfographic(f); await new Promise(r => setTimeout(r, 2000)); }
    catch (e) { console.error(`Failed for ${f.path}:`, e); }
  }
})();
```

### 3. Prepend the embed + link

The script handles this automatically. If you regenerate, the script detects the existing image tag and skips the prepend so you don't get duplicates. If the brief title changes, delete the first two lines manually and re-run.

### 4. Verify by reading the image back

Use the Read tool on the generated PNG to confirm the infographic actually encodes the brief's structure and uses real numbers — not invented ones. If the model hallucinated numbers or inverted a finding, regenerate with a sharper framing paragraph.

### 5. Clean up

Delete the scratch script after the infographic(s) are generated. The brief and the PNG live with the project; the script does not.

## Decisions you make on the user's behalf

The brief-plus-infographic pattern is itself a decision package — the user is asking you to make many small calls so they can spend attention on the takeaway. Make these calls and state them in the response:

- **Where the brief lives** (default: `docs/review-packets/<topic>/<NN>-<slug>.md`).
- **The framing paragraph** for the infographic prompt — this is the load-bearing prompt-engineering choice. State it explicitly in the chat so the user can adjust.
- **Which diagram types** suit the content (distribution → bars; comparison → table; ladder → vertical stack; flow → arrows).
- **How many briefs** to produce in one batch — if the user asks for "research on X", consider whether it splits cleanly into 2-3 briefs (e.g., "field survey" + "our data") rather than one giant doc.

## When to invoke

- User asks: "do a research pass", "survey the landscape", "retro-label", "audit", "deck-clearing report", "synthesis doc", "research brief", "infographic for this doc".
- Proactively: when you are about to produce a >500-word analytical artifact with tables/comparisons/distributions for review.

## Counter-cases (do NOT invoke)

- User wants a PR description, commit message, GitHub issue body — those are different artifacts.
- User wants code review, plan, implementation spec — use other skills.
- User wants a one-line answer — don't inflate it into a brief.
- The artifact is not for human review (e.g., a CI report) — no need for the infographic overhead.

## Output to the user

After the brief and infographic land, the message back to the user should include:
- Clickable links to each brief (`[path](file:///abs/path)` — NOT code tags).
- A one-sentence summary of what the infographic encodes ("Phase 1 → encodes the three-layer frame, the SOTA ladder, the production-framework comparison, and the +54% Anthropic empirical anchor").
- The next decision the user could make from this artifact.
