# Section Manifest Review: notes_credit_assignment

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

- source_pdf: `docs/course-notes/2026_Course Notes_Ch. 1 — The General Problem of Intelligence_ Credit Assignment - FAB.pdf`
- doc_id: `notes_credit_assignment`
- title: Credit Assignment
- target_manifest: `.rag/manifests/notes_credit_assignment.sections.json`
- source_kind: existing manifest
- source_sha_status: fresh
- extracted_lines: 462
- current_sections: 15

## Review Checklist

- Does every top-level/subsection heading start a sensible chunk?
- Are tiny heading-only chunks merged with their following explanatory section when useful?
- Are very large sections split at meaningful internal headings or topic turns?
- Do start/end snippets show missing text, duplicated text, or page-order extraction problems?
- Are page ranges and titles still accurate after any edits?

## Commands

```bash
uv run python scripts/rag.py review-sections --doc-id notes_credit_assignment --write
uv run python scripts/rag.py index
```

## Current Sections

### 001. Front Matter

- level: 1; pages: 1-2; lines: 0-37; words: 486

start sample:
- `L0000 p1.0: Course Notes — SESSION 1`
- `L0001 p1.1: THE GENERAL PROBLEM OF INTELLIGENCE: CREDIT ASSIGNMENT`
- `L0002 p1.3: In the Course Introduction, we laid out a view of AI and organizations as direct analogs.`

end sample:
- `L0034 p1.39: called reinforcement learning and the other called learning in a “society”. Exploring and`
- `L0035 p2.0: debating tensions among these paradigms (or alternatives to either) as they relate to the general`
- `L0036 p2.1: problem of credit assignment will be a focus of our journey throughout this course.`

start boundary context:
- `L0000 p1.0: Course Notes — SESSION 1`
- `L0001 p1.1: THE GENERAL PROBLEM OF INTELLIGENCE: CREDIT ASSIGNMENT`
- `L0002 p1.3: In the Course Introduction, we laid out a view of AI and organizations as direct analogs.`

end boundary context:
- `L0035 p2.0: debating tensions among these paradigms (or alternatives to either) as they relate to the general`
- `L0036 p2.1: problem of credit assignment will be a focus of our journey throughout this course.`
- `L0037 p2.4: 1. Introducing the credit assignment problem`
- `L0038 p2.5: To introduce the credit assignment problem, let us first consider a few common examples of`
- `L0039 p2.6: learning to solve problems in organizations.`

### 002. Introducing the credit assignment problem

- level: 1; pages: 2-2; lines: 37-62; words: 335

start sample:
- `L0037 p2.4: 1. Introducing the credit assignment problem`
- `L0038 p2.5: To introduce the credit assignment problem, let us first consider a few common examples of`
- `L0039 p2.6: learning to solve problems in organizations.`

end sample:
- `L0059 p2.26: many quarterly meetings, sales consistently increase. The committee claims to have`
- `L0060 p2.27: “learned” how to allocate the budget effectively. Yet many business unit heads believe`
- `L0061 p2.28: sales would have grown even more if more budget had been allocated to their units.`

start boundary context:
- `L0035 p2.0: debating tensions among these paradigms (or alternatives to either) as they relate to the general`
- `L0036 p2.1: problem of credit assignment will be a focus of our journey throughout this course.`
- `L0037 p2.4: 1. Introducing the credit assignment problem`
- `L0038 p2.5: To introduce the credit assignment problem, let us first consider a few common examples of`
- `L0039 p2.6: learning to solve problems in organizations.`

end boundary context:
- `L0060 p2.27: “learned” how to allocate the budget effectively. Yet many business unit heads believe`
- `L0061 p2.28: sales would have grown even more if more budget had been allocated to their units.`
- `L0062 p2.30: 1.1 Individual actions as “generate-and-test” processes`
- `L0063 p2.31: What should you take away from these examples? For one, they embed some shared building`
- `L0064 p2.32: blocks of individual actions that we can use for talking about credit assignment across any AI`

### 003. Individual actions as “generate-and-test” processes

- level: 2; pages: 2-3; lines: 62-81; words: 212

start sample:
- `L0062 p2.30: 1.1 Individual actions as “generate-and-test” processes`
- `L0063 p2.31: What should you take away from these examples? For one, they embed some shared building`
- `L0064 p2.32: blocks of individual actions that we can use for talking about credit assignment across any AI`

