# Section Manifest Review: notes_interaction

You are checking whether this PDF was chunked into semantically useful RAG sections.
The deterministic extractor is intentionally simple and can be fooled by PDF formatting.

## Task

- Read the section list and boundary snippets below.
- Decide whether each chunk is coherent enough for retrieval.
- Prefer preserving the manifest when boundaries are acceptable.
- If a boundary is wrong, edit the target manifest JSON directly.
- Only edit `title`, `level`, `line_start`, and `line_end` unless a section must be added or removed.
- Keep line ranges contiguous, non-overlapping, and within the extracted line numbers.
- Keep the source PDF unchanged.

## Target

- source_pdf: `docs/course-notes/Course Notes 7 — Interaction - FAB.pdf`
- doc_id: `notes_interaction`
- title: Interaction
- target_manifest: `.rag/manifests/notes_interaction.sections.json`
- source_kind: existing manifest
- source_sha_status: fresh
- extracted_lines: 376
- current_sections: 11

## Review Checklist

- Does every top-level/subsection heading start a sensible chunk?
- Are tiny heading-only chunks merged with their following explanatory section when useful?
- Are very large sections split at meaningful internal headings or topic turns?
- Do start/end snippets show missing text, duplicated text, or page-order extraction problems?
- Are page ranges and titles still accurate after any edits?

## Commands

```bash
uv run python scripts/rag.py review-sections --doc-id notes_interaction --write
uv run python scripts/rag.py index
```

## Current Sections

### 001. Introduction

- level: 1; pages: 1-2; lines: 0-36; words: 448

start sample:
- `L0000 p1.0: Course Notes — SESSION 7`
- `L0001 p1.1: INTERACTION`
- `L0002 p1.3: 1. Introduction`

end sample:
- `L0033 p1.39: forth — an entire system able to interact with the physical and cultural world. In this session, we`
- `L0034 p2.0: will explore how we might understand and design AI systems and organizations based on`
- `L0035 p2.1: foregrounding such interactions, and not just symbol manipulations.`

start boundary context:
- `L0000 p1.0: Course Notes — SESSION 7`
- `L0001 p1.1: INTERACTION`
- `L0002 p1.3: 1. Introduction`

end boundary context:
- `L0034 p2.0: will explore how we might understand and design AI systems and organizations based on`
- `L0035 p2.1: foregrounding such interactions, and not just symbol manipulations.`
- `L0036 p2.4: 2. Defamiliarizing our language for talking about AI`
- `L0037 p2.5: The basic AI idea described above seems straightforward enough: focusing on interaction with`
- `L0038 p2.6: the external world, not just internal symbol manipulation. Yet researchers of interactionism have`

### 002. Defamiliarizing our language for talking about AI

- level: 1; pages: 2-2; lines: 36-53; words: 229

start sample:
- `L0036 p2.4: 2. Defamiliarizing our language for talking about AI`
- `L0037 p2.5: The basic AI idea described above seems straightforward enough: focusing on interaction with`
- `L0038 p2.6: the external world, not just internal symbol manipulation. Yet researchers of interactionism have`

end sample:
- `L0050 p2.19: inadvertently been using to talk about intelligence. We explore how to do such defamiliarization`
- `L0051 p2.20: in terms of our Cartesian metaphors of action, our stories about learning, and concepts of`
- `L0052 p2.21: complexity in organizations and other systems.`

start boundary context:
- `L0034 p2.0: will explore how we might understand and design AI systems and organizations based on`
- `L0035 p2.1: foregrounding such interactions, and not just symbol manipulations.`
- `L0036 p2.4: 2. Defamiliarizing our language for talking about AI`
- `L0037 p2.5: The basic AI idea described above seems straightforward enough: focusing on interaction with`
- `L0038 p2.6: the external world, not just internal symbol manipulation. Yet researchers of interactionism have`

