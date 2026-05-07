# Section Manifest Review: notes_evolutionary_strategies

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

- source_pdf: `docs/course-notes/Course Notes — Evolutionary Strategies - FAB Spring 2026.pdf`
- doc_id: `notes_evolutionary_strategies`
- title: Evolutionary Strategies
- target_manifest: `.rag/manifests/notes_evolutionary_strategies.sections.json`
- source_kind: existing manifest
- source_sha_status: fresh
- extracted_lines: 385
- current_sections: 12

## Review Checklist

- Does every top-level/subsection heading start a sensible chunk?
- Are tiny heading-only chunks merged with their following explanatory section when useful?
- Are very large sections split at meaningful internal headings or topic turns?
- Do start/end snippets show missing text, duplicated text, or page-order extraction problems?
- Are page ranges and titles still accurate after any edits?

## Commands

```bash
uv run python scripts/rag.py review-sections --doc-id notes_evolutionary_strategies --write
uv run python scripts/rag.py index
```

## Current Sections

### 001. Introduction

- level: 1; pages: 1-2; lines: 0-40; words: 502

start sample:
- `L0000 p1.0: Course Notes — SESSION 2`
- `L0001 p1.1: EVOLUTIONARY STRATEGIES`
- `L0002 p1.3: 1. Introduction`

end sample:
- `L0037 p2.1: paradigm — which we will call the biological systems approach for its inspiration in`
- `L0038 p2.2: how evolution happens at the level of more complex units such as cells or organisms —`
- `L0039 p2.3: adaptation is viewed as requiring distinct ways of manipulating symbols beyond search.`

start boundary context:
- `L0000 p1.0: Course Notes — SESSION 2`
- `L0001 p1.1: EVOLUTIONARY STRATEGIES`
- `L0002 p1.3: 1. Introduction`

end boundary context:
- `L0038 p2.2: how evolution happens at the level of more complex units such as cells or organisms —`
- `L0039 p2.3: adaptation is viewed as requiring distinct ways of manipulating symbols beyond search.`
- `L0040 p2.6: 2. Adaptation: linking evolution to problem-solving in AI systems and organizations`
- `L0041 p2.7: Evolutionary strategies in AI systems and organizations can be traced to the work of`
- `L0042 p2.8: Charles Darwin in the 19th century. Though Darwinism is familiarly thought of in terms`

### 002. Adaptation: linking evolution to problem-solving in AI systems and organizations

- level: 1; pages: 2-2; lines: 40-50; words: 128

start sample:
- `L0040 p2.6: 2. Adaptation: linking evolution to problem-solving in AI systems and organizations`
- `L0041 p2.7: Evolutionary strategies in AI systems and organizations can be traced to the work of`
- `L0042 p2.8: Charles Darwin in the 19th century. Though Darwinism is familiarly thought of in terms`

end sample:
- `L0047 p2.13: in the environment. In the parlance of our course, adaptation is essentially a`
- `L0048 p2.14: generate-and-test strategy for assigning credit at the population-level (e.g., among a`
- `L0049 p2.15: population of pin factories or organisms in a species).`

start boundary context:
- `L0038 p2.2: how evolution happens at the level of more complex units such as cells or organisms —`
- `L0039 p2.3: adaptation is viewed as requiring distinct ways of manipulating symbols beyond search.`
- `L0040 p2.6: 2. Adaptation: linking evolution to problem-solving in AI systems and organizations`
- `L0041 p2.7: Evolutionary strategies in AI systems and organizations can be traced to the work of`
- `L0042 p2.8: Charles Darwin in the 19th century. Though Darwinism is familiarly thought of in terms`

end boundary context:
- `L0048 p2.14: generate-and-test strategy for assigning credit at the population-level (e.g., among a`
- `L0049 p2.15: population of pin factories or organisms in a species).`
- `L0050 p2.17: 2.1. The magic of adaptation`
- `L0051 p2.18: In AI, the magic of evolution is that some simple rules such as the market mechanism —`
- `L0052 p2.19: and more generally called evolutionary operators — can be astonishingly powerful for`