end sample:
- `L0078 p3.7: adding or removing app features, or changes to business unit budgets.`
- `L0079 p3.17: FIGURE 1:`
- `L0080 p3.18: Generating, testing, modifying actions to learn to solve problems`

start boundary context:
- `L0060 p2.27: “learned” how to allocate the budget effectively. Yet many business unit heads believe`
- `L0061 p2.28: sales would have grown even more if more budget had been allocated to their units.`
- `L0062 p2.30: 1.1 Individual actions as “generate-and-test” processes`
- `L0063 p2.31: What should you take away from these examples? For one, they embed some shared building`
- `L0064 p2.32: blocks of individual actions that we can use for talking about credit assignment across any AI`

end boundary context:
- `L0079 p3.17: FIGURE 1:`
- `L0080 p3.18: Generating, testing, modifying actions to learn to solve problems`
- `L0081 p3.21: 1.2 Credit assignment as the problem of generating intermediate feedback`
- `L0082 p3.22: The three examples also embed the concept of assigning credit — that of learning to evaluate the`
- `L0083 p3.23: effects of individual actions on solving a problem — as one of effectively using feedback to`

### 004. Credit assignment as the problem of generating intermediate feedback

- level: 2; pages: 3-4; lines: 81-115; words: 466

start sample:
- `L0081 p3.21: 1.2 Credit assignment as the problem of generating intermediate feedback`
- `L0082 p3.22: The three examples also embed the concept of assigning credit — that of learning to evaluate the`
- `L0083 p3.23: effects of individual actions on solving a problem — as one of effectively using feedback to`

end sample:
- `L0112 p4.11: a distinct paradigm he called learning in a “society of mind”. Next, we explore these two`
- `L0113 p4.12: paradigms, both to better understand the idea of credit assignment and to encourage you to start`
- `L0114 p4.13: to think critically about the diverse types of solutions to the problem that may be possible.`

start boundary context:
- `L0079 p3.17: FIGURE 1:`
- `L0080 p3.18: Generating, testing, modifying actions to learn to solve problems`
- `L0081 p3.21: 1.2 Credit assignment as the problem of generating intermediate feedback`
- `L0082 p3.22: The three examples also embed the concept of assigning credit — that of learning to evaluate the`
- `L0083 p3.23: effects of individual actions on solving a problem — as one of effectively using feedback to`

end boundary context:
- `L0113 p4.12: paradigms, both to better understand the idea of credit assignment and to encourage you to start`
- `L0114 p4.13: to think critically about the diverse types of solutions to the problem that may be possible.`
- `L0115 p4.16: 2. Paradigm 1: assigning credit by reinforcement learning`
- `L0116 p4.17: In reinforcement learning, an agent assigns credit simply by “reinforcing” actions that seem to`
- `L0117 p4.18: have the effect of getting it closer to its goal. Any such effects of actions on goals are called`

### 005. Paradigm 1: assigning credit by reinforcement learning

- level: 1; pages: 4-5; lines: 115-148; words: 475

start sample:
- `L0115 p4.16: 2. Paradigm 1: assigning credit by reinforcement learning`
- `L0116 p4.17: In reinforcement learning, an agent assigns credit simply by “reinforcing” actions that seem to`
- `L0117 p4.18: have the effect of getting it closer to its goal. Any such effects of actions on goals are called`

end sample:
- `L0145 p5.7: Updated belief = (learning ratesuccess)*(1 - prior probability of generating action)`
- `L0146 p5.8: or:`
- `L0147 p5.9: Updated belief = (learning ratefailure)*(1 - prior probability of generating action)`

start boundary context:
- `L0113 p4.12: paradigms, both to better understand the idea of credit assignment and to encourage you to start`
- `L0114 p4.13: to think critically about the diverse types of solutions to the problem that may be possible.`
- `L0115 p4.16: 2. Paradigm 1: assigning credit by reinforcement learning`
- `L0116 p4.17: In reinforcement learning, an agent assigns credit simply by “reinforcing” actions that seem to`
- `L0117 p4.18: have the effect of getting it closer to its goal. Any such effects of actions on goals are called`

