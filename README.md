🇪🇸 [Leer en español](README.es.md)

# Email Campaign A/B Testing: Frequentist, Bayesian and Segment Analysis

Analysis of a randomized email marketing experiment (Kevin Hillstrom's *MineThatData E-Mail Analytics Challenge*, 2008): experiment design validation, estimation of each campaign's effect with confidence intervals and multiple-comparison correction, a Bayesian approach, and an exploration of whether the effect changes by customer type.

**Author:** Carlos Adolfo Peralta · [LinkedIn](https://www.linkedin.com/in/carlosperalta1993/) · [GitHub](https://github.com/CarlosAdolfoPeralta)

## Summary

- **The experiment:** 64,000 customers who purchased in the last 12 months, randomly assigned to receive an email featuring **men's** products, an email featuring **women's** products, or no email (**control**). Over two weeks, it measured whether they visited the site, whether they purchased, and how much they spent.
- **The design is sound:** the three groups have the expected size (one third each, p = 0.90) and are comparable on everything measured before the experiment (maximum standardized difference of 0.009), so later differences can be attributed to the email.
- **Both emails work, and the men's email performs better:** versus control, the men's email raises conversion from 0.57% to 1.25% (+0.68 pp) and the women's email to 0.88% (+0.31 pp). The men's email beats the women's by 0.37 pp. All differences remain significant after multiple-comparison correction.
- **Incremental revenue (gross):** about USD 770 per 1,000 emails with the men's email and about USD 424 with the women's, versus control.
- **The Bayesian approach agrees:** the probability that the men's email beats the women's on conversion is above 99.9%, and the conclusions do not depend on the prior.
- **Exploratory finding:** the effect on visits changes a lot depending on the customer's purchase history. The women's email barely increases visits among those who only bought men's products (+1.1 pp), while among those who bought women's products it adds +7.4 pp.

## Data

| | |
|---|---|
| Source | MineThatData blog, by Kevin Hillstrom (2008) |
| Customers | 64,000, randomly assigned: control 21,306, men's email 21,307, women's email 21,387 |
| Pre-experiment variables | recency, spend history, purchases of men's and women's products, region, new customer, channel |
| Outcomes | `visit` (visited the site), `conversion` (purchased) and `spend` (amount spent), over the following two weeks |
| Peculiarities | 99.1% of customers have zero spend; among the 578 who purchased, the maximum spend is exactly USD 499 in all three groups |

## Methodology

1. **Experiment validation** (`01_validacion_experimento`): data quality, consistency across outcome variables, *sample ratio mismatch* and balance of pre-experiment characteristics (chi-square, ANOVA, Kruskal-Wallis and standardized differences). Includes the **analysis plan**, fixed before looking at the results: conversion as the primary metric; visits and spend as secondary; Holm correction within each metric.
2. **Frequentist analysis** (`02_analisis_frecuentista`):
   - Conversion and visits: absolute difference with a Newcombe interval, relative lift with a log-scale interval, and a two-proportion z-test.
   - Spend per customer: Welch's t-test plus a 10,000-resample bootstrap, because of the zeros and the long tail. Includes a sensitivity check on high amounts and a warning about why spend is not compared causally among purchasers.
   - Power: minimum detectable effect and required sample size.
3. **Bayesian approach and segments** (`03_bayesiano_segmentos`):
   - Beta posteriors for the rates, probability of superiority, expected loss, prior sensitivity and a Bayesian bootstrap for spend.
   - Exploratory analysis across six segmentation variables, with Cochran's Q heterogeneity test and Holm correction.

The statistical functions are in `src/ab.py` and were validated against scipy (for example, the z-test matches the 2x2 chi-square and Holm reproduces a known case).

## Results

### Effect of each email versus control and versus each other

| Metric | Control | Men's email | Women's email | Men's − control | Women's − control | Men's − women's |
|---|---|---|---|---|---|---|
| Conversion | 0.57% | 1.25% | 0.88% | +0.68 pp (0.50 to 0.86) | +0.31 pp (0.15 to 0.47) | +0.37 pp (0.17 to 0.57) |
| Visits | 10.6% | 18.3% | 15.1% | +7.7 pp (7.0 to 8.3) | +4.5 pp (3.9 to 5.2) | +3.1 pp (2.4 to 3.8) |
| Spend per customer | USD 0.65 | USD 1.42 | USD 1.08 | +USD 0.77 (0.48 to 1.06) | +USD 0.42 (0.17 to 0.69) | +USD 0.35 (0.03 to 0.66) |

95% confidence intervals in parentheses (bootstrap for spend). With Holm correction, all differences are significant at 5%; the least conclusive is the spend difference between emails (p = 0.03).

- **Relative lift in conversion:** +119% with the men's email (CI 77% to 171%) and +54% with the women's (CI 23% to 94%).
- **Source of the higher spend:** mean spend among purchasers is similar across the three groups (USD 114, 114 and 122), so the higher revenue per customer comes mainly from more people buying, not from larger purchases.
- **Robustness:** when capping spend at the 90th percentile of purchasers, the effects hold (+0.67, +0.39 and +0.28 USD). Applying Holm across all nine comparisons at once, all remain significant.
- **Power:** with 21,306 customers per group, the minimum detectable effect on conversion is 0.22 pp (a 39% relative lift); detecting a 10% lift would have required about 286,000 customers per group.

### Bayesian approach

- The probability of superiority is above 99.9% in all three conversion comparisons, and the probability that the difference between emails exceeds 0.22 pp is 93%.
- Choosing the men's email has an expected loss of practically 0 pp of conversion; choosing the women's, 0.37 pp.
- With three different priors (uniform, Jeffreys and informative), the difference between emails ranges from 0.353 to 0.369 pp: the data dominate.
- For spend, the Bayesian bootstrap gives results almost identical to the frequentist ones (differences under USD 0.01) and a 98.5% probability that the men's email beats the women's.

### Does the effect change by customer type? (exploratory)

- **Conversion:** none of the 18 heterogeneity tests is significant after Holm (the smallest adjusted p is 0.15). The men's email has a positive effect in all 22 segments analyzed. This test has low power with rare events, so it cannot be concluded that the effect is homogeneous.
- **Visits, by affinity:** there is strong variation (adjusted p ≤ 0.0001), and it is the clearest finding of this part:

| Customer affinity | Visits without email | Men's email effect | Women's email effect |
|---|---|---|---|
| Bought both types of products | 18.1% | +13.4 pp | +7.1 pp |
| Only men's products | 10.0% | +6.9 pp | +1.1 pp |
| Only women's products | 9.6% | +7.1 pp | +7.4 pp |

The women's email performs much worse outside its natural audience. This is a hypothesis for a new experiment (for example, not sending it to those who only bought men's products), not a definitive conclusion: visiting is an intermediate step, and for conversion the pattern points in the same direction but is not significant.

## Limitations

- Revenue is **gross**: neither the cost of the emails nor the margin on the products is deducted, as the dataset does not include them.
- Follow-up covers only two weeks, and the sample is customers who purchased in the last 12 months, so the results do not extend to new or inactive customers.
- The two emails differ in both content and audience at the same time, so the effect of each cannot be separated.
- The dataset has no customer identifier, so duplicates could not be checked. That the maximum spend is exactly USD 499 in all groups suggests a cap in the records (not verified), although the results do not depend on high amounts.
- Conversion is a rare event (0.9%): the intervals for relative lift are wide and the segment analysis has low power. The segments are exploratory and some have very few purchases.
- Deciding which customers should receive each email would require an uplift model, which is beyond the scope of this analysis.

## Repository structure

```
.
├── README.md
├── requirements.txt
├── .gitignore
├── notebooks/
│   ├── 01_validacion_experimento.ipynb
│   ├── 02_analisis_frecuentista.ipynb
│   └── 03_bayesiano_segmentos.ipynb
├── src/
│   ├── __init__.py
│   ├── data.py          # dataset loading and schema validation
│   └── ab.py            # statistical functions (proportions, Holm, bootstrap, power, heterogeneity)
├── reports/             # result tables (.csv)
└── data/                # downloaded data (not versioned)
```

## How to reproduce

1. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the notebooks in order from the `notebooks/` folder. The first time, `src/data.py` downloads the dataset from the MineThatData blog and saves it to `data/raw/hillstrom.csv`. If the download fails, you can save the CSV manually at that path.
3. Notebooks 02 and 03 save their result tables in `reports/`.

Seeds are fixed (42), so the bootstrap and the Bayesian simulations are reproducible.

## References

- Hillstrom, K. (2008). *The MineThatData E-Mail Analytics And Data Mining Challenge*. MineThatData blog. Source of the dataset; the data is not included in this repository.
- Newcombe, R. G. (1998). Interval estimation for the difference between independent proportions: comparison of eleven methods. *Statistics in Medicine*, 17(8), 873-890.
