# Section Manifest Review: notes_search

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

- source_pdf: `docs/course-notes/Course Notes — Search - FAB - Spring 2026.pdf`
- doc_id: `notes_search`
- title: Search
- target_manifest: `.rag/manifests/notes_search.sections.json`
- source_kind: existing manifest
- source_sha_status: fresh
- extracted_lines: 408
- current_sections: 16

## Review Checklist

- Does every top-level/subsection heading start a sensible chunk?
- Are tiny heading-only chunks merged with their following explanatory section when useful?
- Are very large sections split at meaningful internal headings or topic turns?
- Do start/end snippets show missing text, duplicated text, or page-order extraction problems?
- Are page ranges and titles still accurate after any edits?

## Commands

```bash
uv run python scripts/rag.py review-sections --doc-id notes_search --write
uv run python scripts/rag.py index
```

## Current Sections

### 001. Introduction

- level: 1; pages: 1-2; lines: 0-59; words: 764

start sample:
- `L0000 p1.0: Course Notes — SESSION 3`
- `L0001 p1.1: SEARCH`
- `L0002 p1.3: 1. Introduction`

end sample:
- `L0056 p2.31: approach, which we will call Simon search, after Herbert Simon (1916-2001), instead`
- `L0057 p2.32: conjures search as an open-ended process of understanding and structuring an ill-defined`
- `L0058 p2.33: problem, such as an entrepreneur developing a new product for an uncertain market.`

start boundary context:
- `L0000 p1.0: Course Notes — SESSION 3`
- `L0001 p1.1: SEARCH`
- `L0002 p1.3: 1. Introduction`

end boundary context:
- `L0057 p2.32: conjures search as an open-ended process of understanding and structuring an ill-defined`
- `L0058 p2.33: problem, such as an entrepreneur developing a new product for an uncertain market.`
- `L0059 p2.36: 2. Plans: dividing the labor of problem-solving`
- `L0060 p2.37: In AI textbooks, search is commonly introduced by the example of planning the shortest`
- `L0061 p2.38: route to travel from A to B, such as from home to the airport, where the nodes in between`

### 002. Plans: dividing the labor of problem-solving

- level: 1; pages: 2-3; lines: 59-71; words: 171

start sample:
- `L0059 p2.36: 2. Plans: dividing the labor of problem-solving`
- `L0060 p2.37: In AI textbooks, search is commonly introduced by the example of planning the shortest`
- `L0061 p2.38: route to travel from A to B, such as from home to the airport, where the nodes in between`

end sample:
- `L0068 p3.5: examples of computers. The payoff of this detour will be a basis for understanding the`
- `L0069 p3.6: foundational AI idea of search less in terms of optimizing a route from A to B, and more`
- `L0070 p3.7: as a fundamental approach to assigning credit for any complex real-world problem.`

start boundary context:
- `L0057 p2.32: conjures search as an open-ended process of understanding and structuring an ill-defined`
- `L0058 p2.33: problem, such as an entrepreneur developing a new product for an uncertain market.`
- `L0059 p2.36: 2. Plans: dividing the labor of problem-solving`
- `L0060 p2.37: In AI textbooks, search is commonly introduced by the example of planning the shortest`
- `L0061 p2.38: route to travel from A to B, such as from home to the airport, where the nodes in between`

end boundary context:
- `L0069 p3.6: foundational AI idea of search less in terms of optimizing a route from A to B, and more`
- `L0070 p3.7: as a fundamental approach to assigning credit for any complex real-world problem.`
- `L0071 p3.9: 2.1 The division of labor as a general solution to credit assignment`
- `L0072 p3.10: The modern concept of dividing the labor of a problem dates back to the start of the`
- `L0073 p3.11: industrial revolution in 18th century Europe. The Scottish economist Adam Smith`

### 003. The division of labor as a general solution to credit assignment

- level: 2; pages: 3-4; lines: 71-98; words: 381

start sample:
- `L0071 p3.9: 2.1 The division of labor as a general solution to credit assignment`
- `L0072 p3.10: The modern concept of dividing the labor of a problem dates back to the start of the`
- `L0073 p3.11: industrial revolution in 18th century Europe. The Scottish economist Adam Smith`

end sample:
- `L0095 p4.2: pins, but equally to any problems of thinking; further, if thinking problems can be divided`
- `L0096 p4.3: into simple enough mental tasks, it is possible to mechanize thought by building a general`
- `L0097 p4.4: purpose “thinking machine”.`

