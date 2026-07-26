# Common Methodological and Statistical Errors — Reviewer Checklist Catalog

This file lists the **commonly encountered** issues in peer review by category. The `journalpeerreview`
skill reads it in Stage 3; it matches each item against the draft and marks the **actually** observed issue as
major/minor. Each item has three parts: **Common issue · How to detect · What to suggest**.
Example number format is given per the English rule (period); in a Turkish report convert to a comma.

> Rule: **do not fabricate** an issue listed here **if it is not actually in the draft**. If unsure, write it
> as a "question to the author". The reviewer does not do the fix; it hands off to the responsible team member (see SKILL.md single-ownership rule).

---

## Statistical issues

### 1. Misuse and misinterpretation of the p-value
- **Issue:** p-hacking (reporting only significant ones), uncorrected multiple testing, treating non-significance as
  "no effect" evidence, only p without effect size, dichotomizing continuous p at a threshold (p=0.049 ≠ p=0.051),
  confusing statistical significance with clinical significance.
- **How to detect:** p-values piling up just below 0.05; many tests but no correction; a "no difference found"
  statement from a non-significant result; no effect size/CI.
- **What to suggest:** report effect size + 95% CI; appropriate multiple-test correction (Bonferroni, FDR,
  Holm); interpret non-significance cautiously (absence of evidence ≠ evidence of absence); equivalence test for "no difference".

### 2. Wrong statistical test choice
- **Issue:** a parametric test under assumption violation (non-normal, unequal variance); an independent test on paired
  data; repeated t-tests instead of ANOVA in multiple groups; treating ordinal data as continuous;
  ignoring repeated-measures structure.
- **How to detect:** no assumption check mentioned; parametric with a small sample; multiple pairwise t instead of
  ANOVA; Likert with a t-test; without accounting for repeated measures.
- **What to suggest:** check assumptions explicitly (normality test, Q-Q); non-parametric if appropriate;
  appropriate post-hoc correction after ANOVA; mixed-effects model for repeated measures; ordinal regression for ordinal.

### 3. Sample size and power
- **Issue:** no power analysis/justification; a "no effect" claim with insufficient power; post-hoc power (uninformative);
  no pre-defined stopping rule; unjustified unequal groups.
- **How to detect:** small n (in a typical design, n<30 per group); no power analysis in the methods; a post-hoc
  power statement; wide CI; "no effect" with a large p + small n.
- **What to suggest:** a priori power analysis based on the expected effect; report the achieved power/precision (CI width);
  admit if underpowered; effect size + CI in the interpretation; pre-register the sample and stopping rule.

### 4. Missing data
- **Issue:** unjustified complete-case analysis (listwise deletion); the amount/pattern of missingness not reported;
  MCAR assumed without testing; inappropriate imputation; no sensitivity analysis.
- **How to detect:** different n across analyses without explanation; missing data not discussed; a participant
  "excluded from analysis"; simple mean imputation; no sensitivity analysis.
- **What to suggest:** report the amount/pattern of missingness; test MCAR (Little); an appropriate method
  (multiple imputation, maximum likelihood); sensitivity analysis; intention-to-treat (ITT) analysis in trials.

### 5. Circular analysis and double-dipping
- **Issue:** the same data for selection and inference; defining an ROI by a contrast then testing that contrast in the same
  ROI; selecting an outlier then a difference test; presenting a post-hoc subgroup as if planned; HARKing.
- **How to detect:** an ROI/feature selected by the result; an unexpected subgroup analysis; post-hoc not
  labeled as exploratory; no data-independent validation.
- **What to suggest:** an independent data set for selection and test; pre-register the analysis/hypothesis; clearly separate
  confirmatory and exploratory analysis; cross-validation/hold-out; correct for selection bias.

### 6. Pseudoreplication
- **Issue:** counting technical replicates as biological replicates; treating many measurements from the same subject as independent;
  analyzing clustered data without accounting for clustering; spatial/temporal dependence.
- **How to detect:** n = number of measurements (not biological units); many cells from the same animal counted as
  independent; repeated measures not mentioned; no random effect/clustering.
- **What to suggest:** define n as biological replicates (animal/patient/independent sample); mixed-effects model for
  nested/clustered data; account explicitly for repeated measures; average technical replicates first.

---

## Experimental design issues

### 7. Lack of appropriate controls
- **Issue:** no negative/positive control; no vehicle control in a drug study; no time-matched control in a longitudinal
  study; no batch control.