### 003. The magic of adaptation

- level: 2; pages: 2-3; lines: 50-76; words: 325

start sample:
- `L0050 p2.17: 2.1. The magic of adaptation`
- `L0051 p2.18: In AI, the magic of evolution is that some simple rules such as the market mechanism —`
- `L0052 p2.19: and more generally called evolutionary operators — can be astonishingly powerful for`

end sample:
- `L0073 p3.2: problem. The intuition is similar to how, in evolution, “survival of the fittest” applies to`
- `L0074 p3.3: organisms that perform well (i.e., survive and reproduce) in specific niches (e.g., hippos`
- `L0075 p3.4: in the tropics; penguins in Antarctica) rather than the whole world.`

start boundary context:
- `L0048 p2.14: generate-and-test strategy for assigning credit at the population-level (e.g., among a`
- `L0049 p2.15: population of pin factories or organisms in a species).`
- `L0050 p2.17: 2.1. The magic of adaptation`
- `L0051 p2.18: In AI, the magic of evolution is that some simple rules such as the market mechanism —`
- `L0052 p2.19: and more generally called evolutionary operators — can be astonishingly powerful for`

end boundary context:
- `L0074 p3.3: organisms that perform well (i.e., survive and reproduce) in specific niches (e.g., hippos`
- `L0075 p3.4: in the tropics; penguins in Antarctica) rather than the whole world.`
- `L0076 p3.6: 2.2 Visualizing adaptive processes with performance landscapes`
- `L0077 p3.7: The process of adaptively search for higher fitness in a problem-solving environment can`
- `L0078 p3.8: be usefully visualized through the metaphor of a performance landscape. A performance`

### 004. Visualizing adaptive processes with performance landscapes

- level: 2; pages: 3-4; lines: 76-123; words: 614

start sample:
- `L0076 p3.6: 2.2 Visualizing adaptive processes with performance landscapes`
- `L0077 p3.7: The process of adaptively search for higher fitness in a problem-solving environment can`
- `L0078 p3.8: be usefully visualized through the metaphor of a performance landscape. A performance`

end sample:
- `L0120 p4.14: right in the T-maze. In search, the basic process is the use of heuristics. We will see other`
- `L0121 p4.15: ideas throughout the course. Most generally, action processes are based on encoding and`
- `L0122 p4.16: decoding bit strings in Shannon information, and interpreting lists in Simon information.`

start boundary context:
- `L0074 p3.3: organisms that perform well (i.e., survive and reproduce) in specific niches (e.g., hippos`
- `L0075 p3.4: in the tropics; penguins in Antarctica) rather than the whole world.`
- `L0076 p3.6: 2.2 Visualizing adaptive processes with performance landscapes`
- `L0077 p3.7: The process of adaptively search for higher fitness in a problem-solving environment can`
- `L0078 p3.8: be usefully visualized through the metaphor of a performance landscape. A performance`

end boundary context:
- `L0121 p4.15: ideas throughout the course. Most generally, action processes are based on encoding and`
- `L0122 p4.16: decoding bit strings in Shannon information, and interpreting lists in Simon information.`
- `L0123 p4.19: 3. Landscape topologies`
- `L0124 p4.20: The topology of a landscape depicts differences in the quality of solutions in a population`
- `L0125 p4.21: that we may expect to see. The “landscape” can be composed of “hills”, “valleys”, or`

### 005. Landscape topologies

- level: 1; pages: 4-4; lines: 123-129; words: 74
- review_flags: short_chunk

start sample:
- `L0123 p4.19: 3. Landscape topologies`
- `L0124 p4.20: The topology of a landscape depicts differences in the quality of solutions in a population`
- `L0125 p4.21: that we may expect to see. The “landscape” can be composed of “hills”, “valleys”, or`