start boundary context:
- `L0069 p3.6: foundational AI idea of search less in terms of optimizing a route from A to B, and more`
- `L0070 p3.7: as a fundamental approach to assigning credit for any complex real-world problem.`
- `L0071 p3.9: 2.1 The division of labor as a general solution to credit assignment`
- `L0072 p3.10: The modern concept of dividing the labor of a problem dates back to the start of the`
- `L0073 p3.11: industrial revolution in 18th century Europe. The Scottish economist Adam Smith`

end boundary context:
- `L0096 p4.3: into simple enough mental tasks, it is possible to mechanize thought by building a general`
- `L0097 p4.4: purpose “thinking machine”.`
- `L0098 p4.6: 2.2 Dividing labor into plans (programs)`
- `L0099 p4.7: Babbage’s analytic engine was inspired by a newly invented technology at the time called`
- `L0100 p4.8: the Jacquard loom, in which the pattern to be woven into a fabric could be mechanized`

### 004. Dividing labor into plans (programs)

- level: 2; pages: 4-4; lines: 98-117; words: 247

start sample:
- `L0098 p4.6: 2.2 Dividing labor into plans (programs)`
- `L0099 p4.7: Babbage’s analytic engine was inspired by a newly invented technology at the time called`
- `L0100 p4.8: the Jacquard loom, in which the pattern to be woven into a fabric could be mechanized`

end sample:
- `L0114 p4.31: noted that programs could mechanize only subsets of tasks. Hence, intelligent`
- `L0115 p4.32: problem-solving ultimately involved learning a collection of programs (i.e., plans) for`
- `L0116 p4.33: subtasks, and learning to select specific programs for specific tasks as needed.`

start boundary context:
- `L0096 p4.3: into simple enough mental tasks, it is possible to mechanize thought by building a general`
- `L0097 p4.4: purpose “thinking machine”.`
- `L0098 p4.6: 2.2 Dividing labor into plans (programs)`
- `L0099 p4.7: Babbage’s analytic engine was inspired by a newly invented technology at the time called`
- `L0100 p4.8: the Jacquard loom, in which the pattern to be woven into a fabric could be mechanized`

end boundary context:
- `L0115 p4.32: problem-solving ultimately involved learning a collection of programs (i.e., plans) for`
- `L0116 p4.33: subtasks, and learning to select specific programs for specific tasks as needed.`
- `L0117 p4.35: 2.3 Effective procedures as measures of program complexity`
- `L0118 p4.36: Babbage’s proposals imply a complementary view of the complexity of a problem (i.e., of`
- `L0119 p4.37: the challenge of credit assignment) from our previous session, not in terms of the amount`

### 005. Effective procedures as measures of program complexity

- level: 2; pages: 4-5; lines: 117-149; words: 438

start sample:
- `L0117 p4.35: 2.3 Effective procedures as measures of program complexity`
- `L0118 p4.36: Babbage’s proposals imply a complementary view of the complexity of a problem (i.e., of`
- `L0119 p4.37: the challenge of credit assignment) from our previous session, not in terms of the amount`

end sample:
- `L0146 p5.29: Turing and his successors in theories of computation have shown mathematically that as`
- `L0147 p5.30: the program size grows, the complexity of moves and modifications grows`
- `L0148 p5.31: combinatorially.`

start boundary context:
- `L0115 p4.32: problem-solving ultimately involved learning a collection of programs (i.e., plans) for`
- `L0116 p4.33: subtasks, and learning to select specific programs for specific tasks as needed.`
- `L0117 p4.35: 2.3 Effective procedures as measures of program complexity`
- `L0118 p4.36: Babbage’s proposals imply a complementary view of the complexity of a problem (i.e., of`
- `L0119 p4.37: the challenge of credit assignment) from our previous session, not in terms of the amount`

end boundary context:
- `L0147 p5.30: the program size grows, the complexity of moves and modifications grows`
- `L0148 p5.31: combinatorially.`
- `L0149 p5.34: 3. Search processes`
- `L0150 p5.35: Let us return to our earlier depiction of the process of search as structured into nodes`
- `L0151 p5.36: arranged from top to bottom like a hierarchical organization. You can think of the nodes`

### 006. Search processes

