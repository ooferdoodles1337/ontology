# Section Manifest Review: notes_representation

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

- source_pdf: `docs/course-notes/Course Notes — Representation - FAB.pdf`
- doc_id: `notes_representation`
- title: Representation
- target_manifest: `.rag/manifests/notes_representation.sections.json`
- source_kind: existing manifest
- source_sha_status: fresh
- extracted_lines: 556
- current_sections: 17

## Review Checklist

- Does every top-level/subsection heading start a sensible chunk?
- Are tiny heading-only chunks merged with their following explanatory section when useful?
- Are very large sections split at meaningful internal headings or topic turns?
- Do start/end snippets show missing text, duplicated text, or page-order extraction problems?
- Are page ranges and titles still accurate after any edits?

## Commands

```bash
uv run python scripts/rag.py review-sections --doc-id notes_representation --write
uv run python scripts/rag.py index
```

## Current Sections

### 001. Introduction

- level: 1; pages: 1-2; lines: 0-33; words: 429

start sample:
- `L0000 p1.0: Course Notes`
- `L0001 p1.1: REPRESENTATION`
- `L0002 p1.3: 1. Introduction`

end sample:
- `L0030 p2.3: of these examples in terms of two “hypotheses” about how representations lead to intelligence`
- `L0031 p2.4: (corresponding to the assumption of Shannon versus Simon information), which we will call the`
- `L0032 p2.5: “physics hypothesis” and the “society of mind hypothesis”.`

start boundary context:
- `L0000 p1.0: Course Notes`
- `L0001 p1.1: REPRESENTATION`
- `L0002 p1.3: 1. Introduction`

end boundary context:
- `L0031 p2.4: (corresponding to the assumption of Shannon versus Simon information), which we will call the`
- `L0032 p2.5: “physics hypothesis” and the “society of mind hypothesis”.`
- `L0033 p2.8: 2 Some examples of representations`
- `L0034 p2.9: Before we go into the building blocks of representations, let’s begin with some real-world`
- `L0035 p2.10: examples. Representations can be internal (stored in the mind, or the memory of a computer), or`

### 002. Some examples of representations

- level: 1; pages: 2-2; lines: 33-40; words: 81
- review_flags: short_chunk

start sample:
- `L0033 p2.8: 2 Some examples of representations`
- `L0034 p2.9: Before we go into the building blocks of representations, let’s begin with some real-world`
- `L0035 p2.10: examples. Representations can be internal (stored in the mind, or the memory of a computer), or`

end sample:
- `L0037 p2.12: books, traffic signs, or any other symbols out there in the world). Let’s first take a look at some`
- `L0038 p2.13: familiar examples of external representations and consider how they support complex`
- `L0039 p2.14: problem-solving.`

start boundary context:
- `L0031 p2.4: (corresponding to the assumption of Shannon versus Simon information), which we will call the`
- `L0032 p2.5: “physics hypothesis” and the “society of mind hypothesis”.`
- `L0033 p2.8: 2 Some examples of representations`
- `L0034 p2.9: Before we go into the building blocks of representations, let’s begin with some real-world`
- `L0035 p2.10: examples. Representations can be internal (stored in the mind, or the memory of a computer), or`

end boundary context:
- `L0038 p2.13: familiar examples of external representations and consider how they support complex`
- `L0039 p2.14: problem-solving.`
- `L0040 p2.16: 2.1 Representations and complex problem-solving`
- `L0041 p2.17: (1) Until the 17th century, algebra problems were done using prose, rather than notation such`
- `L0042 p2.18: as Xs and Ys. The invention of algebraic notation made it far easier to understand and`

### 003. Representations and complex problem-solving

- level: 2; pages: 2-3; lines: 40-58; words: 215

start sample:
- `L0040 p2.16: 2.1 Representations and complex problem-solving`
- `L0041 p2.17: (1) Until the 17th century, algebra problems were done using prose, rather than notation such`
- `L0042 p2.18: as Xs and Ys. The invention of algebraic notation made it far easier to understand and`

