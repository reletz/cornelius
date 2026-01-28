# Task: Identify Subtopics for Cornell Notes Generation

You are analyzing academic materials to identify coherent subtopics that will each become a standalone Cornell note.

## Input Materials

[PASTE ALL EXTRACTED TEXT HERE WITH METADATA]

Document 1: lecture1.pptx (45 slides)
---
Slide 1: Introduction to Graph Traversal...
Slide 2: Depth-First Search Overview...
[full text]
---

Document 2: lecture2.pptx (38 slides)
---
Slide 1: Advanced DFS Techniques...
[full text]
---

Document 3: lecture3.pptx (30 slides)
---
[full text]
---

## Requirements

1. **Identify 3-7 Subtopics**
   - Each subtopic should be substantial enough for a comprehensive note (minimum 1500 words of content)
   - Group related concepts together logically
   - Avoid overly granular splits (don't create separate topics for closely related concepts)
   - Ensure topics flow in a logical learning sequence

2. **For Each Subtopic, Specify:**
   - Clear, descriptive title (should indicate what student will learn)
   - Which documents and slide/page ranges contain content for this subtopic
   - Brief rationale (1 sentence) explaining why this grouping makes sense

3. **Source Mapping Precision**
   - Be specific about slide/page ranges
   - If content is non-contiguous, list multiple ranges
   - Example: "lecture1.pptx (slides 5-12, 28-35)" not just "lecture1.pptx"

4. **Handle Content Overlap**
   - If multiple documents cover the same concept, group them under one subtopic
   - Example: If all 3 lectures introduce DFS basics, put them all in "DFS Fundamentals" subtopic

## Output Format

Respond ONLY with valid JSON, no markdown code blocks, no preamble:

{
  "clusters": [
    {
      "id": "1",
      "title": "Descriptive subtopic title that indicates learning objective",
      "sources": [
        {
          "document": "lecture1.pptx",
          "slides": "1-15"
        },
        {
          "document": "lecture2.pptx",
          "slides": "3-8"
        }
      ],
      "rationale": "One sentence explaining why these sources belong together",
      "estimated_words": 2000
    },
    {
      "id": "2",
      "title": "Another subtopic",
      "sources": [
        {
          "document": "lecture2.pptx",
          "slides": "20-35"
        },
        {
          "document": "lecture3.pptx",
          "slides": "5-18"
        }
      ],
      "rationale": "Explanation for this grouping",
      "estimated_words": 1800
    }
  ],
  "total_clusters": 5,
  "clustering_approach": "Brief explanation of overall strategy used"
}

## Quality Guidelines

- GOOD: "DFS Implementation: Recursive vs Iterative Approaches"
- POOR: "DFS" (too vague)
- POOR: "Slide 5-10 Content" (not descriptive)

- GOOD: Grouping "DFS basics" from lecture 1, "DFS examples" from lecture 2, "DFS practice" from lecture 3 into one "DFS Fundamentals" topic
- POOR: Splitting "DFS Introduction" and "DFS Definition" into separate topics (too granular)

Begin analysis now.