end boundary context:
- `L0051 p2.20: in terms of our Cartesian metaphors of action, our stories about learning, and concepts of`
- `L0052 p2.21: complexity in organizations and other systems.`
- `L0053 p2.23: 2.1 Agre’s critical technical practice: defamiliarizing Cartesian metaphors in AI`
- `L0054 p2.24: In pioneering work in the 1980s at MIT, the AI scholar Phil Agre introduced a method for`
- `L0055 p2.25: surfacing what he saw as the narrow yet vague language of AI ideas based on symbol`

### 003. Agre’s critical technical practice: defamiliarizing Cartesian metaphors in AI

- level: 2; pages: 2-3; lines: 53-84; words: 415

start sample:
- `L0053 p2.23: 2.1 Agre’s critical technical practice: defamiliarizing Cartesian metaphors in AI`
- `L0054 p2.24: In pioneering work in the 1980s at MIT, the AI scholar Phil Agre introduced a method for`
- `L0055 p2.25: surfacing what he saw as the narrow yet vague language of AI ideas based on symbol`

end sample:
- `L0081 p3.13: self-fulfilling prophecy: we may start thinking about search, planning (or learning or knowledge)`
- `L0082 p3.14: as what happens symbolically inside of a computer. According to Agre, this will unnecessarily`
- `L0083 p3.15: constrain our design of both AI systems and organizations.`

start boundary context:
- `L0051 p2.20: in terms of our Cartesian metaphors of action, our stories about learning, and concepts of`
- `L0052 p2.21: complexity in organizations and other systems.`
- `L0053 p2.23: 2.1 Agre’s critical technical practice: defamiliarizing Cartesian metaphors in AI`
- `L0054 p2.24: In pioneering work in the 1980s at MIT, the AI scholar Phil Agre introduced a method for`
- `L0055 p2.25: surfacing what he saw as the narrow yet vague language of AI ideas based on symbol`

end boundary context:
- `L0082 p3.14: as what happens symbolically inside of a computer. According to Agre, this will unnecessarily`
- `L0083 p3.15: constrain our design of both AI systems and organizations.`
- `L0084 p3.17: 2.2 Brooks’ “creature hypothesis”: defamiliarizing Cartesian stories about learning`
- `L0085 p3.18: The AI field has often set the benchmarks for intelligent learning in terms of individual`
- `L0086 p3.19: Cartesian-style tasks for manipulating symbols. An early benchmark for AI was to learn to play`

### 004. Brooks’ “creature hypothesis”: defamiliarizing Cartesian stories about learning

- level: 2; pages: 3-4; lines: 84-114; words: 400

start sample:
- `L0084 p3.17: 2.2 Brooks’ “creature hypothesis”: defamiliarizing Cartesian stories about learning`
- `L0085 p3.18: The AI field has often set the benchmarks for intelligent learning in terms of individual`
- `L0086 p3.19: Cartesian-style tasks for manipulating symbols. An early benchmark for AI was to learn to play`

end sample:
- `L0111 p4.7: large shifts in attention and resources to whatever the current paradigm is (e.g., LLMs today),`
- `L0112 p4.8: while all the actually complex parts of intelligence (as laid out in the creature hypothesis) run the`
- `L0113 p4.9: risk of never getting addressed.`

start boundary context:
- `L0082 p3.14: as what happens symbolically inside of a computer. According to Agre, this will unnecessarily`
- `L0083 p3.15: constrain our design of both AI systems and organizations.`
- `L0084 p3.17: 2.2 Brooks’ “creature hypothesis”: defamiliarizing Cartesian stories about learning`
- `L0085 p3.18: The AI field has often set the benchmarks for intelligent learning in terms of individual`
- `L0086 p3.19: Cartesian-style tasks for manipulating symbols. An early benchmark for AI was to learn to play`