end sample:
- `L0055 p3.4: engineers drafting the designs of automobiles at the US auto manufacturer General`
- `L0056 p3.5: Motors in the 1950s (left) and optical equipment at Tamron, a Japanese manufacturer of`
- `L0057 p3.6: optical equipment, in the 1970s (right).`

start boundary context:
- `L0038 p2.13: familiar examples of external representations and consider how they support complex`
- `L0039 p2.14: problem-solving.`
- `L0040 p2.16: 2.1 Representations and complex problem-solving`
- `L0041 p2.17: (1) Until the 17th century, algebra problems were done using prose, rather than notation such`
- `L0042 p2.18: as Xs and Ys. The invention of algebraic notation made it far easier to understand and`

end boundary context:
- `L0056 p3.5: Motors in the 1950s (left) and optical equipment at Tamron, a Japanese manufacturer of`
- `L0057 p3.6: optical equipment, in the 1970s (right).`
- `L0058 p3.20: 2.2 Digital representations and complex problem-solving`
- `L0059 p3.21: Unlike the above examples, many representations that we use today are stored in electronic`
- `L0060 p3.22: digital computers. Though the electronic digital computer emerged in the 1940s, it was too big`

### 004. Digital representations and complex problem-solving

- level: 2; pages: 3-5; lines: 58-91; words: 421

start sample:
- `L0058 p3.20: 2.2 Digital representations and complex problem-solving`
- `L0059 p3.21: Unlike the above examples, many representations that we use today are stored in electronic`
- `L0060 p3.22: digital computers. Though the electronic digital computer emerged in the 1940s, it was too big`

end sample:
- `L0088 p5.1: in “exposing the natural constraints inherent in a problem”, which may or may not be helped by`
- `L0089 p5.2: making representations more complex. Yet how might these examples also possibly reduce the`
- `L0090 p5.3: value of non-digital representations, such as the paper engineering drawings?`

start boundary context:
- `L0056 p3.5: Motors in the 1950s (left) and optical equipment at Tamron, a Japanese manufacturer of`
- `L0057 p3.6: optical equipment, in the 1970s (right).`
- `L0058 p3.20: 2.2 Digital representations and complex problem-solving`
- `L0059 p3.21: Unlike the above examples, many representations that we use today are stored in electronic`
- `L0060 p3.22: digital computers. Though the electronic digital computer emerged in the 1940s, it was too big`

end boundary context:
- `L0089 p5.2: making representations more complex. Yet how might these examples also possibly reduce the`
- `L0090 p5.3: value of non-digital representations, such as the paper engineering drawings?`
- `L0091 p5.6: 3. Representations as networks of constraints`
- `L0092 p5.7: Next, to connect these examples to AI and organizations, we need to transition from these`
- `L0093 p5.8: examples to a more precise set of building blocks of what representations and how they may`

### 005. Representations as networks of constraints

- level: 1; pages: 5-5; lines: 91-109; words: 257

start sample:
- `L0091 p5.6: 3. Representations as networks of constraints`
- `L0092 p5.7: Next, to connect these examples to AI and organizations, we need to transition from these`
- `L0093 p5.8: examples to a more precise set of building blocks of what representations and how they may`

end sample:
- `L0106 p5.22: spreadsheets and databases constrain the visualization of data into (respectively) rectangular grid`
- `L0107 p5.23: structures or tables, as well as restrict the types of data that can be entered. CAD software, like`
- `L0108 p5.24: engineering drawings, imposes constraints that control the proportionality of different objects.`

start boundary context:
- `L0089 p5.2: making representations more complex. Yet how might these examples also possibly reduce the`
- `L0090 p5.3: value of non-digital representations, such as the paper engineering drawings?`
- `L0091 p5.6: 3. Representations as networks of constraints`
- `L0092 p5.7: Next, to connect these examples to AI and organizations, we need to transition from these`
- `L0093 p5.8: examples to a more precise set of building blocks of what representations and how they may`