- level: 1; pages: 5-6; lines: 149-161; words: 165

start sample:
- `L0149 p5.34: 3. Search processes`
- `L0150 p5.35: Let us return to our earlier depiction of the process of search as structured into nodes`
- `L0151 p5.36: arranged from top to bottom like a hierarchical organization. You can think of the nodes`

end sample:
- `L0158 p6.2: agent to intermediate states until (hopefully) eventually reaching a goal state. The`
- `L0159 p6.3: credit assignment challenge is how to make such transitions efficient, which we look at`
- `L0160 p6.4: next as based on heuristics (3.1), including a special heuristic called satisficing (3.2).`

start boundary context:
- `L0147 p5.30: the program size grows, the complexity of moves and modifications grows`
- `L0148 p5.31: combinatorially.`
- `L0149 p5.34: 3. Search processes`
- `L0150 p5.35: Let us return to our earlier depiction of the process of search as structured into nodes`
- `L0151 p5.36: arranged from top to bottom like a hierarchical organization. You can think of the nodes`

end boundary context:
- `L0159 p6.3: credit assignment challenge is how to make such transitions efficient, which we look at`
- `L0160 p6.4: next as based on heuristics (3.1), including a special heuristic called satisficing (3.2).`
- `L0161 p6.6: 3.1 Search as a heuristic process`
- `L0162 p6.7: We will call any process of transitioning from an initial state to a goal state in a search`
- `L0163 p6.8: tree as a search process. Agents search by generating, evaluating, and selecting among`

### 007. Search as a heuristic process

- level: 2; pages: 6-7; lines: 161-195; words: 414

start sample:
- `L0161 p6.6: 3.1 Search as a heuristic process`
- `L0162 p6.7: We will call any process of transitioning from an initial state to a goal state in a search`
- `L0163 p6.8: tree as a search process. Agents search by generating, evaluating, and selecting among`

end sample:
- `L0192 p7.17: management team might learn rules of testing a product in at least two markets before`
- `L0193 p7.18: investing in scaling it.`
- `L0194 p7.28: Breadth- versus depth-first`

start boundary context:
- `L0159 p6.3: credit assignment challenge is how to make such transitions efficient, which we look at`
- `L0160 p6.4: next as based on heuristics (3.1), including a special heuristic called satisficing (3.2).`
- `L0161 p6.6: 3.1 Search as a heuristic process`
- `L0162 p6.7: We will call any process of transitioning from an initial state to a goal state in a search`
- `L0163 p6.8: tree as a search process. Agents search by generating, evaluating, and selecting among`

end boundary context:
- `L0193 p7.18: investing in scaling it.`
- `L0194 p7.28: Breadth- versus depth-first`
- `L0195 p7.30: 3.2 Search as a satisficing process`
- `L0196 p7.31: Given that an agent cannot evaluate every state of a search tree and must use heuristics, it`
- `L0197 p7.32: cannot be guaranteed of finding the best plan for solving a problem. Based on this`

### 008. Search as a satisficing process

- level: 2; pages: 7-8; lines: 195-228; words: 425

start sample:
- `L0195 p7.30: 3.2 Search as a satisficing process`
- `L0196 p7.31: Given that an agent cannot evaluate every state of a search tree and must use heuristics, it`
- `L0197 p7.32: cannot be guaranteed of finding the best plan for solving a problem. Based on this`

end sample:
- `L0225 p8.19: the complexity is not just that implied by a Turing machine but extends to how processes`
- `L0226 p8.20: for learning and selecting these programs are bound up in complex organizational goals`
- `L0227 p8.21: that map to problems with no clearly “optimal” solution.`

start boundary context:
- `L0193 p7.18: investing in scaling it.`
- `L0194 p7.28: Breadth- versus depth-first`
- `L0195 p7.30: 3.2 Search as a satisficing process`
- `L0196 p7.31: Given that an agent cannot evaluate every state of a search tree and must use heuristics, it`
- `L0197 p7.32: cannot be guaranteed of finding the best plan for solving a problem. Based on this`

end boundary context:
- `L0226 p8.20: for learning and selecting these programs are bound up in complex organizational goals`
- `L0227 p8.21: that map to problems with no clearly “optimal” solution.`
- `L0228 p8.23: 3.3 Paradigmatically-different approaches to search`
- `L0229 p8.24: This section has defined search in general terms as a heuristic process of generating and`
- `L0230 p8.25: evaluating satisfactory plans to solve problems. You can understand search as a general`

