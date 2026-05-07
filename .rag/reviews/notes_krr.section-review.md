# Section Manifest Review: notes_krr

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

- source_pdf: `docs/course-notes/Course Notes — Knowledge Representation and Reasoning - FAB Spring 2026.pdf`
- doc_id: `notes_krr`
- title: Knowledge Representation and Reasoning
- target_manifest: `.rag/manifests/notes_krr.sections.json`
- source_kind: existing manifest
- source_sha_status: fresh
- extracted_lines: 366
- current_sections: 14

## Review Checklist

- Does every top-level/subsection heading start a sensible chunk?
- Are tiny heading-only chunks merged with their following explanatory section when useful?
- Are very large sections split at meaningful internal headings or topic turns?
- Do start/end snippets show missing text, duplicated text, or page-order extraction problems?
- Are page ranges and titles still accurate after any edits?

## Commands

```bash
uv run python scripts/rag.py review-sections --doc-id notes_krr --write
uv run python scripts/rag.py index
```

## Current Sections

### 001. Introduction

- level: 1; pages: 1-2; lines: 0-65; words: 906

start sample:
- `L0000 p1.0: Course Notes — SESSION 6`
- `L0001 p1.1: KNOWLEDGE REPRESENTATION AND REASONING`
- `L0002 p1.3: 1. Introduction`

end sample:
- `L0062 p2.29: knowledge and reasoning. Hence, the general problem of credit assignment in AI ultimately`
- `L0063 p2.30: reduces down to — or is most fundamentally about — the challenges of representing and`
- `L0064 p2.31: reasoning about commonsense knowledge.`

start boundary context:
- `L0000 p1.0: Course Notes — SESSION 6`
- `L0001 p1.1: KNOWLEDGE REPRESENTATION AND REASONING`
- `L0002 p1.3: 1. Introduction`

end boundary context:
- `L0063 p2.30: reduces down to — or is most fundamentally about — the challenges of representing and`
- `L0064 p2.31: reasoning about commonsense knowledge.`
- `L0065 p2.34: 2. The Advice taker and the frame problem`
- `L0066 p2.35: What are the possibilities and challenges of representing and reasoning about commonsense`
- `L0067 p2.36: knowledge in AI systems and organizations? In 1959, McCarthy outlined a vision of the`

### 002. The Advice taker and the frame problem

- level: 1; pages: 2-2; lines: 65-71; words: 78
- review_flags: short_chunk

start sample:
- `L0065 p2.34: 2. The Advice taker and the frame problem`
- `L0066 p2.35: What are the possibilities and challenges of representing and reasoning about commonsense`
- `L0067 p2.36: knowledge in AI systems and organizations? In 1959, McCarthy outlined a vision of the`

start boundary context:
- `L0063 p2.30: reduces down to — or is most fundamentally about — the challenges of representing and`
- `L0064 p2.31: reasoning about commonsense knowledge.`
- `L0065 p2.34: 2. The Advice taker and the frame problem`
- `L0066 p2.35: What are the possibilities and challenges of representing and reasoning about commonsense`
- `L0067 p2.36: knowledge in AI systems and organizations? In 1959, McCarthy outlined a vision of the`

end boundary context:
- `L0069 p2.38: decade of research later, in 1969, he outlined what he had found to be the fundamental credit`
- `L0070 p2.39: assignment challenge in KRR that he called the “frame problem”.`
- `L0071 p3.0: 2.1 Advice taker: envisioning an AI system that represents and reasons about knowledge`
- `L0072 p3.1: McCarthy’s proposed AI system can be summarized as having the following characteristics:`
- `L0073 p3.2: (1) The Advice Taker easily learns new representations just by you telling it facts about`

### 003. Advice taker: envisioning an AI system that represents and reasons about knowledge

- level: 2; pages: 3-3; lines: 71-100; words: 378

start sample:
- `L0071 p3.0: 2.1 Advice taker: envisioning an AI system that represents and reasons about knowledge`
- `L0072 p3.1: McCarthy’s proposed AI system can be summarized as having the following characteristics:`
- `L0073 p3.2: (1) The Advice Taker easily learns new representations just by you telling it facts about`