end boundary context:
- `L0107 p5.23: structures or tables, as well as restrict the types of data that can be entered. CAD software, like`
- `L0108 p5.24: engineering drawings, imposes constraints that control the proportionality of different objects.`
- `L0109 p5.26: 3.1 Constraints`
- `L0110 p5.27: A constraint can be defined as any restrictions on the values of a variable, or on the`
- `L0111 p5.28: relations among two or more variables. For example, say you go to buy a car and want the`

### 006. Constraints

- level: 2; pages: 5-7; lines: 109-189; words: 969

start sample:
- `L0109 p5.26: 3.1 Constraints`
- `L0110 p5.27: A constraint can be defined as any restrictions on the values of a variable, or on the`
- `L0111 p5.28: relations among two or more variables. For example, say you go to buy a car and want the`

end sample:
- `L0186 p7.34: constraints at a point assignments of values, where the car first, before choosing the`
- `L0187 p7.35: in time. solutions = consistent and “Interior color” as an example of a`
- `L0188 p7.36: complete assignments. partial assignment.`

start boundary context:
- `L0107 p5.23: structures or tables, as well as restrict the types of data that can be entered. CAD software, like`
- `L0108 p5.24: engineering drawings, imposes constraints that control the proportionality of different objects.`
- `L0109 p5.26: 3.1 Constraints`
- `L0110 p5.27: A constraint can be defined as any restrictions on the values of a variable, or on the`
- `L0111 p5.28: relations among two or more variables. For example, say you go to buy a car and want the`

end boundary context:
- `L0187 p7.35: in time. solutions = consistent and “Interior color” as an example of a`
- `L0188 p7.36: complete assignments. partial assignment.`
- `L0189 p7.39: 3.2 Propagating information across a constraint network`
- `L0190 p7.40: A set of constraints relevant to a complex problem in AI and organizations can be thought of as`
- `L0191 p7.41: structured into a network. A network (also called a graph structure) refers to any mathematical`

### 007. Propagating information across a constraint network

- level: 2; pages: 7-9; lines: 189-253; words: 968

start sample:
- `L0189 p7.39: 3.2 Propagating information across a constraint network`
- `L0190 p7.40: A set of constraints relevant to a complex problem in AI and organizations can be thought of as`
- `L0191 p7.41: structured into a network. A network (also called a graph structure) refers to any mathematical`

end sample:
- `L0250 p9.34: higher order constraints that can be used to propagate information. That is, the puzzle on the`
- `L0251 p9.35: right offers richer propagation, whereas the one on the left has less opportunities to propagate`
- `L0252 p9.36: information across the constraints.`

start boundary context:
- `L0187 p7.35: in time. solutions = consistent and “Interior color” as an example of a`
- `L0188 p7.36: complete assignments. partial assignment.`
- `L0189 p7.39: 3.2 Propagating information across a constraint network`
- `L0190 p7.40: A set of constraints relevant to a complex problem in AI and organizations can be thought of as`
- `L0191 p7.41: structured into a network. A network (also called a graph structure) refers to any mathematical`

end boundary context:
- `L0251 p9.35: right offers richer propagation, whereas the one on the left has less opportunities to propagate`
- `L0252 p9.36: information across the constraints.`
- `L0253 p10.0: 3.3 Satisfying constraints`
- `L0254 p10.1: Another major difference in AI ideas about representation versus search concerns the nature of`
- `L0255 p10.2: the goals. In search, the goal is to find a specific, ideally optimal, “path” through the tree. Agents`

### 008. Satisfying constraints

- level: 2; pages: 10-11; lines: 253-285; words: 482

start sample:
- `L0253 p10.0: 3.3 Satisfying constraints`
- `L0254 p10.1: Another major difference in AI ideas about representation versus search concerns the nature of`
- `L0255 p10.2: the goals. In search, the goal is to find a specific, ideally optimal, “path” through the tree. Agents`