- **How to detect:** only experimental groups in the methods; no control in the figures; unclear baseline/reference condition.
- **What to suggest:** a negative control for specificity, a positive control for method validation; a matched vehicle;
  a sham in a surgical procedure; a batch control in batch comparisons.

### 8. Confounding variables
- **Issue:** groups systematically different beyond the intervention; an uncontrolled batch effect; order effect;
  time-of-day effect; an unblinded experimenter effect.
- **How to detect:** groups differ in more than one property; samples in different batches by group;
  processing order not randomized; no blinding; baseline properties differ between groups.
- **What to suggest:** randomize units to conditions; block by known confounders; randomize sample-processing
  order; blind; batch correction if needed; report and adjust for baseline differences.

### 9. Insufficient replication
- **Issue:** a single experiment without replication; mistaking a technical replicate for biological; a small n justified by "typical in the field";
  no independent validation; selecting a representative sample.
- **How to detect:** "the experiment was done once"; n=3 without justification; "representative visual"; a key claim based on a single
  experiment; no validation in an independent data set.
- **What to suggest:** independent biological replicates (typically ≥3); validate the key finding in an independent cohort;
  report all replicates, not only the representative; justify the sample with a power analysis; show individual data points.

---

## Reproducibility issues

### 10. Insufficient method detail
- **Issue:** methods insufficient for replication; a key reagent not specified (vendor/catalog no); no software
  version/parameter; an unvalidated antibody; an unauthenticated cell line identity.
- **How to detect:** vague ("standard protocols were used"); no reagent source; a generic
  software without version; no antibody validation info.
- **What to suggest:** give/cite a detailed protocol; reagent vendor-catalog-lot; software version+parameter;
  antibody validation; cell-line identity method (STR); make protocols accessible (protocols.io).

### 11. Data and code availability
- **Issue:** no data-availability statement; "upon request" (most are not fulfilled); no analysis code;
  proprietary software not shared; no documentation.
- **How to detect:** missing availability statement; no repository accession no; computational method without code;
  proprietary pipeline inaccessible; no README.
- **What to suggest:** deposit raw data in an appropriate repository (GEO, SRA, Dryad, Zenodo); share code on
  GitHub; README/documentation; environment file (requirements.txt); a DOI for a persistent citation.

### 12. Lack of method validation
- **Issue:** a new method not validated against a gold standard; specificity/sensitivity/linearity not
  tested; no spike-in; cross-reactivity not tested; limit of detection not established.
- **How to detect:** a new assay without validation; no comparison with an existing method; positive/negative
  control not shown; an unsupported specificity claim; no standard curve.
- **What to suggest:** validate against established approaches; show specificity (knockdown/knockout);
  linearity & dynamic range; positive/negative control; limit of detection/quantification; inter-operator reproducibility.

---

## Interpretation issues

### 13. Overstating the results
- **Issue:** causal language on correlational data; a mechanism claim without mechanism evidence; extrapolation
  beyond the data (species/condition/population); a "first to show" claim without a good literature search;
  over-generalization from a limited sample.
- **How to detect:** "X causes Y" from observational data; an untested mechanism; mouse data
  applied to humans without caveats; a novelty claim with missing citations.
- **What to suggest:** appropriate language ("associated with" vs "caused"); correlation-causation distinction; admit the
  model-system limitation; comprehensive literature context; be specific about generalizability; present the mechanism as a hypothesis.

### 14. Cherry-picking and selective reporting
- **Issue:** reporting only significant ones; a "representative" visual that may not be typical; unjustified outlier
  exclusion; not reporting negative/conflicting findings; switching between different statistical approaches.
- **How to detect:** all reported results are significant; "representative of 3 experiments" but no quantification; data
  exclusion is in the results but not the methods; supplementary data conflicts with the main finding.
- **What to suggest:** report all planned analyses regardless of result; show variability across replicates;
  pre-define the outlier criterion; include negative results; pre-register the analysis plan.

### 15. Ignoring alternative explanations
- **Issue:** a preferred explanation without considering alternatives; dismissing conflicting evidence without discussion;
  off-target effect not considered; a confounder not acknowledged; a weak/absent limitations section.
- **How to detect:** a single interpretation presented as fact; a prior conflicting finding not mentioned; no alternative
  mechanism; no limitation discussion; an uncontrolled specificity assumption.
- **What to suggest:** discuss alternative explanations; address conflicting findings in the literature; specificity
  controls; discuss limitations thoroughly; test alternative hypotheses.

---

## Figure and data presentation issues