end boundary context:
- `L0146 p5.8: or:`
- `L0147 p5.9: Updated belief = (learning ratefailure)*(1 - prior probability of generating action)`
- `L0148 p5.11: 2.1 Navigating a T-maze`
- `L0149 p5.12: To concretize the above discussion, let us first look at the use of reinforcement to assign credit in`
- `L0150 p5.13: a simple problem. In fact, let us look at perhaps the simplest type of reinforcement learning`

### 006. Navigating a T-maze

- level: 2; pages: 5-7; lines: 148-227; words: 1091

start sample:
- `L0148 p5.11: 2.1 Navigating a T-maze`
- `L0149 p5.12: To concretize the above discussion, let us first look at the use of reinforcement to assign credit in`
- `L0150 p5.13: a simple problem. In fact, let us look at perhaps the simplest type of reinforcement learning`

end sample:
- `L0224 p7.31: tradeoff. This tradeoff frames the solution to the fundamental problem of credit assignment in`
- `L0225 p7.32: our first AI idea. In reinforcement learning, the solution is simply to design a policy (learning`
- `L0226 p7.33: rate) that balances the trial-and-error exploration and exploitation of beliefs.`

start boundary context:
- `L0146 p5.8: or:`
- `L0147 p5.9: Updated belief = (learning ratefailure)*(1 - prior probability of generating action)`
- `L0148 p5.11: 2.1 Navigating a T-maze`
- `L0149 p5.12: To concretize the above discussion, let us first look at the use of reinforcement to assign credit in`
- `L0150 p5.13: a simple problem. In fact, let us look at perhaps the simplest type of reinforcement learning`

end boundary context:
- `L0225 p7.32: our first AI idea. In reinforcement learning, the solution is simply to design a policy (learning`
- `L0226 p7.33: rate) that balances the trial-and-error exploration and exploitation of beliefs.`
- `L0227 p7.35: 2.2 Navigating two, interdependent T-mazes`
- `L0228 p7.36: Next, imagine that our mouse instead has to navigate two T-mazes, as depicted in Figure 2 below,`
- `L0229 p7.37: and where the cheese is only placed in the second one. The mouse now has to assign credit to`

### 007. Navigating two, interdependent T-mazes

- level: 2; pages: 7-8; lines: 227-247; words: 279

start sample:
- `L0227 p7.35: 2.2 Navigating two, interdependent T-mazes`
- `L0228 p7.36: Next, imagine that our mouse instead has to navigate two T-mazes, as depicted in Figure 2 below,`
- `L0229 p7.37: and where the cheese is only placed in the second one. The mouse now has to assign credit to`

end sample:
- `L0244 p8.30: feedback about interdependent actions, they could not tell if the beliefs they reinforced about`
- `L0245 p8.31: these actions were true or just “superstitious”. This phenomenon — reinforcing beliefs without`
- `L0246 p8.32: enough feedback to assign credit — is called superstitious learning (Levitt & March 1988).`

start boundary context:
- `L0225 p7.32: our first AI idea. In reinforcement learning, the solution is simply to design a policy (learning`
- `L0226 p7.33: rate) that balances the trial-and-error exploration and exploitation of beliefs.`
- `L0227 p7.35: 2.2 Navigating two, interdependent T-mazes`
- `L0228 p7.36: Next, imagine that our mouse instead has to navigate two T-mazes, as depicted in Figure 2 below,`
- `L0229 p7.37: and where the cheese is only placed in the second one. The mouse now has to assign credit to`

end boundary context:
- `L0245 p8.31: these actions were true or just “superstitious”. This phenomenon — reinforcing beliefs without`
- `L0246 p8.32: enough feedback to assign credit — is called superstitious learning (Levitt & March 1988).`
- `L0247 p8.34: 2.3 Navigating arbitrarily complex mazes: Sutton’s “reward hypothesis”`
- `L0248 p8.35: In the late 1970s at the University of Massachusetts, Amherst, Richard Sutton and his colleague`
- `L0249 p8.36: Andrew Barto developed a reinforcement learning approach to address combinatorial explosion`

### 008. Navigating arbitrarily complex mazes: Sutton’s “reward hypothesis”

- level: 2; pages: 8-9; lines: 247-283; words: 485

start sample:
- `L0247 p8.34: 2.3 Navigating arbitrarily complex mazes: Sutton’s “reward hypothesis”`
- `L0248 p8.35: In the late 1970s at the University of Massachusetts, Amherst, Richard Sutton and his colleague`
- `L0249 p8.36: Andrew Barto developed a reinforcement learning approach to address combinatorial explosion`

