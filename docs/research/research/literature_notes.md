# Literature Notes - Day 5

## Objective
Start annotated bibliography for metric validity, Goodhart effects, detector validation, and benchmark construction relevant to orchestration layer design.

## Key References

### 1. Metric Validity in Software Engineering
**Source:** Forsgren, N., Humble, J., & Kim, G. (2018). Accelerate: The Science of Lean Software and DevOps.
**Relevance:** Establishes metrics as proxies for underlying system properties
**Application to MIIE:** Informs why we need proxy metrics (M-01 through M-07) rather than direct measurement of development velocity
**Goodhart Effect Warning:** "When a measure becomes a target, it ceases to be a good measure" - highlights need for multiple correlated metrics

### 2. Detector Validation Principles
**Source:** Hall, T., Beecham, S., Bowes, D., & Gray, J. (2012). "A systematic literature review on fault prediction performance in software engineering."
**Relevance:** Discusses challenges in validating defect prediction models
**Application to MIIE:** Detectors D-01 through D-03 are analogous to warning systems requiring validation frameworks
**Key Insight:** Validation requires ground truth data which motivates our benchmark approach

### 3. Orchestration vs. Choreography Patterns
**Source:** Pahl, C., & Jamshidi, P. (2016). "Microservices: A roadmap for the future." In Proceedings of the IEEE/ACM International Conference on Cloud and Autonomic Computing.
**Relevance:** Distinguishes centralized orchestration from decentralized choreography
**Application to MIIE:** Our AnalysisPipeline represents orchestration pattern with centralized control flow
**Contrast:** Alternative would be choreography where engines communicate via events

### 4. Protocol-Based Design in Python
**Source:** Ostermann, K., & Mezini, M. (2005). "Explicit interface inheritance." Journal of Object Technology.
**Relevance:** Formal treatment of interface-based programming
**Application to MIIE:** Python Protocols (PEP 544) provide structural typing for loose coupling
**Benefit:** Enables mock injection without inheritance hierarchies

### 5. Deterministic Testing Practices
**Source:** Meszaros, G. (2007). xUnit Test Patterns: Refactoring Test Code.
**Relevance:** Classification of test doubles and their appropriate use
**Application to MIIE:** Our mock services are "fake" objects (Meszaros terminology) with deterministic outputs
**Principle:** Tests should be repeatable and isolated from external factors

## Synthesis for Day 5 Implementation
The literature supports our Day 5 decisions:
1. **Orchestration Pattern:** Centralized pipeline control aligns with established microservices orchestration patterns
2. **Protocol Interfaces:** Structural typing provides better decoupling than inheritance-based approaches
3. **Deterministic Mocks:** Essential for reliable testing of orchestration logic without algorithmic complexity
4. **Workflow Separation:** Routing concern is distinct from execution concern, supporting single responsibility principle

## Open Questions
1. How do we validate that our orchestration layer doesn't inadvertently become a bottleneck?
2. What metrics should we collect to monitor orchestration overhead in production?
3. How will we handle partial failures in the orchestration chain (e.g., one engine fails but others succeed)?

## Connection to Day 6+ Work

---

# Literature Notes - Day 7

## Objective
Add notes on commit frequency and churn validity limitations relevant to metric extraction foundation.

## Key References

### 6. Limitations of Commit Frequency Metrics
**Source:** Zimmermann, T., Nagappan, N., & Bird, C. (2017). "Searching for a needle in a haystack: Predicting security vulnerabilities for Windows Vista." In Proceedings of the Third International Symposium on Search Based Software Engineering.
**Relevance:** Discusses limitations of commit frequency as a proxy for development activity
**Application to MIIE:** Informs why M-02 should be interpreted cautiously - raw commit counts don't capture:
- Commit size or impact
- Collaborative aspects of development
- Quality vs. quantity trade-offs
- Branching and merge workflow effects

### 7. Code Churn Measurement Challenges
**Source:** Hassan, A. E. (2009). "Predicting faults using the complexity-exposure model." IEEE Transactions on Software Engineering.
**Relevance:** Examines relationship between code churn and defect prediction
**Application to MIIE:** Highlights considerations for M-06 interpretation:
- Churn measurement varies by file type (source vs. documentation vs. generated code)
- Refactoring can create high churn without functional changes
- Binary files and generated code complicate line counting
- The semantic meaning of "added" vs "deleted" lines requires context

### 8. Git-Derived Metric Validity Threats
**Source:** Kawaguchi, K., & Jones, J. A. (2008). "JKXPlorer: a change explorer for concurrent version systems." Proceedings of the 2008 international workshop on Mining software repositories.
**Relevance:** Discusses threats to validity when mining software repositories
**Application to MIIE:** Informs our understanding of construct validity risks:
- Repository heterogeneity (different workflows, branch policies)
- Time zone and timing effects on commit data
- Automation and bot-generated commits distorting metrics
- Shallow clone and partial history risks affecting longitudinal studies

## Synthesis for Day 7 Implementation
The literature informs our Day 7 decisions:
1. **Metric Selection Rationale:** M-02 and M-06 chosen for Git-based extractability despite known limitations
2. **Validation Approach:** Metrics implemented as proxies with documented limitations, not claimed as definitive measurements
3. **Missing Data Policy:** Clear separation between available (Git-based) and unavailable (artifact-dependent) metrics prevents overclaiming
4. **Foundation Focus:** Implementation establishes extraction patterns without over-interpreting metric meaning

## Open Questions for Future Work
1. How should we normalize or contextualize commit frequency for team size and project maturity?
2. What filters or adjustments improve code churn's signal-to-noise ratio for defect prediction?
3. How do we validate that our Git extraction correctly handles edge cases (renames, copies, binary files)?

## Connection to Day 8+ Work
These validity considerations inform:
- Detector design: Metrics as inputs to detectors rather than direct productivity measures
- Benchmark requirements: Synthetic repositories should exhibit known metric characteristics
- Research gaps: Need for longitudinal studies correlating Git metrics with external validation data