end boundary context:
- `L0112 p4.8: while all the actually complex parts of intelligence (as laid out in the creature hypothesis) run the`
- `L0113 p4.9: risk of never getting addressed.`
- `L0114 p4.11: 2.3 Wiener’s “variety”: defamiliarizing Cartesian concepts of complexity`
- `L0115 p4.12: Cartesianism implies a concept of complexity in terms of the amount of internal symbol`
- `L0116 p4.13: manipulations. We saw measures of such complexity as, for example, Shannon entropy or the`

### 005. Wiener’s “variety”: defamiliarizing Cartesian concepts of complexity

- level: 2; pages: 4-4; lines: 114-139; words: 338

start sample:
- `L0114 p4.11: 2.3 Wiener’s “variety”: defamiliarizing Cartesian concepts of complexity`
- `L0115 p4.12: Cartesianism implies a concept of complexity in terms of the amount of internal symbol`
- `L0116 p4.13: manipulations. We saw measures of such complexity as, for example, Shannon entropy or the`

end sample:
- `L0136 p4.35: “non-modern” (e.g., non-Cartesian, non-Newtonian, or non-industrial) concept of complexity`
- `L0137 p4.36: that foregrounds novel ways of organizing direct interactions with the physical and cultural`
- `L0138 p4.37: world rather than of structuring symbol manipulations.`

start boundary context:
- `L0112 p4.8: while all the actually complex parts of intelligence (as laid out in the creature hypothesis) run the`
- `L0113 p4.9: risk of never getting addressed.`
- `L0114 p4.11: 2.3 Wiener’s “variety”: defamiliarizing Cartesian concepts of complexity`
- `L0115 p4.12: Cartesianism implies a concept of complexity in terms of the amount of internal symbol`
- `L0116 p4.13: manipulations. We saw measures of such complexity as, for example, Shannon entropy or the`

end boundary context:
- `L0137 p4.36: that foregrounds novel ways of organizing direct interactions with the physical and cultural`
- `L0138 p4.37: world rather than of structuring symbol manipulations.`
- `L0139 p5.0: 3. Criteria for intelligent interaction`
- `L0140 p5.1: 3.1 Goals: homeostasis or “comportment”`
- `L0141 p5.2: The earliest ideas about interaction in AI originated in the field’s immediate predecessor called`

### 006. Goals: homeostasis or “comportment”

- level: 2; pages: 5-6; lines: 140-184; words: 613

start sample:
- `L0140 p5.1: 3.1 Goals: homeostasis or “comportment”`
- `L0141 p5.2: The earliest ideas about interaction in AI originated in the field’s immediate predecessor called`
- `L0142 p5.3: cybernetics, which arose in the 1940s led by Wiener. “Cyber” means “to govern”, and`

end sample:
- `L0181 p6.13: seems to play together effortlessly, or our everyday common sense, such as how a team of`
- `L0182 p6.14: medical professionals are able to navigate their way through cases mostly without consciously`
- `L0183 p6.15: thinking about it.`

start boundary context:
- `L0138 p4.37: world rather than of structuring symbol manipulations.`
- `L0139 p5.0: 3. Criteria for intelligent interaction`
- `L0140 p5.1: 3.1 Goals: homeostasis or “comportment”`
- `L0141 p5.2: The earliest ideas about interaction in AI originated in the field’s immediate predecessor called`
- `L0142 p5.3: cybernetics, which arose in the 1940s led by Wiener. “Cyber” means “to govern”, and`

end boundary context:
- `L0182 p6.14: medical professionals are able to navigate their way through cases mostly without consciously`
- `L0183 p6.15: thinking about it.`
- `L0184 p6.17: 3.2 Action as situated, embodied, and embedded`
- `L0185 p6.18: The above examples suggest important aspects of intelligently solving problems are learned`
- `L0186 p6.19: using sensorimotor actions to interact with and experience the physical world, and where goals`

### 007. Action as situated, embodied, and embedded

- level: 2; pages: 6-7; lines: 184-219; words: 472