### 16. Inappropriate data visualization
- **Issue:** a bar chart for continuous data (hides the distribution); an undefined/missing error bar; a truncated
  y-axis exaggerates the difference; a dual y-axis misleads; excessive significant digits; a color-blind-unfriendly color.
- **How to detect:** a bar with little data; unclear what the error bar is (SD/SEM/CI?); for proportion/percentage data
  the y does not start at zero; two y-axes with different scales; overly precise value (p=0.04562); a red-green scheme.
- **What to suggest:** individual points (scatter/box/violin); define the error bar (SD/SEM/95% CI);
  start y at zero or mark the break; separate panels instead of a dual y; appropriate digits; a color-blind-safe
  palette (viridis, colorbrewer); the sample size in the legend.

### 17. Suspicion of image manipulation
- **Issue:** excessive contrast/brightness; a spliced gel/visual without disclosure; a duplicated
  panel; an uneven background in a blot; selective cropping; over-processed microscopy.
- **How to detect:** a suspicious pattern/discontinuity; very high contrast without a background; a similar element in a
  different panel; a straight line suggesting a splice; an inconsistent background.
- **What to suggest:** apply settings uniformly to the whole visual; mark a splice with a separator line; a full/uncropped
  visual in a supplement; the original if requested; comply with the journal's image-integrity policy.

---

## Study design issues

### 18. Poorly defined hypothesis and outcome
- **Issue:** no clear hypothesis; primary outcome not specified; multiple outcomes without correction; an outcome
  changed after the data; presenting "fishing" as if hypothesis-driven.
- **How to detect:** the introduction does not give a clear testable hypothesis; multiple outcomes with an unclear hierarchy;
  the outcome in the results does not match the methods; an exploratory study presented as confirmatory.
- **What to suggest:** a clear, testable hypothesis; a priori primary/secondary outcome; if possible,
  pre-registration; correction for multiple outcomes; exploratory/confirmatory distinction; report all pre-defined outcomes.

### 19. Baseline imbalance and selection bias
- **Issue:** groups differ at baseline; selection criterion applied differently; healthy-volunteer bias;
  survivorship bias; indication bias in an observational study.
- **How to detect:** a significant baseline difference in Table 1; different inclusion criteria between groups; a response rate
  <50% without analysis; only completers; self-selected groups instead of randomized.
- **What to suggest:** report baseline properties in Table 1; achieve balance by randomization; adjust for the baseline
  difference in the analysis; report the response rate; propensity-score matching in observational data; ITT analysis.

### 20. Temporal and batch effects
- **Issue:** samples batched by condition; a temporal trend not accounted for; instrument drift;
  a different operator for groups; a reagent-lot change between groups.
- **How to detect:** all treatment samples on the same day; controls from a different period; batch/time effect
  not mentioned; a different technician for groups; a long duration with no temporal analysis.
- **What to suggest:** randomize samples to batch/time; include batch as a covariate; batch correction
  (ComBat, limma); a quality-control sample across batches; test the temporal trend; balance operators.

---

## Reporting issues

### 21. Incomplete statistical reporting
- **Issue:** no test statistic; missing degrees of freedom; an inequality (p<0.05) instead of an exact p;
  no CI; no effect size; n per group not reported.
- **How to detect:** only p, no test statistic; p<0.05 (not an exact value); no measure of uncertainty;
  unclear effect size; n given for the total but not per group.
- **What to suggest:** the full test statistic (t, F, χ², etc. + df); an exact p (except p<0.001); 95% CI; effect
  size (Cohen's d, OR, correlation coefficient); n per group in every analysis; a CONSORT-style flow diagram.

### 22. Methods–Results mismatch
- **Issue:** an analysis in the methods that was not done; an analysis in the results that is not in the methods; a different sample
  in the methods and results; a control mentioned in the methods but not shown; statistics that do not match what was done.
- **How to detect:** an analysis in the results with no method description; an experiment in the methods not in the results;
  inconsistent numbers between sections; a mentioned but not-shown control; a software different from what was used.
- **What to suggest:** ensure full methods–results consistency; describe all performed analyses in the methods;
  remove what was not done; verify all numbers are consistent; update the methods to match the actual analyses.

---

## How to use this reference

When evaluating a manuscript: (1) read the methods and results systematically, (2) scan these items in each
category, (3) note the specific issue **with its evidence**, (4) suggest a constructive improvement, (5) separate major (affects
validity) from minor (affects clarity), (6) prioritize reproducibility and transparency.

This list is not exhaustive; it covers the most common ones. Always consider the discipline and context.
**Do not flag an issue if you do not actually see it in the draft.**
