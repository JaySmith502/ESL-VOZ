# ESL-voice Data Corpus

Last updated: 2026-06-14. 48 files, ~50 MB. Free/open sources only.

This directory holds the offline knowledge corpus for the ESL-voice tutor. Files
are organized by *role in the runtime*, not by source.

## Layout

```
data/
├── standards/        WIDA ELD framework + Can-Do descriptors (US K-12 standards)
│   ├── wida_eld_framework_2020.pdf
│   ├── wida_spanish_standards.pdf     (Marco DALE)
│   └── wida_cando/                    (per-grade-band can-do PDFs, Grades 1-12)
├── cefr/             CEFR Companion Volume 2020 (EN + ES)
├── frequency/        NGSL, NAWL, BSL, TSL — corpus-based word lists
├── pronunciation/    CMU dict + minimal pairs index
├── pedagogy/         SLA primer, Krashen, SIOP, translanguaging, pragmatics,
│                     lesson templates
├── reference/        Bloom's taxonomy stems + Bloom×CEFR matrix + DOK
├── bilingual/        Spanish L1 transfer materials
├── adult_esl/        Adult-learner content + standards
│   ├── mn_story_bank_*.pdf           (reading passages, low levels)
│   ├── casas_esl_handbook.pdf        (CASAS competencies framework)
│   └── uscis_100_civics_questions.pdf
├── local/            JCPS + La Casita (Louisville context)
├── research/         (placeholder — see gaps.md for what's pending)
├── gaps.md           What's NOT here and why
└── README.md         this file
```

## How the runtime should use each tier

| Tutor question at runtime | Pull from |
|----------------------------|-----------|
| What's the learner's level? | `cefr/`, `standards/wida_cando/` |
| What vocabulary should I introduce next? | `frequency/NGSL_*` (general), `frequency/NAWL_*` (academic) |
| What grammar can I expect at this level? | English Grammar Profile (see gaps — open-access via englishprofile.org) + `cefr/` descriptors |
| How do I pronounce this word? | `pronunciation/cmudict.txt` (IPA via CMU phones) |
| What pronunciation contrast should I drill? | `pronunciation/minimal_pairs_index.md` |
| What error is the learner likely to make? | `bilingual/spanish_l1_transfer_cheat_sheet.md` (Spanish L1) |
| How should I correct? | `pedagogy/sla_primer.md` § Error-correction taxonomy |
| What lesson structure fits? | `pedagogy/lesson_templates.md` |
| How do I phrase this socially? | `pedagogy/pragmatics_inventory.md` |
| What question should I ask next? | `reference/blooms_x_cefr_question_stems.md` |
| Adult-ESL US standards alignment | `adult_esl/casas_esl_handbook.pdf` |
| Local context / scenarios | `local/la_casita.txt`, `local/jcps_lau_plan_2024_2025.pdf` |
| Citizenship-track learner | `adult_esl/uscis_100_civics_questions.pdf` |
| Sheltered (content+language) | `pedagogy/siop_*` |
| Bilingual/translanguaging stance | `pedagogy/translanguaging_*` |

## What's not here (see `gaps.md`)

- Kentucky ELPS framework (placeholder URL in original manifest)
- WIDA Can-Do K (404 — likely behind WIDA secure portal)
- 2 paywalled research papers
- 4 bulk crawls deferred per user direction (MN curriculum, PEDAL, Colorin
  Colorado, BusyTeacher)
- English Grammar Profile direct CSV (interactive search interface only —
  englishprofile.org)
