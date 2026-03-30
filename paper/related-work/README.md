# Related Work Library

This directory stores locally downloaded papers that are directly relevant to the current CoverAgent-ML / CoverUp follow-up project.

The goal is not to accumulate PDFs blindly, but to maintain a working reference set for:

- novelty positioning
- experiment design
- baseline selection
- claim scoping
- reviewer-risk checking

The original CoverUp paper already exists in this repository as [coverup.pdf](/home/zzzccc/coverup/paper/coverup.pdf).

## Downloaded PDFs

### Baselines and Closely Adjacent LLM Test Generation

- `pdfs/CodaMOSA_escaping_coverage_plateaus_ICSE2023.pdf`
  Source: https://www.carolemieux.com/20230517_Codamosa_ICSE23.pdf
  Why it matters: classical hybrid baseline; useful when discussing search + LLM seeding versus iterative agent control.

- `pdfs/ChatUniTest_framework_for_LLM_based_test_generation_2023.pdf`
  Source: https://arxiv.org/pdf/2305.04764.pdf
  Why it matters: representative LLM unit-test generation framework with repair loop; relevant for Java-centric comparisons and repair discussion.

- `pdfs/MuTAP_mutation_testing_for_LLM_test_generation_2023.pdf`
  Source: https://arxiv.org/pdf/2308.16557.pdf
  Why it matters: mutation-guided Python test generation; relevant when contrasting coverage guidance versus mutation guidance.

- `pdfs/TestGen_LLM_automated_unit_test_improvement_at_Meta_2024.pdf`
  Source: https://arxiv.org/pdf/2402.09171.pdf
  Why it matters: strong industrial reference point for improving existing human-written tests rather than generating from scratch.

### Program-Analysis-Guided / Hybrid Approaches

- `pdfs/SymPrompt_code_aware_prompting_coverage_guided_regression_2024.pdf`
  Source: https://arxiv.org/pdf/2402.00097.pdf
  Why it matters: explicit path-constraint and code-aware prompting; directly relevant to any "where vs why/how" positioning.

- `pdfs/ASTER_natural_and_multi_language_unit_test_generation_2024.pdf`
  Source: https://arxiv.org/pdf/2409.03093.pdf
  Why it matters: multi-language pipeline with static analysis and naturalness evaluation; especially relevant against your current cross-language narrative.

- `pdfs/RUG_turbo_LLM_for_Rust_unit_test_generation_2025.pdf`
  Source: https://gts3.org/assets/papers/2025/cheng%3Arug.pdf
  Why it matters: Rust-specific strong baseline; relevant for understanding compiler strictness and Rust-only specialization.

- `pdfs/PALM_hybrid_program_analysis_and_LLMs_for_Rust_2025.pdf`
  Source: https://arxiv.org/pdf/2506.09002.pdf
  Why it matters: probably the most important direct comparison point for your blocker story; it uses analysis-derived path constraints for Rust.

- `pdfs/Panta_iterative_hybrid_program_analysis_2025.pdf`
  Source: https://arxiv.org/pdf/2503.13580.pdf
  Why it matters: iterative static + dynamic path-guided loop; useful if we need to position against stronger analysis-feedback pipelines beyond CoverUp.

- `pdfs/Mutation_guided_LLM_test_generation_at_Meta_2025.pdf`
  Source: https://arxiv.org/pdf/2501.12862.pdf
  Why it matters: industry-style mutation-guided improvement pipeline; useful when discussing alternative feedback signals and practical deployment.

### Critique / Landscape / Risk Framing

- `pdfs/Design_choices_prevent_bug_finding_2024.pdf`
  Source: https://arxiv.org/pdf/2412.14137.pdf
  Why it matters: critical paper arguing that pass-oriented LLM test generators can validate bugs instead of finding them; essential for threat-to-validity and claim-scoping.

- `pdfs/Large_language_models_for_unit_testing_systematic_review_2025.pdf`
  Source: https://arxiv.org/pdf/2506.15227.pdf
  Why it matters: broad map of the literature up to March 2025; useful for checking whether a claim is actually novel or already commoditized.

## Not Downloaded Yet

- Logic-CoT (Applied Sciences 2026)
  Landing page: https://www.mdpi.com/2076-3417/16/5/2542
  Status: article page is accessible, but direct PDF download returned HTTP 403 from this environment.
  Why it still matters: logic-guided and explainable test generation is conceptually adjacent to your "why/how" narrative.

- Evaluating LLM-based Regression Test Generation
  Status: previously found link returned HTTP 404; not stored locally.
  Why it still matters: could be useful as an external critical evaluation if we find a stable mirror later.

## How We Should Use This Library

- For novelty:
  compare primarily against CoverUp, PALM, ASTER, RUG, and Panta.

- For evaluation design:
  use ASTER, PALM, TestGen-LLM, and the systematic review to avoid weak benchmark or metric choices.

- For reviewer-risk analysis:
  use Design Choices and mutation-guided work to stress-test claims about "good tests", "useful tests", and "coverage gain".

- For claim discipline:
  do not compare incomparable metrics without explicitly marking the difference between:
  incremental coverage over existing suites,
  coverage from generated tests only,
  pass rate / compile rate,
  bug-finding ability.