end sample:
- `L0097 p3.27: commonsense reasoning). Hence, McCarthy’s overall point of view was that an intelligent AI`
- `L0098 p3.28: system or organization is one that has common sense, defined as a general capacity to represent`
- `L0099 p3.29: and reason about knowledge across situations.`

start boundary context:
- `L0069 p2.38: decade of research later, in 1969, he outlined what he had found to be the fundamental credit`
- `L0070 p2.39: assignment challenge in KRR that he called the “frame problem”.`
- `L0071 p3.0: 2.1 Advice taker: envisioning an AI system that represents and reasons about knowledge`
- `L0072 p3.1: McCarthy’s proposed AI system can be summarized as having the following characteristics:`
- `L0073 p3.2: (1) The Advice Taker easily learns new representations just by you telling it facts about`

end boundary context:
- `L0098 p3.28: system or organization is one that has common sense, defined as a general capacity to represent`
- `L0099 p3.29: and reason about knowledge across situations.`
- `L0100 p3.31: 2.2 The frame problem: KRR and the credit assignment problem`
- `L0101 p3.32: What are the challenges of achieving his Advice Taker vision? The obvious challenge is that`
- `L0102 p3.33: there is presumably a lot of commonsense knowledge about the world, such that representing it is`

### 004. The frame problem: KRR and the credit assignment problem

- level: 2; pages: 3-5; lines: 100-147; words: 746

start sample:
- `L0100 p3.31: 2.2 The frame problem: KRR and the credit assignment problem`
- `L0101 p3.32: What are the challenges of achieving his Advice Taker vision? The obvious challenge is that`
- `L0102 p3.33: there is presumably a lot of commonsense knowledge about the world, such that representing it is`

end sample:
- `L0144 p5.0: know tons of this stuff, or what he called “commonsense knowledge”. Further, it needs to be able`
- `L0145 p5.1: to efficiently access and make inferences from this knowledge, called “commonsense reasoning”,`
- `L0146 p5.2: with a characteristic called “elaboration tolerance”.`

start boundary context:
- `L0098 p3.28: system or organization is one that has common sense, defined as a general capacity to represent`
- `L0099 p3.29: and reason about knowledge across situations.`
- `L0100 p3.31: 2.2 The frame problem: KRR and the credit assignment problem`
- `L0101 p3.32: What are the challenges of achieving his Advice Taker vision? The obvious challenge is that`
- `L0102 p3.33: there is presumably a lot of commonsense knowledge about the world, such that representing it is`

end boundary context:
- `L0145 p5.1: to efficiently access and make inferences from this knowledge, called “commonsense reasoning”,`
- `L0146 p5.2: with a characteristic called “elaboration tolerance”.`
- `L0147 p5.5: 3. Representing commonsense knowledge`
- `L0148 p5.6: For McCarthy, common sense refers to knowledge that is common to most humans. Common`
- `L0149 p5.7: sense can be granular, such as the common sense specific to a local culture or practice. The basic`

### 005. Representing commonsense knowledge

- level: 1; pages: 5-5; lines: 147-159; words: 138

start sample:
- `L0147 p5.5: 3. Representing commonsense knowledge`
- `L0148 p5.6: For McCarthy, common sense refers to knowledge that is common to most humans. Common`
- `L0149 p5.7: sense can be granular, such as the common sense specific to a local culture or practice. The basic`

end sample:
- `L0156 p5.14: (4) What the physical world is like and how it is perceived, including the properties of`
- `L0157 p5.15: objects and relations of these objects and properties to one another.`
- `L0158 p5.16: (5) Concepts and principles to abstract all of the above knowledge.`

start boundary context:
- `L0145 p5.1: to efficiently access and make inferences from this knowledge, called “commonsense reasoning”,`
- `L0146 p5.2: with a characteristic called “elaboration tolerance”.`
- `L0147 p5.5: 3. Representing commonsense knowledge`
- `L0148 p5.6: For McCarthy, common sense refers to knowledge that is common to most humans. Common`
- `L0149 p5.7: sense can be granular, such as the common sense specific to a local culture or practice. The basic`