### 009. Paradigmatically-different approaches to search

- level: 2; pages: 8-8; lines: 228-244; words: 216

start sample:
- `L0228 p8.23: 3.3 Paradigmatically-different approaches to search`
- `L0229 p8.24: This section has defined search in general terms as a heuristic process of generating and`
- `L0230 p8.25: evaluating satisfactory plans to solve problems. You can understand search as a general`

end sample:
- `L0241 p8.37: builds on the former, conceiving of search as akin to playing a well-defined game. What`
- `L0242 p8.38: we will call Simon search builds on the latter, conceiving of search as understanding and`
- `L0243 p8.39: structuring an ill-defined problem.`

start boundary context:
- `L0226 p8.20: for learning and selecting these programs are bound up in complex organizational goals`
- `L0227 p8.21: that map to problems with no clearly “optimal” solution.`
- `L0228 p8.23: 3.3 Paradigmatically-different approaches to search`
- `L0229 p8.24: This section has defined search in general terms as a heuristic process of generating and`
- `L0230 p8.25: evaluating satisfactory plans to solve problems. You can understand search as a general`

end boundary context:
- `L0242 p8.38: we will call Simon search builds on the latter, conceiving of search as understanding and`
- `L0243 p8.39: structuring an ill-defined problem.`
- `L0244 p9.0: 4. Von Neumann search: search as game-playing`
- `L0245 p9.1: A first approach to search derives from, among others, the seminal work of the`
- `L0246 p9.2: mathematician John von Neumann in the 1930s and 1940s on game theory. You can`

### 010. Von Neumann search: search as game-playing

- level: 1; pages: 9-9; lines: 244-253; words: 116
- review_flags: short_chunk

start sample:
- `L0244 p9.0: 4. Von Neumann search: search as game-playing`
- `L0245 p9.1: A first approach to search derives from, among others, the seminal work of the`
- `L0246 p9.2: mathematician John von Neumann in the 1930s and 1940s on game theory. You can`

end sample:
- `L0250 p9.6: agents’ search for a sequence of actions must consider the strategies of “opponent”`
- `L0251 p9.7: agents. This approach to search has focused on strategies for playing various well-defined`
- `L0252 p9.8: games, from tic-tac-toe to chess, Go, backgammon and many others.`

start boundary context:
- `L0242 p8.38: we will call Simon search builds on the latter, conceiving of search as understanding and`
- `L0243 p8.39: structuring an ill-defined problem.`
- `L0244 p9.0: 4. Von Neumann search: search as game-playing`
- `L0245 p9.1: A first approach to search derives from, among others, the seminal work of the`
- `L0246 p9.2: mathematician John von Neumann in the 1930s and 1940s on game theory. You can`

end boundary context:
- `L0251 p9.7: agents. This approach to search has focused on strategies for playing various well-defined`
- `L0252 p9.8: games, from tic-tac-toe to chess, Go, backgammon and many others.`
- `L0253 p9.10: 4.1 Why games?`
- `L0254 p9.11: Why games? Unlike a simple division of labor problem, such as how to plan the`
- `L0255 p9.12: sequences of three or so tasks in a pin factory, the adversarial nature of even seemingly`

### 011. Why games?

- level: 2; pages: 9-9; lines: 253-275; words: 277

start sample:
- `L0253 p9.10: 4.1 Why games?`
- `L0254 p9.11: Why games? Unlike a simple division of labor problem, such as how to plan the`
- `L0255 p9.12: sequences of three or so tasks in a pin factory, the adversarial nature of even seemingly`

end sample:
- `L0272 p9.31: is called a unitary actor assumption, in that it does not matter much whether one`
- `L0273 p9.32: assumes that nodes are assigned to different agents — the entire search process is`
- `L0274 p9.33: controlled by a single centralized agent.`

start boundary context:
- `L0251 p9.7: agents. This approach to search has focused on strategies for playing various well-defined`
- `L0252 p9.8: games, from tic-tac-toe to chess, Go, backgammon and many others.`
- `L0253 p9.10: 4.1 Why games?`
- `L0254 p9.11: Why games? Unlike a simple division of labor problem, such as how to plan the`
- `L0255 p9.12: sequences of three or so tasks in a pin factory, the adversarial nature of even seemingly`