end sample:
- `L0282 p10.31: if/then logic where violating a constraint ends the possibility of a solution, soft constraints are`
- `L0283 p11.0: defined in terms of probabilities that impose a “cost” on violating the constraint such that it may`
- `L0284 p11.1: still be part of a solution.`

start boundary context:
- `L0251 p9.35: right offers richer propagation, whereas the one on the left has less opportunities to propagate`
- `L0252 p9.36: information across the constraints.`
- `L0253 p10.0: 3.3 Satisfying constraints`
- `L0254 p10.1: Another major difference in AI ideas about representation versus search concerns the nature of`
- `L0255 p10.2: the goals. In search, the goal is to find a specific, ideally optimal, “path” through the tree. Agents`

end boundary context:
- `L0283 p11.0: defined in terms of probabilities that impose a “cost” on violating the constraint such that it may`
- `L0284 p11.1: still be part of a solution.`
- `L0285 p11.3: 4. Four types of constraint networks used in AI`
- `L0286 p11.4: The ideas of constraint propagation and constraint satisfaction characterize the overall idea of`
- `L0287 p11.5: using representations as a strategy for intelligence in AI systems and organizations. The precise`

### 009. Four types of constraint networks used in AI

- level: 1; pages: 11-11; lines: 285-295; words: 134

start sample:
- `L0285 p11.3: 4. Four types of constraint networks used in AI`
- `L0286 p11.4: The ideas of constraint propagation and constraint satisfaction characterize the overall idea of`
- `L0287 p11.5: using representations as a strategy for intelligence in AI systems and organizations. The precise`

end sample:
- `L0292 p11.10: of the AI ideas of constraints and propagation — (1) constraint satisfaction problems; (2) causal`
- `L0293 p11.11: nets; (3) Boltzmann machines — that will give you a broad basis for linking our discussion of`
- `L0294 p11.12: representations to their effects on intelligence in AI systems and organizations.`

start boundary context:
- `L0283 p11.0: defined in terms of probabilities that impose a “cost” on violating the constraint such that it may`
- `L0284 p11.1: still be part of a solution.`
- `L0285 p11.3: 4. Four types of constraint networks used in AI`
- `L0286 p11.4: The ideas of constraint propagation and constraint satisfaction characterize the overall idea of`
- `L0287 p11.5: using representations as a strategy for intelligence in AI systems and organizations. The precise`

end boundary context:
- `L0293 p11.11: nets; (3) Boltzmann machines — that will give you a broad basis for linking our discussion of`
- `L0294 p11.12: representations to their effects on intelligence in AI systems and organizations.`
- `L0295 p11.14: 4.1 Constraint satisfaction problems (CSPs)`
- `L0296 p11.15: For given problems where the goal is to find a single solution (e.g. Sudoku), you can think of`
- `L0297 p11.16: constraint satisfaction as almost like a new type of search that interleaves representations. The`

### 010. Constraint satisfaction problems (CSPs)

- level: 2; pages: 11-12; lines: 295-340; words: 673

start sample:
- `L0295 p11.14: 4.1 Constraint satisfaction problems (CSPs)`
- `L0296 p11.15: For given problems where the goal is to find a single solution (e.g. Sudoku), you can think of`
- `L0297 p11.16: constraint satisfaction as almost like a new type of search that interleaves representations. The`

end sample:
- `L0337 p12.20: still usually be reached in the same way even if we had a vastly more complex scheduling`
- `L0338 p12.21: problem (e.g., if we had a product with 1,000 parts, which involved many specialists, complex`
- `L0339 p12.22: materials and shipments, etc.).`

start boundary context:
- `L0293 p11.11: nets; (3) Boltzmann machines — that will give you a broad basis for linking our discussion of`
- `L0294 p11.12: representations to their effects on intelligence in AI systems and organizations.`
- `L0295 p11.14: 4.1 Constraint satisfaction problems (CSPs)`
- `L0296 p11.15: For given problems where the goal is to find a single solution (e.g. Sudoku), you can think of`
- `L0297 p11.16: constraint satisfaction as almost like a new type of search that interleaves representations. The`