end boundary context:
- `L0157 p5.15: objects and relations of these objects and properties to one another.`
- `L0158 p5.16: (5) Concepts and principles to abstract all of the above knowledge.`
- `L0159 p5.18: 3.1 Knowledge representations need to be declarative`
- `L0160 p5.19: Let us introduce a distinction between explicit and implicit knowledge. Explicit means stored in`
- `L0161 p5.20: minds or external memory, such as paper or a computing device. Implicit can be illustrated by`

### 006. Knowledge representations need to be declarative

- level: 2; pages: 5-6; lines: 159-181; words: 313

start sample:
- `L0159 p5.18: 3.1 Knowledge representations need to be declarative`
- `L0160 p5.19: Let us introduce a distinction between explicit and implicit knowledge. Explicit means stored in`
- `L0161 p5.20: minds or external memory, such as paper or a computing device. Implicit can be illustrated by`

end sample:
- `L0178 p5.38: representations should be abstracted into objects, and treated as if they were units of data. He`
- `L0179 p6.0: developed a language, called Lisp (short for “list processing”), in which all commonsense`
- `L0180 p6.1: knowledge — facts, programs, etc. — could be represented declaratively as lists.`

start boundary context:
- `L0157 p5.15: objects and relations of these objects and properties to one another.`
- `L0158 p5.16: (5) Concepts and principles to abstract all of the above knowledge.`
- `L0159 p5.18: 3.1 Knowledge representations need to be declarative`
- `L0160 p5.19: Let us introduce a distinction between explicit and implicit knowledge. Explicit means stored in`
- `L0161 p5.20: minds or external memory, such as paper or a computing device. Implicit can be illustrated by`

end boundary context:
- `L0179 p6.0: developed a language, called Lisp (short for “list processing”), in which all commonsense`
- `L0180 p6.1: knowledge — facts, programs, etc. — could be represented declaratively as lists.`
- `L0181 p6.3: 3.2 Knowledge representations need to allow concepts at various levels of abstraction`
- `L0182 p6.4: Declarative, list-based representations should also enable representing concepts — that is, not`
- `L0183 p6.5: just facts or programs and such things, but ways of talking about them conceptually, meaning at`

### 007. Knowledge representations need to allow concepts at various levels of abstraction

- level: 2; pages: 6-6; lines: 181-188; words: 97
- review_flags: short_chunk

start sample:
- `L0181 p6.3: 3.2 Knowledge representations need to allow concepts at various levels of abstraction`
- `L0182 p6.4: Declarative, list-based representations should also enable representing concepts — that is, not`
- `L0183 p6.5: just facts or programs and such things, but ways of talking about them conceptually, meaning at`

end sample:
- `L0185 p6.7: about specific phenomena without having to represent and reason about all the facts. For`
- `L0186 p6.8: example, our implicit knowledge told us that the Pyramids of Giza should be older than my`
- `L0187 p6.9: neighbor’s house since we have a more abstract concept of a neighbor’s house.`

start boundary context:
- `L0179 p6.0: developed a language, called Lisp (short for “list processing”), in which all commonsense`
- `L0180 p6.1: knowledge — facts, programs, etc. — could be represented declaratively as lists.`
- `L0181 p6.3: 3.2 Knowledge representations need to allow concepts at various levels of abstraction`
- `L0182 p6.4: Declarative, list-based representations should also enable representing concepts — that is, not`
- `L0183 p6.5: just facts or programs and such things, but ways of talking about them conceptually, meaning at`

end boundary context:
- `L0186 p6.8: example, our implicit knowledge told us that the Pyramids of Giza should be older than my`
- `L0187 p6.9: neighbor’s house since we have a more abstract concept of a neighbor’s house.`
- `L0188 p6.11: 3.3 Knowledge representations need to reflect contexts`
- `L0189 p6.12: Consider the following sentence: “I tried to fill the suitcase with the whale, but it was too big”.`
- `L0190 p6.13: What is “it” in this sentence? We would conclude, based on our common sense, that “it” in the`