end sample:
- `L0280 p9.27: the maze, without having to evaluate paths of interdependent actions. These reward estimates can`
- `L0281 p9.28: then be used as a basis for evaluating and reinforcing individual actions (i.e., for solving the`
- `L0282 p9.29: credit assignment problem).`

start boundary context:
- `L0245 p8.31: these actions were true or just “superstitious”. This phenomenon — reinforcing beliefs without`
- `L0246 p8.32: enough feedback to assign credit — is called superstitious learning (Levitt & March 1988).`
- `L0247 p8.34: 2.3 Navigating arbitrarily complex mazes: Sutton’s “reward hypothesis”`
- `L0248 p8.35: In the late 1970s at the University of Massachusetts, Amherst, Richard Sutton and his colleague`
- `L0249 p8.36: Andrew Barto developed a reinforcement learning approach to address combinatorial explosion`

end boundary context:
- `L0281 p9.28: then be used as a basis for evaluating and reinforcing individual actions (i.e., for solving the`
- `L0282 p9.29: credit assignment problem).`
- `L0283 p10.0: 3. Minsky and the limits of the reinforcement paradigm`
- `L0284 p10.1: Sutton’s reward hypothesis proposes reinforcement learning as a general solution to credit`
- `L0285 p10.2: assignment for any problem requiring intelligence. Is this really plausible? A counterargument in`

### 009. Minsky and the limits of the reinforcement paradigm

- level: 1; pages: 10-10; lines: 283-309; words: 361

start sample:
- `L0283 p10.0: 3. Minsky and the limits of the reinforcement paradigm`
- `L0284 p10.1: Sutton’s reward hypothesis proposes reinforcement learning as a general solution to credit`
- `L0285 p10.2: assignment for any problem requiring intelligence. Is this really plausible? A counterargument in`

end sample:
- `L0306 p10.25: organization) of multiple agents that generate intermediate feedback based on coordinating and`
- `L0307 p10.26: cooperating actions. We next explore this idea of learning in a society as an alternative`
- `L0308 p10.27: paradigm for thinking about the general problem of credit assignment.`

start boundary context:
- `L0281 p9.28: then be used as a basis for evaluating and reinforcing individual actions (i.e., for solving the`
- `L0282 p9.29: credit assignment problem).`
- `L0283 p10.0: 3. Minsky and the limits of the reinforcement paradigm`
- `L0284 p10.1: Sutton’s reward hypothesis proposes reinforcement learning as a general solution to credit`
- `L0285 p10.2: assignment for any problem requiring intelligence. Is this really plausible? A counterargument in`

end boundary context:
- `L0307 p10.26: cooperating actions. We next explore this idea of learning in a society as an alternative`
- `L0308 p10.27: paradigm for thinking about the general problem of credit assignment.`
- `L0309 p10.30: 4. Paradigm 2: assigning credit by learning in a “society”`
- `L0310 p10.31: 4.1 Revisiting the T-maze`
- `L0311 p10.32: To introduce this alternative paradigm of assigning credit by learning in a society, let us revisit`

### 010. Revisiting the T-maze

- level: 2; pages: 10-12; lines: 310-366; words: 824

start sample:
- `L0310 p10.31: 4.1 Revisiting the T-maze`
- `L0311 p10.32: To introduce this alternative paradigm of assigning credit by learning in a society, let us revisit`
- `L0312 p10.33: our earlier T-maze problem from a different point of view. Imagine the problem is not for a`

end sample:
- `L0363 p12.10: “maximize” individual rewards (though this is one possibility); mostly, they fit into the society`
- `L0364 p12.11: by learning to coordinate and cooperate with many other agents using a variety of evaluative`
- `L0365 p12.12: criteria for assigning credit, always evaluated with respect to actions of many other agents.`

start boundary context:
- `L0308 p10.27: paradigm for thinking about the general problem of credit assignment.`
- `L0309 p10.30: 4. Paradigm 2: assigning credit by learning in a “society”`
- `L0310 p10.31: 4.1 Revisiting the T-maze`
- `L0311 p10.32: To introduce this alternative paradigm of assigning credit by learning in a society, let us revisit`
- `L0312 p10.33: our earlier T-maze problem from a different point of view. Imagine the problem is not for a`