start boundary context:
- `L0121 p4.15: ideas throughout the course. Most generally, action processes are based on encoding and`
- `L0122 p4.16: decoding bit strings in Shannon information, and interpreting lists in Simon information.`
- `L0123 p4.19: 3. Landscape topologies`
- `L0124 p4.20: The topology of a landscape depicts differences in the quality of solutions in a population`
- `L0125 p4.21: that we may expect to see. The “landscape” can be composed of “hills”, “valleys”, or`

end boundary context:
- `L0127 p4.23: landscape, with gentle slopes, a landscape with multiple fitness peaks, called a “rugged”`
- `L0128 p4.24: landscape, or one with no peaks and just thresholds (a “mesa” landscape).`
- `L0129 p4.26: 3.1 Single-peaked landscapes: hill-climbing (a.k.a., gradient descent)`
- `L0130 p4.27: Perhaps the simplest “journey” in a performance landscape is a simple trial-and-error`
- `L0131 p4.28: learning strategy. The trial-and-error feedback can be depicted by “hills” or “gradients”`

### 006. Single-peaked landscapes: hill-climbing (a.k.a., gradient descent)

- level: 2; pages: 4-5; lines: 129-152; words: 291

start sample:
- `L0129 p4.26: 3.1 Single-peaked landscapes: hill-climbing (a.k.a., gradient descent)`
- `L0130 p4.27: Perhaps the simplest “journey” in a performance landscape is a simple trial-and-error`
- `L0131 p4.28: learning strategy. The trial-and-error feedback can be depicted by “hills” or “gradients”`

end sample:
- `L0149 p5.12: yet incredibly long journey. For example, in organizations, the single peak may refer to`
- `L0150 p5.13: the design of some complex product or system of activities that only becomes`
- `L0151 p5.14: competitive in the market if some single optimal configuration is achieved.`

start boundary context:
- `L0127 p4.23: landscape, with gentle slopes, a landscape with multiple fitness peaks, called a “rugged”`
- `L0128 p4.24: landscape, or one with no peaks and just thresholds (a “mesa” landscape).`
- `L0129 p4.26: 3.1 Single-peaked landscapes: hill-climbing (a.k.a., gradient descent)`
- `L0130 p4.27: Perhaps the simplest “journey” in a performance landscape is a simple trial-and-error`
- `L0131 p4.28: learning strategy. The trial-and-error feedback can be depicted by “hills” or “gradients”`

end boundary context:
- `L0150 p5.13: the design of some complex product or system of activities that only becomes`
- `L0151 p5.14: competitive in the market if some single optimal configuration is achieved.`
- `L0152 p5.16: 3.2 Rugged landscapes: hill-climbing and long-jumps`
- `L0153 p5.17: Let us go back to the earlier example of designing four components of a laptop — the`
- `L0154 p5.18: screen, CPU, memory, and keyboard. Let us call each component’s effect on performance`

### 007. Rugged landscapes: hill-climbing and long-jumps

- level: 2; pages: 5-7; lines: 152-209; words: 770

start sample:
- `L0152 p5.16: 3.2 Rugged landscapes: hill-climbing and long-jumps`
- `L0153 p5.17: Let us go back to the earlier example of designing four components of a laptop — the`
- `L0154 p5.18: screen, CPU, memory, and keyboard. Let us call each component’s effect on performance`

end sample:
- `L0206 p7.10: of product innovation and strategy, where managers continually have to decide whether`
- `L0207 p7.11: to invest their budgets in doing what they do a bit better, or risk doing something`
- `L0208 p7.12: different.`

start boundary context:
- `L0150 p5.13: the design of some complex product or system of activities that only becomes`
- `L0151 p5.14: competitive in the market if some single optimal configuration is achieved.`
- `L0152 p5.16: 3.2 Rugged landscapes: hill-climbing and long-jumps`
- `L0153 p5.17: Let us go back to the earlier example of designing four components of a laptop — the`
- `L0154 p5.18: screen, CPU, memory, and keyboard. Let us call each component’s effect on performance`