### 008. Knowledge representations need to reflect contexts

- level: 2; pages: 6-6; lines: 188-215; words: 427

start sample:
- `L0188 p6.11: 3.3 Knowledge representations need to reflect contexts`
- `L0189 p6.12: Consider the following sentence: “I tried to fill the suitcase with the whale, but it was too big”.`
- `L0190 p6.13: What is “it” in this sentence? We would conclude, based on our common sense, that “it” in the`

end sample:
- `L0212 p6.37: even if we figure out how to provide an AI system with enough explicit knowledge to derive an`
- `L0213 p6.38: adequate amount of implicit knowledge, we need to enable the system also to have some`
- `L0214 p6.39: common sense in how to flexibly modify its knowledge to such situation-specific contexts.`

start boundary context:
- `L0186 p6.8: example, our implicit knowledge told us that the Pyramids of Giza should be older than my`
- `L0187 p6.9: neighbor’s house since we have a more abstract concept of a neighbor’s house.`
- `L0188 p6.11: 3.3 Knowledge representations need to reflect contexts`
- `L0189 p6.12: Consider the following sentence: “I tried to fill the suitcase with the whale, but it was too big”.`
- `L0190 p6.13: What is “it” in this sentence? We would conclude, based on our common sense, that “it” in the`

end boundary context:
- `L0213 p6.38: adequate amount of implicit knowledge, we need to enable the system also to have some`
- `L0214 p6.39: common sense in how to flexibly modify its knowledge to such situation-specific contexts.`
- `L0215 p7.0: 4. Elaborating commonsense knowledge`
- `L0216 p7.1: The process of representing knowledge in an AI system or organization — whether general`
- `L0217 p7.2: commonsense knowledge or knowledge specific to the context of problems solved in a particular`

### 009. Elaborating commonsense knowledge

- level: 1; pages: 7-7; lines: 215-248; words: 472

start sample:
- `L0215 p7.0: 4. Elaborating commonsense knowledge`
- `L0216 p7.1: The process of representing knowledge in an AI system or organization — whether general`
- `L0217 p7.2: commonsense knowledge or knowledge specific to the context of problems solved in a particular`

end sample:
- `L0245 p7.32: ‘the effort required to add new information to the repository is proportional to the complexity of`
- `L0246 p7.33: that information’. You can think of ‘effort required’ as the amount of ‘garbage’ — i.e.,`
- `L0247 p7.34: non-useful information — that has ‘piled up’ in the repository and needs to be collected.`

start boundary context:
- `L0213 p6.38: adequate amount of implicit knowledge, we need to enable the system also to have some`
- `L0214 p6.39: common sense in how to flexibly modify its knowledge to such situation-specific contexts.`
- `L0215 p7.0: 4. Elaborating commonsense knowledge`
- `L0216 p7.1: The process of representing knowledge in an AI system or organization — whether general`
- `L0217 p7.2: commonsense knowledge or knowledge specific to the context of problems solved in a particular`

end boundary context:
- `L0246 p7.33: that information’. You can think of ‘effort required’ as the amount of ‘garbage’ — i.e.,`
- `L0247 p7.34: non-useful information — that has ‘piled up’ in the repository and needs to be collected.`
- `L0248 p7.36: 4.1 Elaboration tolerance requires “default reasoning”`
- `L0249 p7.37: Consider our earlier sentence: “I tried to fill the suitcase with the whale, but it was too big”.`
- `L0250 p7.38: Perhaps it is a real whale, or a stuffed animal whale. Or perhaps “whale” is a nickname for some`

### 010. Elaboration tolerance requires “default reasoning”

- level: 2; pages: 7-8; lines: 248-257; words: 136