start sample:
- `L0184 p6.17: 3.2 Action as situated, embodied, and embedded`
- `L0185 p6.18: The above examples suggest important aspects of intelligently solving problems are learned`
- `L0186 p6.19: using sensorimotor actions to interact with and experience the physical world, and where goals`

end sample:
- `L0216 p7.8: crossed by a pedestrian with caution (since cars will tend to go through the crosswalk,`
- `L0217 p7.9: even given a waiting pedestrian); in contrast, in Vietnam, even if there is no crosswalk`
- `L0218 p7.10: (and a lot of traffic), it is often acceptable just to walk across the street without waiting.`

start boundary context:
- `L0182 p6.14: medical professionals are able to navigate their way through cases mostly without consciously`
- `L0183 p6.15: thinking about it.`
- `L0184 p6.17: 3.2 Action as situated, embodied, and embedded`
- `L0185 p6.18: The above examples suggest important aspects of intelligently solving problems are learned`
- `L0186 p6.19: using sensorimotor actions to interact with and experience the physical world, and where goals`

end boundary context:
- `L0217 p7.9: even given a waiting pedestrian); in contrast, in Vietnam, even if there is no crosswalk`
- `L0218 p7.10: (and a lot of traffic), it is often acceptable just to walk across the street without waiting.`
- `L0219 p7.13: 3.3 Assigning credit efficiently: the world as its own best model`
- `L0220 p7.14: Brooks’ phrase “the world is its own best model” (where by “model”, he was referring to the`
- `L0221 p7.15: use of Cartesian-style symbolic representations) implies that an AI system or organization can be`

### 008. Assigning credit efficiently: the world as its own best model

- level: 2; pages: 7-9; lines: 219-284; words: 921

start sample:
- `L0219 p7.13: 3.3 Assigning credit efficiently: the world as its own best model`
- `L0220 p7.14: Brooks’ phrase “the world is its own best model” (where by “model”, he was referring to the`
- `L0221 p7.15: use of Cartesian-style symbolic representations) implies that an AI system or organization can be`

end sample:
- `L0281 p9.9: ongoing interplay between representations (schemes), reality (the physical world) and our`
- `L0282 p9.10: experience of these — what Cantwell-Smith calls the interplay between “reckoning and`
- `L0283 p9.11: judgment” — that refers to processes of registration.`

start boundary context:
- `L0217 p7.9: even given a waiting pedestrian); in contrast, in Vietnam, even if there is no crosswalk`
- `L0218 p7.10: (and a lot of traffic), it is often acceptable just to walk across the street without waiting.`
- `L0219 p7.13: 3.3 Assigning credit efficiently: the world as its own best model`
- `L0220 p7.14: Brooks’ phrase “the world is its own best model” (where by “model”, he was referring to the`
- `L0221 p7.15: use of Cartesian-style symbolic representations) implies that an AI system or organization can be`

end boundary context:
- `L0282 p9.10: experience of these — what Cantwell-Smith calls the interplay between “reckoning and`
- `L0283 p9.11: judgment” — that refers to processes of registration.`
- `L0284 p9.14: 4. Strategies for interaction in AI and organizations`
- `L0285 p9.15: The previous subsection explained basic building blocks that can be used to understand any ideas`
- `L0286 p9.16: of interaction in AI and organizations. Intelligence arises from learning to homeostatically`

### 009. Strategies for interaction in AI and organizations

- level: 1; pages: 9-9; lines: 284-295; words: 132

start sample:
- `L0284 p9.14: 4. Strategies for interaction in AI and organizations`
- `L0285 p9.15: The previous subsection explained basic building blocks that can be used to understand any ideas`
- `L0286 p9.16: of interaction in AI and organizations. Intelligence arises from learning to homeostatically`

end sample:
- `L0292 p9.22: consider two main technical proposals: Brooks’ subsumption architecture (which does not`
- `L0293 p9.23: require any symbol manipulation), and the notion of direct manipulation of symbols as`
- `L0294 p9.24: resources for action.`