end boundary context:
- `L0207 p7.11: to invest their budgets in doing what they do a bit better, or risk doing something`
- `L0208 p7.12: different.`
- `L0209 p7.14: 3.3 Satisficing and the landscape: lowering expectations vs. taking giant strides`
- `L0210 p7.15: We can depict satisficing in a performance landscape simply as a threshold for`
- `L0211 p7.16: performance, reflecting Simon’s term of an aspiration level. Any point higher than the`

### 008. Satisficing and the landscape: lowering expectations vs. taking giant strides

- level: 2; pages: 7-8; lines: 209-262; words: 594

start sample:
- `L0209 p7.14: 3.3 Satisficing and the landscape: lowering expectations vs. taking giant strides`
- `L0210 p7.15: We can depict satisficing in a performance landscape simply as a threshold for`
- `L0211 p7.16: performance, reflecting Simon’s term of an aspiration level. Any point higher than the`

end sample:
- `L0259 p8.40: landscapes or gradients in a lack of gradients for coherently piecing`
- `L0260 p8.41: between trial-and-error learning together the problem.`
- `L0261 p8.42: (sparse learning)`

start boundary context:
- `L0207 p7.11: to invest their budgets in doing what they do a bit better, or risk doing something`
- `L0208 p7.12: different.`
- `L0209 p7.14: 3.3 Satisficing and the landscape: lowering expectations vs. taking giant strides`
- `L0210 p7.15: We can depict satisficing in a performance landscape simply as a threshold for`
- `L0211 p7.16: performance, reflecting Simon’s term of an aspiration level. Any point higher than the`

end boundary context:
- `L0260 p8.41: between trial-and-error learning together the problem.`
- `L0261 p8.42: (sparse learning)`
- `L0262 p9.0: 4. Approaches to adapting on the landscape`
- `L0263 p9.1: What does the landscape metaphor imply for how to assign credit effectively? You can`
- `L0264 p9.2: think of the approach to answering this question as driven by: how well the agents of an`

### 009. Approaches to adapting on the landscape

- level: 1; pages: 9-9; lines: 262-271; words: 114
- review_flags: short_chunk

start sample:
- `L0262 p9.0: 4. Approaches to adapting on the landscape`
- `L0263 p9.1: What does the landscape metaphor imply for how to assign credit effectively? You can`
- `L0264 p9.2: think of the approach to answering this question as driven by: how well the agents of an`

end sample:
- `L0268 p9.6: similarly, view learning to assign credit as fundamentally a matter of balancing the`
- `L0269 p9.7: exploration and exploitation of actions. The third example is closer to the learning in a`
- `L0270 p9.8: society paradigm, and views learning to assign credit as instead a matter of…`

start boundary context:
- `L0260 p8.41: between trial-and-error learning together the problem.`
- `L0261 p8.42: (sparse learning)`
- `L0262 p9.0: 4. Approaches to adapting on the landscape`
- `L0263 p9.1: What does the landscape metaphor imply for how to assign credit effectively? You can`
- `L0264 p9.2: think of the approach to answering this question as driven by: how well the agents of an`

end boundary context:
- `L0269 p9.7: exploration and exploitation of actions. The third example is closer to the learning in a`
- `L0270 p9.8: society paradigm, and views learning to assign credit as instead a matter of…`
- `L0271 p9.10: 4.1 Approach 1a: gene-inspired representations`
- `L0272 p9.11: As a baseline approach, imagine a new category of watch emerging that has many`
- `L0273 p9.12: interdependent features. Assume that the landscape is “rugged”: only a small subset of`

### 010. Approach 1a: gene-inspired representations

- level: 2; pages: 9-10; lines: 271-303; words: 393

start sample:
- `L0271 p9.10: 4.1 Approach 1a: gene-inspired representations`
- `L0272 p9.11: As a baseline approach, imagine a new category of watch emerging that has many`
- `L0273 p9.12: interdependent features. Assume that the landscape is “rugged”: only a small subset of`

end sample:
- `L0300 p10.3: navigate the landscape more easily. In landscape terms, you can think of the effects of`
- `L0301 p10.4: such use of components as “smoothing” the topology of the landscape from steep and`
- `L0302 p10.5: rugged to gentler.`