start sample:
- `L0248 p7.36: 4.1 Elaboration tolerance requires “default reasoning”`
- `L0249 p7.37: Consider our earlier sentence: “I tried to fill the suitcase with the whale, but it was too big”.`
- `L0250 p7.38: Perhaps it is a real whale, or a stuffed animal whale. Or perhaps “whale” is a nickname for some`

end sample:
- `L0254 p8.3: doing so on the basis of some default assumptions — our commonsense assumptions about the`
- `L0255 p8.4: way the world is. In this way, we only need to change our assumptions when specific evidence`
- `L0256 p8.5: arrives, such as me telling you that the whale is in fact a stuffed animal.`

start boundary context:
- `L0246 p7.33: that information’. You can think of ‘effort required’ as the amount of ‘garbage’ — i.e.,`
- `L0247 p7.34: non-useful information — that has ‘piled up’ in the repository and needs to be collected.`
- `L0248 p7.36: 4.1 Elaboration tolerance requires “default reasoning”`
- `L0249 p7.37: Consider our earlier sentence: “I tried to fill the suitcase with the whale, but it was too big”.`
- `L0250 p7.38: Perhaps it is a real whale, or a stuffed animal whale. Or perhaps “whale” is a nickname for some`

end boundary context:
- `L0255 p8.4: way the world is. In this way, we only need to change our assumptions when specific evidence`
- `L0256 p8.5: arrives, such as me telling you that the whale is in fact a stuffed animal.`
- `L0257 p8.7: 4.2 Elaboration tolerance requires adequately “expressive” languages`
- `L0258 p8.8: Think of the problems that SQL databases address versus a standard file system. The achieve`
- `L0259 p8.9: high integrity in storing and updating data by introducing a formal language for doing so — one`

### 011. Elaboration tolerance requires adequately “expressive” languages

- level: 2; pages: 8-8; lines: 257-272; words: 214

start sample:
- `L0257 p8.7: 4.2 Elaboration tolerance requires adequately “expressive” languages`
- `L0258 p8.8: Think of the problems that SQL databases address versus a standard file system. The achieve`
- `L0259 p8.9: high integrity in storing and updating data by introducing a formal language for doing so — one`

end sample:
- `L0269 p8.20: complex. In fact, the challenges of elaboration in an organization can fundamentally impair its`
- `L0270 p8.21: intelligence, as reflected in how the majority of data science work is not in data-driven`
- `L0271 p8.22: problem-solving per se, but rather in tasks of integrating data.`

start boundary context:
- `L0255 p8.4: way the world is. In this way, we only need to change our assumptions when specific evidence`
- `L0256 p8.5: arrives, such as me telling you that the whale is in fact a stuffed animal.`
- `L0257 p8.7: 4.2 Elaboration tolerance requires adequately “expressive” languages`
- `L0258 p8.8: Think of the problems that SQL databases address versus a standard file system. The achieve`
- `L0259 p8.9: high integrity in storing and updating data by introducing a formal language for doing so — one`

end boundary context:
- `L0270 p8.21: intelligence, as reflected in how the majority of data science work is not in data-driven`
- `L0271 p8.22: problem-solving per se, but rather in tasks of integrating data.`
- `L0272 p8.25: 5. Approaches to representing and reasoning about knowledge`
- `L0273 p8.26: As in our previous sessions, we will understand AI ideas about knowledge representation and`
- `L0274 p8.27: reasoning in terms of two paradigmatically-different approaches. One approach, which we will`

### 012. Approaches to representing and reasoning about knowledge

- level: 1; pages: 8-8; lines: 272-280; words: 98
- review_flags: short_chunk

start sample:
- `L0272 p8.25: 5. Approaches to representing and reasoning about knowledge`
- `L0273 p8.26: As in our previous sessions, we will understand AI ideas about knowledge representation and`
- `L0274 p8.27: reasoning in terms of two paradigmatically-different approaches. One approach, which we will`

end sample:
- `L0277 p8.30: emerging from patterns in bit strings. Another approach, which we will refer to as the`
- `L0278 p8.31: mathematical logic approach, derives from McCarthy himself and views knowledge`
- `L0279 p8.32: representations as emerging from patterns in lists.`

