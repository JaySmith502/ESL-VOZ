# Data Gaps — ESL-voice corpus

Generated 2026-06-13. Items from the resource manifest that were **not** downloaded
in this pass, and why. Each entry includes the manifest `id` and a suggested follow-up.

---

## Placeholder / unverifiable URLs

### `ky_elps_framework` — Kentucky ELPS Instructional Framework
- **Reason:** `download_url` in the manifest is a literal placeholder
  (`docs.google.com/spreadsheets/d/e/2PACX-1vS.../pub?output=pdf`).
- **Landing page:** https://education.ky.gov/curriculum/standards/kyacadstand/Pages/English-Language-Proficiency-(ELP)-Standards.aspx
- **Action needed:** Visit landing page manually, locate the current Google Sheet
  "Publish to web" URL, then either:
  - download as XLSX: `…/pub?output=xlsx`
  - download as PDF:   `…/pub?output=pdf`
  Replace placeholder in manifest and re-run.

---

## Paywalled research papers (abstracts only — to be captured separately if needed)

### `research_learning_paths` — Knowledge Map Mining for English Learning (Nguyen 2024)
- **DOI / URL:** https://link.springer.com/article/10.1007/s11042-024-18765-8
- **Reason:** Springer paywall. No arXiv preprint located in this pass.
- **Action needed:** Check institutional access, or search Google Scholar for an
  author-hosted PDF (typically `.edu/~author/papers/...`). If unavailable, capture
  the abstract + key figures into `./research/nguyen_2024_knowledge_map.txt`.

### `research_spaced_repetition` — Vocabulary Retention (Karatas et al. 2025)
- **URL:** https://www.sciencedirect.com/science/article/pii/S2666920X24000123
- **Reason:** ScienceDirect article. The S2666920X prefix is the *Computers and
  Education: Artificial Intelligence* journal, which **is open access** — re-attempt
  via the "Download PDF" button on the article page (Firecrawl `firecrawl_scrape`
  with `parsers: ["pdf"]` against the PDF link should work in a follow-up pass).
- **Action needed:** Open article in browser, copy the direct `…/pii/…/pdfft?...`
  PDF URL, then `curl` it.

---

## Bulk crawls skipped per user direction (2026-06-13)

User chose "Skip bulk crawls entirely" — only the seed/landing pages were not
captured. To pick these up later, treat each as a small crawl job with a cap.

| id | Landing URL | Suggested cap |
|----|-------------|---------------|
| `mn_literacy_curriculum` | https://www.literacymn.org/educator-resources | ~30 PDFs by level |
| `pedal_curriculum` | https://www.gse.upenn.edu/elp/teacher-resources/pedal | all lesson PDFs (~20) |
| `colorin_colorado_bilingual` | https://www.colorincolorado.org/ | top 50 educator/vocab pages |
| `busy_teacher_worksheets` | https://busyteacher.org/classroom_activities-vocabulary-worksheets/ | first 100 worksheets, levels 0–3 |

Suggested approach: `firecrawl_map` to enumerate URLs, filter to PDF/level-appropriate
pages, then `firecrawl_scrape` with `parsers: ["pdf"]` per URL.

---

## Manifest URL corrections applied this pass

For traceability — the manifest's `download_url` values for these were wrong/stale;
the URLs below are what was actually used.

| id | Manifest URL | Used URL |
|----|--------------|----------|
| `mn_literacy_story_bank` | `…/story_bank_all_stories_updated_2024.pdf` (404) | `…/beginning_esl_story_bank.pdf` **and** `…/pre-beginning_esl_story_bank.pdf` (split into two files) |
| `jcps_lau_plan` | `…/JCPS%20Lau%20Plan%202021-2022.pdf` (404; old URL scheme) | KSBA Portal AttachmentID=872622 (2024-25 Phase Four English Learner Plan) |
| `wida_spanish_standards` | (none — extraction hint only) | `https://wida.wisc.edu/sites/default/files/resource/MarcoDALE.pdf` |
| `la_casita_center` | `/programs` (404) | Site root `/` (no `/programs` route exists on current Wix site) |

Update manifest `download_url` fields to these working URLs to avoid re-discovery
on next run.

---

## Pass 2 additions (2026-06-14) — Tier 1/2/3 expansion

Items not in the original manifest but added per user request to flesh out an
"effective ESL brain". Files landed; minor gaps below.

### Pass 2 minor gaps

| Item | Status | Notes |
|------|--------|-------|
| WIDA Can-Do Descriptors, Grade K | **MISSING** | Tried `CanDo-KeyUses-Gr-K.pdf` and `CanDo-KeyUses-Gr-K-12.pdf` on wida.wisc.edu — both 404. Likely behind login (WIDA Secure Portal). Grades 1, 2-3, 4-5, 6-8, 9-12 ✓ — K is the only missing band. |
| Hamline pragmatics paper | **SKIPPED** | digitalcommons.hamline.edu returned HTTP 202 (queue/captcha) on retry. NCOLCTL pragmatics PDF (4.2 MB) covers the same speech-acts framework — redundant. |
| Krashen *Principles and Practice* full book | **REPLACED** | sdkrashen.com DNS unreachable. Substituted with the ESC1 Krashen theory summary PDF, which covers the 5 hypotheses with the same depth needed for a runtime primer. |
| NGSL FEL (Fitness English List), Spoken, New Dolch, Graded Reader, Medical Oral | **DEFERRED** | Specialized SP-lists on newgeneralservicelist.com. Not core for adult ESL voice — add later if learner population shifts toward a specific domain. |

### Pass 2 corpus additions — categorical summary

- **CEFR** (`cefr/`): Companion Volume 2020 (EN + ES PDFs).
- **WIDA Can-Do** (`standards/wida_cando/`): Grade-band descriptor PDFs (1, 2-3, 4-5, 6-8, 9-12).
- **Frequency lists** (`frequency/`): NGSL 1.2, NAWL 1.2, BSL 1.2, TSL 1.2 (CSV + XLSX with definitions).
- **Pronunciation** (`pronunciation/`): CMU Pronouncing Dict + phoneme set + curated minimal-pairs index.
- **Pedagogy** (`pedagogy/`): Krashen summary, SIOP (8 components + WWC report), Translanguaging (CAL + García + Hwb classroom strategies), pragmatics (NCOLCTL speech acts), plus compiled markdown primers (SLA, pragmatics inventory, lesson templates).
- **Reference** (`reference/`): Bloom's verbs/stems (3 PDFs), DOK (Ohio flip chart + Webb wheel), Bloom×CEFR matrix.
- **Bilingual** (`bilingual/`): 2 Spanish L1 interference papers + transfer cheat sheet.
- **Adult ESL** (`adult_esl/`): CASAS teacher handbook, USCIS 100 civics questions.

