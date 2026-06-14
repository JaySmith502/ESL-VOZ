# Bloom's Revised Taxonomy × CEFR — Question Stem Matrix

The Bloom level controls **cognitive demand** (what kind of thinking is required).
The CEFR level controls **linguistic demand** (how much language is required to
express the thinking). A good ESL voice tutor matrix-multiplies them: the same
"Evaluate" question lands differently at A1 vs B2.

This sheet gives one stem per cell so the tutor has a vocabulary to draw from.
For fuller Bloom verb lists see `blooms_verbs_and_stems_utica.pdf` and
`blooms_revised_landmark.pdf` in this directory; for fuller CEFR descriptors see
`../cefr/cefr_companion_volume_2020_en.pdf`.

---

## Matrix (Bloom rows × CEFR cols)

|                    | **A1 (Beginner)** | **A2 (Elementary)** | **B1 (Intermediate)** | **B2 (Upper-int.)** | **C1 (Advanced)** |
|--------------------|-------------------|---------------------|------------------------|---------------------|--------------------|
| **1. Remember**    | "What is this?" (point) | "What did she say?" | "What happened first?" | "What were the main steps?" | "Summarize the key claims." |
| **2. Understand**  | "Is it big or small?" | "Why is she sad?" | "Can you tell me in your own words?" | "What does the author mean by X?" | "Paraphrase the argument." |
| **3. Apply**       | "Show me 'open'." | "How do you ask for water?" | "How would you use this word in a sentence?" | "How would you handle this at work?" | "Apply this rule to a new context." |
| **4. Analyze**     | "Same or different?" | "Why is this group together?" | "What's the difference between A and B?" | "What pattern do you notice?" | "Analyze the assumptions behind X." |
| **5. Evaluate**    | "Good or bad?" | "Do you like it? Why?" | "Was it a good choice? Why?" | "Which option is better and why?" | "Critique the strongest counter-argument." |
| **6. Create**      | "Draw it." | "Tell me a short story." | "What would you do differently?" | "Write a new ending." | "Propose an original solution." |

---

## How to use this in the tutor runtime

1. **Pick a CEFR column first** — based on the learner's assessed level.
2. **Pick a Bloom row second** — based on the lesson goal *or* to vary cognitive demand
   across a session (don't camp on row 1).
3. **Customize the stem** with the actual lesson content (a story, a workplace scene,
   a citizenship topic).

### Cross-level scaffolding pattern

Same Bloom-3 (Apply) target, three CEFR scaffolds in sequence:
- A1 → "Point to the doctor."
- A2 → "What do you say to the doctor?"
- B1 → "Tell the doctor what's wrong and ask for help."

This is the **language-level scaffold for a constant cognitive target** — exactly
what good ESL teachers do implicitly.

### Cross-Bloom drilling pattern

Same CEFR level (B1), climbing Bloom levels in one mini-arc:
1. Remember: "What did the character do?"
2. Understand: "Why did he do it?"
3. Apply: "Have you ever done something like that?"
4. Analyze: "What made him decide?"
5. Evaluate: "Was it the right choice?"
6. Create: "What would you do instead?"

This pattern doubles as an exit ticket — if the learner stays fluent across all six
turns at one CEFR level, they're probably ready to nudge up half a level on the next
session.

---

## When Bloom's helps and when it doesn't

**Helps for:** generating questions, varying cognitive demand within a session,
auditing lesson plans for higher-order thinking.

**Doesn't help for:** vocabulary sequencing (use NGSL), grammar progression (use
English Grammar Profile), pronunciation (use minimal pairs + CMU dict), pragmatics
(use the pragmatics inventory). Bloom's is a **question-generation utility**, not a
theory of language acquisition. Pair it with the SLA primer (`sla_primer.md`).