start boundary context:
- `L0270 p8.21: intelligence, as reflected in how the majority of data science work is not in data-driven`
- `L0271 p8.22: problem-solving per se, but rather in tasks of integrating data.`
- `L0272 p8.25: 5. Approaches to representing and reasoning about knowledge`
- `L0273 p8.26: As in our previous sessions, we will understand AI ideas about knowledge representation and`
- `L0274 p8.27: reasoning in terms of two paradigmatically-different approaches. One approach, which we will`

end boundary context:
- `L0278 p8.31: mathematical logic approach, derives from McCarthy himself and views knowledge`
- `L0279 p8.32: representations as emerging from patterns in lists.`
- `L0280 p8.34: 5.1 Approach based on deep learning`
- `L0281 p8.35: The currently-popular approach to knowledge representation and reasoning (KRR) is based on`
- `L0282 p8.36: deep learning. This approach (at least implicitly) concerns the same fundamental challenges`

### 013. Approach based on deep learning

- level: 2; pages: 8-10; lines: 280-327; words: 579

start sample:
- `L0280 p8.34: 5.1 Approach based on deep learning`
- `L0281 p8.35: The currently-popular approach to knowledge representation and reasoning (KRR) is based on`
- `L0282 p8.36: deep learning. This approach (at least implicitly) concerns the same fundamental challenges`

end sample:
- `L0324 p10.2: of the new information. Updating knowledge typically involves indirect methods, such as`
- `L0325 p10.3: modifying prompts, updating external data sources, or retraining the entire model, rather than`
- `L0326 p10.4: ongoing and efficient operations on an evolving knowledge base.`

start boundary context:
- `L0278 p8.31: mathematical logic approach, derives from McCarthy himself and views knowledge`
- `L0279 p8.32: representations as emerging from patterns in lists.`
- `L0280 p8.34: 5.1 Approach based on deep learning`
- `L0281 p8.35: The currently-popular approach to knowledge representation and reasoning (KRR) is based on`
- `L0282 p8.36: deep learning. This approach (at least implicitly) concerns the same fundamental challenges`

end boundary context:
- `L0325 p10.3: modifying prompts, updating external data sources, or retraining the entire model, rather than`
- `L0326 p10.4: ongoing and efficient operations on an evolving knowledge base.`
- `L0327 p10.6: 5.2 Approach based on mathematical logic`
- `L0328 p10.7: Another approach, pioneered by John McCarthy himself, is based on mathematical logic. At a`
- `L0329 p10.8: very basic level, mathematical logic just means using a precise, rule-based language, similar to`

### 014. Approach based on mathematical logic

- level: 2; pages: 10-11; lines: 327-366; words: 509

start sample:
- `L0327 p10.6: 5.2 Approach based on mathematical logic`
- `L0328 p10.7: Another approach, pioneered by John McCarthy himself, is based on mathematical logic. At a`
- `L0329 p10.8: very basic level, mathematical logic just means using a precise, rule-based language, similar to`

end sample:
- `L0363 p11.6: level, a requirement seems to be to deliberately represent at least a good chunk of commonsense`
- `L0364 p11.7: knowledge for such systems. Hence, though such an AI system’s knowledge should be easier to`
- `L0365 p11.8: track and understand, it is harder for now to construct such systems at scale.`

start boundary context:
- `L0325 p10.3: modifying prompts, updating external data sources, or retraining the entire model, rather than`
- `L0326 p10.4: ongoing and efficient operations on an evolving knowledge base.`
- `L0327 p10.6: 5.2 Approach based on mathematical logic`
- `L0328 p10.7: Another approach, pioneered by John McCarthy himself, is based on mathematical logic. At a`
- `L0329 p10.8: very basic level, mathematical logic just means using a precise, rule-based language, similar to`

end boundary context:
- `L0364 p11.7: knowledge for such systems. Hence, though such an AI system’s knowledge should be easier to`
- `L0365 p11.8: track and understand, it is harder for now to construct such systems at scale.`