end boundary context:
- `L0273 p9.32: assumes that nodes are assigned to different agents — the entire search process is`
- `L0274 p9.33: controlled by a single centralized agent.`
- `L0275 p9.35: 4.2 Heuristics defined in terms of economic utility functions`
- `L0276 p9.36: In games such as chess or backgammon where all the rules and, hence, goals are defined,`
- `L0277 p9.37: there is no inherent need for physical symbols. All the information about the game can, in`

### 012. Heuristics defined in terms of economic utility functions

- level: 2; pages: 9-11; lines: 275-309; words: 485

start sample:
- `L0275 p9.35: 4.2 Heuristics defined in terms of economic utility functions`
- `L0276 p9.36: In games such as chess or backgammon where all the rules and, hence, goals are defined,`
- `L0277 p9.37: there is no inherent need for physical symbols. All the information about the game can, in`

end sample:
- `L0306 p10.41: based on various heuristic measures of intermediate feedback. By collapsing these`
- `L0307 p11.0: heuristic measures into a single numerical value for the “utility” of each state, alternative`
- `L0308 p11.1: actions can be ranked to guide the search process (i.e., path selection).`

start boundary context:
- `L0273 p9.32: assumes that nodes are assigned to different agents — the entire search process is`
- `L0274 p9.33: controlled by a single centralized agent.`
- `L0275 p9.35: 4.2 Heuristics defined in terms of economic utility functions`
- `L0276 p9.36: In games such as chess or backgammon where all the rules and, hence, goals are defined,`
- `L0277 p9.37: there is no inherent need for physical symbols. All the information about the game can, in`

end boundary context:
- `L0307 p11.0: heuristic measures into a single numerical value for the “utility” of each state, alternative`
- `L0308 p11.1: actions can be ranked to guide the search process (i.e., path selection).`
- `L0309 p11.3: 4.3 Satisficing by extending the reinforcement paradigm of maximizing rewards`
- `L0310 p11.4: In von Neumann search, since the state of a game can be estimated using the evaluation`
- `L0311 p11.5: function as a single “reward”. Hence, under von Neumann search, where all the rules of a`

### 013. Satisficing by extending the reinforcement paradigm of maximizing rewards

- level: 2; pages: 11-11; lines: 309-329; words: 245

start sample:
- `L0309 p11.3: 4.3 Satisficing by extending the reinforcement paradigm of maximizing rewards`
- `L0310 p11.4: In von Neumann search, since the state of a game can be estimated using the evaluation`
- `L0311 p11.5: function as a single “reward”. Hence, under von Neumann search, where all the rules of a`

end sample:
- `L0326 p11.21: approach to search. You may contrast this with Richard Sutton’s preference to focus on`
- `L0327 p11.22: his reward hypothesis, which focuses on collapsing all such search and other functions to`
- `L0328 p11.23: a single scalar for reward.`

start boundary context:
- `L0307 p11.0: heuristic measures into a single numerical value for the “utility” of each state, alternative`
- `L0308 p11.1: actions can be ranked to guide the search process (i.e., path selection).`
- `L0309 p11.3: 4.3 Satisficing by extending the reinforcement paradigm of maximizing rewards`
- `L0310 p11.4: In von Neumann search, since the state of a game can be estimated using the evaluation`
- `L0311 p11.5: function as a single “reward”. Hence, under von Neumann search, where all the rules of a`

end boundary context:
- `L0327 p11.22: his reward hypothesis, which focuses on collapsing all such search and other functions to`
- `L0328 p11.23: a single scalar for reward.`
- `L0329 p11.26: 5. Simon search: search as means-ends analysis`
- `L0330 p11.27: A second approach pioneered by Simon, along with his colleague at Carnegie-Mellon`
- `L0331 p11.28: Allen Newell, developed by way of contrast with von Neumann-style search and its`

### 014. Simon search: search as means-ends analysis

- level: 1; pages: 11-11; lines: 329-339; words: 121

start sample:
- `L0329 p11.26: 5. Simon search: search as means-ends analysis`
- `L0330 p11.27: A second approach pioneered by Simon, along with his colleague at Carnegie-Mellon`
- `L0331 p11.28: Allen Newell, developed by way of contrast with von Neumann-style search and its`