start boundary context:
- `L0282 p9.10: experience of these — what Cantwell-Smith calls the interplay between “reckoning and`
- `L0283 p9.11: judgment” — that refers to processes of registration.`
- `L0284 p9.14: 4. Strategies for interaction in AI and organizations`
- `L0285 p9.15: The previous subsection explained basic building blocks that can be used to understand any ideas`
- `L0286 p9.16: of interaction in AI and organizations. Intelligence arises from learning to homeostatically`

end boundary context:
- `L0293 p9.23: require any symbol manipulation), and the notion of direct manipulation of symbols as`
- `L0294 p9.24: resources for action.`
- `L0295 p9.26: 4.1 Learning based on goals for interacting with the world: the subsumption architecture`
- `L0296 p9.27: Brooks proposed that the sensorimotor actions fundamental to the evolution of intelligence could`
- `L0297 p9.28: be understood as corresponding to multiple goals (also called behaviors) that need to be`

### 010. Learning based on goals for interacting with the world: the subsumption architecture

- level: 2; pages: 9-10; lines: 295-331; words: 499

start sample:
- `L0295 p9.26: 4.1 Learning based on goals for interacting with the world: the subsumption architecture`
- `L0296 p9.27: Brooks proposed that the sensorimotor actions fundamental to the evolution of intelligence could`
- `L0297 p9.28: be understood as corresponding to multiple goals (also called behaviors) that need to be`

end sample:
- `L0328 p10.20: simple circuits, called finite state machines (FSMs), with no communication channels (i.e., this is`
- `L0329 p10.21: not like Shannon information).`
- `L0330 p10.30: Basic elements of the subsumption architecture Example architecture for a simple robot`

start boundary context:
- `L0293 p9.23: require any symbol manipulation), and the notion of direct manipulation of symbols as`
- `L0294 p9.24: resources for action.`
- `L0295 p9.26: 4.1 Learning based on goals for interacting with the world: the subsumption architecture`
- `L0296 p9.27: Brooks proposed that the sensorimotor actions fundamental to the evolution of intelligence could`
- `L0297 p9.28: be understood as corresponding to multiple goals (also called behaviors) that need to be`

end boundary context:
- `L0329 p10.21: not like Shannon information).`
- `L0330 p10.30: Basic elements of the subsumption architecture Example architecture for a simple robot`
- `L0331 p10.33: 4.2. Direct manipulation of symbols`
- `L0332 p10.34: Another main area of research on interaction in AI and organizations concerns directly`
- `L0333 p10.35: interacting with physical media, and specifically digital representations in personal computers`

### 011. Direct manipulation of symbols

- level: 2; pages: 10-11; lines: 331-376; words: 617

start sample:
- `L0331 p10.33: 4.2. Direct manipulation of symbols`
- `L0332 p10.34: Another main area of research on interaction in AI and organizations concerns directly`
- `L0333 p10.35: interacting with physical media, and specifically digital representations in personal computers`

end sample:
- `L0373 p11.37: Analogous to McCarthy’s ideas about programming as declarative, the engineer only needed to`
- `L0374 p11.38: directly manipulate a computer since the computer stored constraints about what the circuit`
- `L0375 p11.39: should do, rather than precisely how to do it.`

start boundary context:
- `L0329 p10.21: not like Shannon information).`
- `L0330 p10.30: Basic elements of the subsumption architecture Example architecture for a simple robot`
- `L0331 p10.33: 4.2. Direct manipulation of symbols`
- `L0332 p10.34: Another main area of research on interaction in AI and organizations concerns directly`
- `L0333 p10.35: interacting with physical media, and specifically digital representations in personal computers`

end boundary context:
- `L0374 p11.38: directly manipulate a computer since the computer stored constraints about what the circuit`
- `L0375 p11.39: should do, rather than precisely how to do it.`