start boundary context:
- `L0269 p9.7: exploration and exploitation of actions. The third example is closer to the learning in a`
- `L0270 p9.8: society paradigm, and views learning to assign credit as instead a matter of…`
- `L0271 p9.10: 4.1 Approach 1a: gene-inspired representations`
- `L0272 p9.11: As a baseline approach, imagine a new category of watch emerging that has many`
- `L0273 p9.12: interdependent features. Assume that the landscape is “rugged”: only a small subset of`

end boundary context:
- `L0301 p10.4: such use of components as “smoothing” the topology of the landscape from steep and`
- `L0302 p10.5: rugged to gentler.`
- `L0303 p10.7: 4.2 Approach 1b: chromosome-inspired representations`
- `L0304 p10.8: A first approach pioneered by the AI scholar John Holland at the University of Michigan`
- `L0305 p10.9: is called “genetic algorithms”. In genetic algorithms, a schema for representing a`

### 011. Approach 1b: chromosome-inspired representations

- level: 2; pages: 10-11; lines: 303-343; words: 535

start sample:
- `L0303 p10.7: 4.2 Approach 1b: chromosome-inspired representations`
- `L0304 p10.8: A first approach pioneered by the AI scholar John Holland at the University of Michigan`
- `L0305 p10.9: is called “genetic algorithms”. In genetic algorithms, a schema for representing a`

end sample:
- `L0340 p11.15: use this same basic strategy as in reinforcement learning or the baseline “Mendelian”`
- `L0341 p11.16: approach above, but just mix it with some basic abstractions (i.e., chromosomes instead`
- `L0342 p11.17: of individual genes), analogous to Simon’s second watchmaker.`

start boundary context:
- `L0301 p10.4: such use of components as “smoothing” the topology of the landscape from steep and`
- `L0302 p10.5: rugged to gentler.`
- `L0303 p10.7: 4.2 Approach 1b: chromosome-inspired representations`
- `L0304 p10.8: A first approach pioneered by the AI scholar John Holland at the University of Michigan`
- `L0305 p10.9: is called “genetic algorithms”. In genetic algorithms, a schema for representing a`

end boundary context:
- `L0341 p11.16: approach above, but just mix it with some basic abstractions (i.e., chromosomes instead`
- `L0342 p11.17: of individual genes), analogous to Simon’s second watchmaker.`
- `L0343 p11.19: 4.3 Approach 2: biological systems-inspired schemas`
- `L0344 p11.20: A second approach, pioneered by Marvin Minsky’s student Gerald Sussman at MIT, is`
- `L0345 p11.21: called the “propagator model”. In the propagator model, a schema for representing a`

### 012. Approach 2: biological systems-inspired schemas

- level: 2; pages: 11-12; lines: 343-385; words: 534

start sample:
- `L0343 p11.19: 4.3 Approach 2: biological systems-inspired schemas`
- `L0344 p11.20: A second approach, pioneered by Marvin Minsky’s student Gerald Sussman at MIT, is`
- `L0345 p11.21: called the “propagator model”. In the propagator model, a schema for representing a`

end sample:
- `L0382 p12.22: Hence, something like Sussman’s propagator model is needed to construct an`
- `L0383 p12.23: understanding of the structure of a problem in terms of stable functions (constraints) and`
- `L0384 p12.24: how a variety of solutions might satisfy these constraints.`

start boundary context:
- `L0341 p11.16: approach above, but just mix it with some basic abstractions (i.e., chromosomes instead`
- `L0342 p11.17: of individual genes), analogous to Simon’s second watchmaker.`
- `L0343 p11.19: 4.3 Approach 2: biological systems-inspired schemas`
- `L0344 p11.20: A second approach, pioneered by Marvin Minsky’s student Gerald Sussman at MIT, is`
- `L0345 p11.21: called the “propagator model”. In the propagator model, a schema for representing a`

end boundary context:
- `L0383 p12.23: understanding of the structure of a problem in terms of stable functions (constraints) and`
- `L0384 p12.24: how a variety of solutions might satisfy these constraints.`