end sample:
- `L0336 p11.33: open-endedness meant search was not just about coming up with a utility function, and`
- `L0337 p11.34: corresponding evaluation function, but rather of the ability to manipulate physical`
- `L0338 p11.35: symbols to transform some simplified model into a model of some meaningful goal state.`

start boundary context:
- `L0327 p11.22: his reward hypothesis, which focuses on collapsing all such search and other functions to`
- `L0328 p11.23: a single scalar for reward.`
- `L0329 p11.26: 5. Simon search: search as means-ends analysis`
- `L0330 p11.27: A second approach pioneered by Simon, along with his colleague at Carnegie-Mellon`
- `L0331 p11.28: Allen Newell, developed by way of contrast with von Neumann-style search and its`

end boundary context:
- `L0337 p11.34: corresponding evaluation function, but rather of the ability to manipulate physical`
- `L0338 p11.35: symbols to transform some simplified model into a model of some meaningful goal state.`
- `L0339 p11.37: 5.1 Heuristics as general methods for manipulating physical symbols`
- `L0340 p11.38: In Simon search, heuristics are used to inform actions for manipulating physical symbols`
- `L0341 p11.39: in programs. Specifically a program would have: (i) A set of meaningful physical symbols`

### 015. Heuristics as general methods for manipulating physical symbols

- level: 2; pages: 11-13; lines: 339-394; words: 701

start sample:
- `L0339 p11.37: 5.1 Heuristics as general methods for manipulating physical symbols`
- `L0340 p11.38: In Simon search, heuristics are used to inform actions for manipulating physical symbols`
- `L0341 p11.39: in programs. Specifically a program would have: (i) A set of meaningful physical symbols`

end sample:
- `L0391 p13.17: closer to B. Hence, in search, learning works by developing fundamental heuristics that,`
- `L0392 p13.18: given any goal state and initial state, could generally construct and “discover” new`
- `L0393 p13.19: heuristics through the search process itself.`

start boundary context:
- `L0337 p11.34: corresponding evaluation function, but rather of the ability to manipulate physical`
- `L0338 p11.35: symbols to transform some simplified model into a model of some meaningful goal state.`
- `L0339 p11.37: 5.1 Heuristics as general methods for manipulating physical symbols`
- `L0340 p11.38: In Simon search, heuristics are used to inform actions for manipulating physical symbols`
- `L0341 p11.39: in programs. Specifically a program would have: (i) A set of meaningful physical symbols`

end boundary context:
- `L0392 p13.18: given any goal state and initial state, could generally construct and “discover” new`
- `L0393 p13.19: heuristics through the search process itself.`
- `L0394 p13.21: 5.3 Learning as the use of search operations to acquire new heuristics like an expert`
- `L0395 p13.22: Simon realized that a central challenge was how an AI system could have enough diverse`
- `L0396 p13.23: experiences to learn heuristics for solving any problem. This challenge of learning to`

### 016. Learning as the use of search operations to acquire new heuristics like an expert

- level: 2; pages: 13-13; lines: 394-408; words: 189

start sample:
- `L0394 p13.21: 5.3 Learning as the use of search operations to acquire new heuristics like an expert`
- `L0395 p13.22: Simon realized that a central challenge was how an AI system could have enough diverse`
- `L0396 p13.23: experiences to learn heuristics for solving any problem. This challenge of learning to`

end sample:
- `L0405 p13.32: that experts in various fields used heuristics related to “deliberate practice” to learn other`
- `L0406 p13.33: heuristics, or that entrepreneurs used heuristics to construct business ideas in a piecemeal`
- `L0407 p13.34: fashion (a process called “effectuation”) rather than plan things out ahead of time.`

start boundary context:
- `L0392 p13.18: given any goal state and initial state, could generally construct and “discover” new`
- `L0393 p13.19: heuristics through the search process itself.`
- `L0394 p13.21: 5.3 Learning as the use of search operations to acquire new heuristics like an expert`
- `L0395 p13.22: Simon realized that a central challenge was how an AI system could have enough diverse`
- `L0396 p13.23: experiences to learn heuristics for solving any problem. This challenge of learning to`

end boundary context:
- `L0406 p13.33: heuristics, or that entrepreneurs used heuristics to construct business ideas in a piecemeal`
- `L0407 p13.34: fashion (a process called “effectuation”) rather than plan things out ahead of time.`