end boundary context:
- `L0364 p12.11: by learning to coordinate and cooperate with many other agents using a variety of evaluative`
- `L0365 p12.12: criteria for assigning credit, always evaluated with respect to actions of many other agents.`
- `L0366 p12.14: 4.2 Constructing two different mazes`
- `L0367 p12.15: You should start to see how, even for a seemingly simple problem of constructing a T-maze from`
- `L0368 p12.16: a few blocks, the credit assignment challenge is radically different from that in the reinforcement`

### 011. Constructing two different mazes

- level: 2; pages: 12-12; lines: 366-388; words: 333

start sample:
- `L0366 p12.14: 4.2 Constructing two different mazes`
- `L0367 p12.15: You should start to see how, even for a seemingly simple problem of constructing a T-maze from`
- `L0368 p12.16: a few blocks, the credit assignment challenge is radically different from that in the reinforcement`

end sample:
- `L0385 p12.34: also have to figure out what to remember when constructing a new hedge maze. Hence, Geoffrey`
- `L0386 p12.35: is really not just a CEO managing how to delegate actions for constructing a maze to lower-level`
- `L0387 p12.36: agents, but also how to manage their memories that enable efficiently constructing new mazes.`

start boundary context:
- `L0364 p12.11: by learning to coordinate and cooperate with many other agents using a variety of evaluative`
- `L0365 p12.12: criteria for assigning credit, always evaluated with respect to actions of many other agents.`
- `L0366 p12.14: 4.2 Constructing two different mazes`
- `L0367 p12.15: You should start to see how, even for a seemingly simple problem of constructing a T-maze from`
- `L0368 p12.16: a few blocks, the credit assignment challenge is radically different from that in the reinforcement`

end boundary context:
- `L0386 p12.35: is really not just a CEO managing how to delegate actions for constructing a maze to lower-level`
- `L0387 p12.36: agents, but also how to manage their memories that enable efficiently constructing new mazes.`
- `L0388 p13.0: 4.3 The management hypothesis`
- `L0389 p13.1: Geoffrey’s credit assignment challenge is vastly more complex (or, at the least, qualitatively`
- `L0390 p13.2: different) from the challenge in the reinforcement learning paradigm of modifying beliefs or`

### 012. The management hypothesis

- level: 2; pages: 13-13; lines: 388-417; words: 416

start sample:
- `L0388 p13.0: 4.3 The management hypothesis`
- `L0389 p13.1: Geoffrey’s credit assignment challenge is vastly more complex (or, at the least, qualitatively`
- `L0390 p13.2: different) from the challenge in the reinforcement learning paradigm of modifying beliefs or`

end sample:
- `L0414 p13.29: system. Further, when they collectively assign credit to their configuration of agents, the novel`
- `L0415 p13.30: configuration may form a new goal. Even if there is just a rearrangement of goals, the “reward”`
- `L0416 p13.31: is not maximization, so much as learning a new skill or satisfying the needs of the society.`

start boundary context:
- `L0386 p12.35: is really not just a CEO managing how to delegate actions for constructing a maze to lower-level`
- `L0387 p12.36: agents, but also how to manage their memories that enable efficiently constructing new mazes.`
- `L0388 p13.0: 4.3 The management hypothesis`
- `L0389 p13.1: Geoffrey’s credit assignment challenge is vastly more complex (or, at the least, qualitatively`
- `L0390 p13.2: different) from the challenge in the reinforcement learning paradigm of modifying beliefs or`

end boundary context:
- `L0415 p13.30: configuration may form a new goal. Even if there is just a rearrangement of goals, the “reward”`
- `L0416 p13.31: is not maximization, so much as learning a new skill or satisfying the needs of the society.`
- `L0417 p13.33: 5. Conclusion`
- `L0418 p13.34: What should you take away from our discussion so far? First, you should see that any AI ideas`
- `L0419 p13.35: (or analogous organizational theories) can be understood in terms of how they propose solving`

### 013. Conclusion

- level: 1; pages: 13-13; lines: 417-425; words: 98
- review_flags: short_chunk

start sample:
- `L0417 p13.33: 5. Conclusion`
- `L0418 p13.34: What should you take away from our discussion so far? First, you should see that any AI ideas`
- `L0419 p13.35: (or analogous organizational theories) can be understood in terms of how they propose solving`