end boundary context:
- `L0338 p12.21: problem (e.g., if we had a product with 1,000 parts, which involved many specialists, complex`
- `L0339 p12.22: materials and shipments, etc.).`
- `L0340 p12.24: 4.2 Causal nets`
- `L0341 p12.25: In CSPs, there are no challenges of superstitious or sparse learning. In scheduling tasks for the`
- `L0342 p12.26: pin factory, for example, we assumed that we knew the goal and the actions (i.e., tasks) to`

### 011. Causal nets

- level: 2; pages: 12-14; lines: 340-393; words: 774

start sample:
- `L0340 p12.24: 4.2 Causal nets`
- `L0341 p12.25: In CSPs, there are no challenges of superstitious or sparse learning. In scheduling tasks for the`
- `L0342 p12.26: pin factory, for example, we assumed that we knew the goal and the actions (i.e., tasks) to`

end sample:
- `L0390 p13.38: offer an alternative view of problem-solving in organizations (as well as AI systems) as driven`
- `L0391 p14.0: by cause-effect reasoning, rather than just the trial-and-error, heuristics, or statistical prediction`
- `L0392 p14.1: mechanisms that we have focused on so far.`

start boundary context:
- `L0338 p12.21: problem (e.g., if we had a product with 1,000 parts, which involved many specialists, complex`
- `L0339 p12.22: materials and shipments, etc.).`
- `L0340 p12.24: 4.2 Causal nets`
- `L0341 p12.25: In CSPs, there are no challenges of superstitious or sparse learning. In scheduling tasks for the`
- `L0342 p12.26: pin factory, for example, we assumed that we knew the goal and the actions (i.e., tasks) to`

end boundary context:
- `L0391 p14.0: by cause-effect reasoning, rather than just the trial-and-error, heuristics, or statistical prediction`
- `L0392 p14.1: mechanisms that we have focused on so far.`
- `L0393 p14.3: 4.3 Expert systems`
- `L0394 p14.4: Representations that are acquired and stored as heuristics for solving problems — that is, based`
- `L0395 p14.5: on search — is done in what is called an expert system. In an expert system, domain experts’`

### 012. Expert systems

- level: 2; pages: 14-15; lines: 393-429; words: 512

start sample:
- `L0393 p14.3: 4.3 Expert systems`
- `L0394 p14.4: Representations that are acquired and stored as heuristics for solving problems — that is, based`
- `L0395 p14.5: on search — is done in what is called an expert system. In an expert system, domain experts’`

end sample:
- `L0426 p15.0: Wittgenstein, the famous AI critic Hubert Dreyfus (1965) called this the issue of infinite`
- `L0427 p15.1: regress, meaning that one would theoretically need an infinite number of rules to capture all the`
- `L0428 p15.2: contingencies that could happen, even in a narrow problem-solving domain.`

start boundary context:
- `L0391 p14.0: by cause-effect reasoning, rather than just the trial-and-error, heuristics, or statistical prediction`
- `L0392 p14.1: mechanisms that we have focused on so far.`
- `L0393 p14.3: 4.3 Expert systems`
- `L0394 p14.4: Representations that are acquired and stored as heuristics for solving problems — that is, based`
- `L0395 p14.5: on search — is done in what is called an expert system. In an expert system, domain experts’`

end boundary context:
- `L0427 p15.1: regress, meaning that one would theoretically need an infinite number of rules to capture all the`
- `L0428 p15.2: contingencies that could happen, even in a narrow problem-solving domain.`
- `L0429 p15.4: 4.4 Boltzmann machines and deep learning`
- `L0430 p15.5: Another idea about constraint networks called Boltzmann machines — invented by the recent`
- `L0431 p15.6: Nobel Prize in physics and deep learning leader Geoff Hinton — is perhaps the foundational`

### 013. Boltzmann machines and deep learning

- level: 2; pages: 15-16; lines: 429-470; words: 573

start sample:
- `L0429 p15.4: 4.4 Boltzmann machines and deep learning`
- `L0430 p15.5: Another idea about constraint networks called Boltzmann machines — invented by the recent`
- `L0431 p15.6: Nobel Prize in physics and deep learning leader Geoff Hinton — is perhaps the foundational`

end sample:
- `L0467 p16.5: then be the basis for “learning” representations of problems, making predictions and, ultimately,`
- `L0468 p16.6: decisions. As we will discuss next, this deep learning-driven vision of how organizations will be`
- `L0469 p16.7: intelligent is, however, contested, in a debate that can be traced back to the early days of AI.`

start boundary context:
- `L0427 p15.1: regress, meaning that one would theoretically need an infinite number of rules to capture all the`
- `L0428 p15.2: contingencies that could happen, even in a narrow problem-solving domain.`
- `L0429 p15.4: 4.4 Boltzmann machines and deep learning`
- `L0430 p15.5: Another idea about constraint networks called Boltzmann machines — invented by the recent`
- `L0431 p15.6: Nobel Prize in physics and deep learning leader Geoff Hinton — is perhaps the foundational`

end boundary context:
- `L0468 p16.6: decisions. As we will discuss next, this deep learning-driven vision of how organizations will be`
- `L0469 p16.7: intelligent is, however, contested, in a debate that can be traced back to the early days of AI.`
- `L0470 p16.10: 5. What can constraint networks tell us about intelligence in AI and organizations?:`
- `L0471 p16.11: Paradigmatically-different approaches`
- `L0472 p16.12: We have taken a long journey in this week’s course notes from some familiar examples of`

### 014. What can constraint networks tell us about intelligence in AI and organizations?:

- level: 1; pages: 16-17; lines: 470-505; words: 286

start sample:
- `L0470 p16.10: 5. What can constraint networks tell us about intelligence in AI and organizations?:`
- `L0471 p16.11: Paradigmatically-different approaches`
- `L0472 p16.12: We have taken a long journey in this week’s course notes from some familiar examples of`

end sample:
- `L0502 p17.2: Outcome of Constraint Evaluating whether Learning precise Learning a probability`
- `L0503 p17.3: Propagation constraints are satisfied or cause-effect relations distribution`
- `L0504 p17.4: not`

start boundary context:
- `L0468 p16.6: decisions. As we will discuss next, this deep learning-driven vision of how organizations will be`
- `L0469 p16.7: intelligent is, however, contested, in a debate that can be traced back to the early days of AI.`
- `L0470 p16.10: 5. What can constraint networks tell us about intelligence in AI and organizations?:`
- `L0471 p16.11: Paradigmatically-different approaches`
- `L0472 p16.12: We have taken a long journey in this week’s course notes from some familiar examples of`

end boundary context:
- `L0503 p17.3: Propagation constraints are satisfied or cause-effect relations distribution`
- `L0504 p17.4: not`
- `L0505 p17.6: 5.1 The satisficing perspective in causal nets and other “mental models”`
- `L0506 p17.7: Pearl intended causal nets to define the essence of reasoning about a given problem where the`
- `L0507 p17.8: causes are uncertain. By “given problem”, I mean that we know what the problem is and are`

### 015. The satisficing perspective in causal nets and other “mental models”

- level: 2; pages: 17-17; lines: 505-517; words: 167

start sample:
- `L0505 p17.6: 5.1 The satisficing perspective in causal nets and other “mental models”`
- `L0506 p17.7: Pearl intended causal nets to define the essence of reasoning about a given problem where the`
- `L0507 p17.8: causes are uncertain. By “given problem”, I mean that we know what the problem is and are`

end sample:
- `L0514 p17.15: causal nets is that they assume that intelligence arises from having highly simplified`
- `L0515 p17.16: representations of the world that enable rational behavior under limited information — or what`
- `L0516 p17.17: Simon called satisficing.`