end sample:
- `L0422 p13.38: ideas can offer paradigmatically different views of learning and intelligence. Hence,`
- `L0423 p13.39: understanding AI will require you to form your own perspective based on thinking critically`
- `L0424 p13.40: about diverse ideas about intelligence that are often in tension.`

start boundary context:
- `L0415 p13.30: configuration may form a new goal. Even if there is just a rearrangement of goals, the “reward”`
- `L0416 p13.31: is not maximization, so much as learning a new skill or satisfying the needs of the society.`
- `L0417 p13.33: 5. Conclusion`
- `L0418 p13.34: What should you take away from our discussion so far? First, you should see that any AI ideas`
- `L0419 p13.35: (or analogous organizational theories) can be understood in terms of how they propose solving`

end boundary context:
- `L0423 p13.39: understanding AI will require you to form your own perspective based on thinking critically`
- `L0424 p13.40: about diverse ideas about intelligence that are often in tension.`
- `L0425 p14.0: 6. Appendix`
- `L0426 p14.1: 6.1 Historical link between the AI ideas and organizations`
- `L0427 p14.2: Reinforcement learning has roots in 1940s-1950s research in the US, famously by Richard`

### 014. Historical link between the AI ideas and organizations

- level: 2; pages: 14-14; lines: 426-450; words: 323

start sample:
- `L0426 p14.1: 6.1 Historical link between the AI ideas and organizations`
- `L0427 p14.2: Reinforcement learning has roots in 1940s-1950s research in the US, famously by Richard`
- `L0428 p14.3: Bellman, an applied mathematician at a US government think tank called the RAND`

end sample:
- `L0447 p14.23: machine learning strategies have dominated popular discourse about AI in recent decades,`
- `L0448 p14.24: current uses of AI increasingly involve managing systems of AI “agents”. Hence, as AI becomes`
- `L0449 p14.25: increasingly embedded in organizations, the AI field may be circling back to Minsky’s paradigm.`

start boundary context:
- `L0424 p13.40: about diverse ideas about intelligence that are often in tension.`
- `L0425 p14.0: 6. Appendix`
- `L0426 p14.1: 6.1 Historical link between the AI ideas and organizations`
- `L0427 p14.2: Reinforcement learning has roots in 1940s-1950s research in the US, famously by Richard`
- `L0428 p14.3: Bellman, an applied mathematician at a US government think tank called the RAND`

end boundary context:
- `L0448 p14.24: current uses of AI increasingly involve managing systems of AI “agents”. Hence, as AI becomes`
- `L0449 p14.25: increasingly embedded in organizations, the AI field may be circling back to Minsky’s paradigm.`
- `L0450 p14.27: 6.2 Philosophical background`
- `L0451 p14.30: 6.3 Further reading`
- `L0452 p14.31: Minsky, M. 1988. Society of Mind. New York, NY: Simon and Schuster.`

### 015. Further reading

- level: 2; pages: 14-15; lines: 451-462; words: 110
- review_flags: short_chunk

start sample:
- `L0451 p14.30: 6.3 Further reading`
- `L0452 p14.31: Minsky, M. 1988. Society of Mind. New York, NY: Simon and Schuster.`
- `L0453 p14.32: Minsky, M., & Selfridge, O. 1961. Learning in random nets. In C. Cherry (Ed.), Information`

end sample:
- `L0459 p14.38: Singh, P. 2003. Examining the society of mind. Computing and Informatics, 22(6): 521–543.`
- `L0460 p15.0: Sutton, R. S., & Barto, A. G. 2018. Reinforcement Learning: An Introduction. Cambridge MA:`
- `L0461 p15.1: MIT Press.`

start boundary context:
- `L0449 p14.25: increasingly embedded in organizations, the AI field may be circling back to Minsky’s paradigm.`
- `L0450 p14.27: 6.2 Philosophical background`
- `L0451 p14.30: 6.3 Further reading`
- `L0452 p14.31: Minsky, M. 1988. Society of Mind. New York, NY: Simon and Schuster.`
- `L0453 p14.32: Minsky, M., & Selfridge, O. 1961. Learning in random nets. In C. Cherry (Ed.), Information`

end boundary context:
- `L0460 p15.0: Sutton, R. S., & Barto, A. G. 2018. Reinforcement Learning: An Introduction. Cambridge MA:`
- `L0461 p15.1: MIT Press.`