start boundary context:
- `L0503 p17.3: Propagation constraints are satisfied or cause-effect relations distribution`
- `L0504 p17.4: not`
- `L0505 p17.6: 5.1 The satisficing perspective in causal nets and other “mental models”`
- `L0506 p17.7: Pearl intended causal nets to define the essence of reasoning about a given problem where the`
- `L0507 p17.8: causes are uncertain. By “given problem”, I mean that we know what the problem is and are`

end boundary context:
- `L0515 p17.16: representations of the world that enable rational behavior under limited information — or what`
- `L0516 p17.17: Simon called satisficing.`
- `L0517 p17.19: 5.4.2 Deep learning’s physics perspective`
- `L0518 p17.20: Hinton intended the Boltzmann machine to relate to a general purpose way of representing,`
- `L0519 p17.21: making predictions about, and generating new data about, any problem in the universe. It reduces`

### 016. Deep learning’s physics perspective

- level: 3; pages: 17-17; lines: 517-530; words: 171

start sample:
- `L0517 p17.19: 5.4.2 Deep learning’s physics perspective`
- `L0518 p17.20: Hinton intended the Boltzmann machine to relate to a general purpose way of representing,`
- `L0519 p17.21: making predictions about, and generating new data about, any problem in the universe. It reduces`

end sample:
- `L0527 p17.29: be reduced to a few laws and homogenous parts (e.g., “neurons”, or units of Shannon`
- `L0528 p17.30: information). The examples of representations given earlier in this session would, in this view,`
- `L0529 p17.31: simply be generated from such basic building blocks, and not the essence of intelligence itself.`

start boundary context:
- `L0515 p17.16: representations of the world that enable rational behavior under limited information — or what`
- `L0516 p17.17: Simon called satisficing.`
- `L0517 p17.19: 5.4.2 Deep learning’s physics perspective`
- `L0518 p17.20: Hinton intended the Boltzmann machine to relate to a general purpose way of representing,`
- `L0519 p17.21: making predictions about, and generating new data about, any problem in the universe. It reduces`

end boundary context:
- `L0528 p17.30: information). The examples of representations given earlier in this session would, in this view,`
- `L0529 p17.31: simply be generated from such basic building blocks, and not the essence of intelligence itself.`
- `L0530 p17.33: 5.4.3 The knowledge representation and reasoning (KRR) perspective implied by CSPs`
- `L0531 p17.34: In the examples that we looked at earlier, the constraints were given, rather than learned — just`
- `L0532 p17.35: as in the first AI idea that we covered of constraint satisfaction and CSPs. Unlike mental`

### 017. The knowledge representation and reasoning (KRR) perspective implied by CSPs

- level: 3; pages: 17-18; lines: 530-556; words: 346

start sample:
- `L0530 p17.33: 5.4.3 The knowledge representation and reasoning (KRR) perspective implied by CSPs`
- `L0531 p17.34: In the examples that we looked at earlier, the constraints were given, rather than learned — just`
- `L0532 p17.35: as in the first AI idea that we covered of constraint satisfaction and CSPs. Unlike mental`

end sample:
- `L0553 p18.15: machines would simply be two types of highly specialized constraints (i.e., for causal reasoning`
- `L0554 p18.16: and statistical pattern identification), among a diversity of knowledge representations needed for`
- `L0555 p18.17: general intelligence.`

start boundary context:
- `L0528 p17.30: information). The examples of representations given earlier in this session would, in this view,`
- `L0529 p17.31: simply be generated from such basic building blocks, and not the essence of intelligence itself.`
- `L0530 p17.33: 5.4.3 The knowledge representation and reasoning (KRR) perspective implied by CSPs`
- `L0531 p17.34: In the examples that we looked at earlier, the constraints were given, rather than learned — just`
- `L0532 p17.35: as in the first AI idea that we covered of constraint satisfaction and CSPs. Unlike mental`

end boundary context:
- `L0554 p18.16: and statistical pattern identification), among a diversity of knowledge representations needed for`
- `L0555 p18.17: general intelligence.`
