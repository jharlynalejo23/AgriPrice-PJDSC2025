# AGRIPRICE: Tracking Agricultural Prices Amid Typhoons

## Executive Summary
AGRIPRICE is a data analysis and dashboard project that shifts the focus of disaster response from **reaction** to **proactive anticipation**. By integrating historical typhoon data (PAGASA) with commodity price data (PSA), we quantify market vulnerability.

The core findings enable evidence-based policy:
* **Most Volatile:** **Red Onion** is the most volatile commodity (6.34% spike frequency, $\text{P}70.82 \text{/KG}$ volatility).
* **High-Risk Regions:** **Central Luzon, MIMAROPA, and CALABARZON** show the highest concentration of price spikes.

---

## The Problem: Climate Change as an Economic Threat

Climate change is a direct threat to the cost of food. The Philippines experiences approximately 20 tropical cyclones annually, leading to massive agricultural losses (e.g., P6.83 Billion from Typhoons Kristine and Leon in 2024). This supply shock immediately translates to higher food prices for vulnerable households.

**The Market Gap:** Existing monitoring focuses on **damage assessment after the event**. We lack the tools for:
1.  Predicting **which** commodity will spike first.
2.  Identifying **which regions** are structurally most prone to price chaos.

Our goal is to provide the data for **proactive, evidence-based intervention strategies.**

---

## Data & Core Methodology

The analysis is built on three core risk metrics to quantify market vulnerability:

### Data Sources
* **Climate Data:** Historical tropical cyclones (timing and intensity) from **PAGASA** Annual and Preliminary Reports.
* **Price Data:** Monthly retail prices of selected commodities from **PSA OpenSTAT**.

### AGRIPRICE Risk Metrics
| Metric | Definition | Measures |
| :--- | :--- | :--- |
| **Price Spike Frequency** | How often the price exceeds Median + 1.5 x IQR. | Acute, **short-term supply shocks**. |
| **Price Volatility** | The standard deviation of retail prices over time. | Chronic, **long-term price instability**. |
| **Price Lag** | Time (mean months) between a Typhoon's entry into the PAR and the commodity's first price spike. | **Market speed** of disruption. |

---

## Key Findings for Policy Action

### 1. The Volatility Leaders
| Commodity | Spike Frequency | Price Volatility (Standard Deviation) |
| :--- | :--- | :--- |
| **Red Onion** | $\mathbf{6.34\%}$ | $\mathbf{P}70.82/\text{KG}$ |
| **White Onion** | $5.11\%$ | $\mathbf{P}70.32/\text{KG}$ |
| **Tomato** | $6.32\%$ | $\text{P}47.11/\text{KG}$ |

> **Key Insight:** Red and White Onions are overwhelmingly the most unstable commodities, exhibiting both high frequency of spikes and the largest magnitude of price swings.

### 2. Regional Vulnerability
The majority of price irregularities are concentrated in these three high-risk regions:
1.  **Region III - Central Luzon**
2.  **MIMAROPA Region**
3.  **IV-A - CALABARZON**

### 3. Price Reaction Time
* The median price spike occurs **1.0 month** after a typhoon event.
* **Garlic, Local** is the fastest reacting commodity (mean lag: **0.9 months**).

> **Conclusion:** Price spikes are rapid. Policy interventions must be designed for deployment *within one month* of a major weather event.

---

## Dashboard Features

The AGRIPRICE dashboard provides two key interactive features for analysis:

1.  **National Average Prices vs. Typhoon Events:** Visualizations that confirm the direct, lagged impact of typhoon clusters on commodity prices (e.g., Rootcrops).
2.  **The Resilience Matrix (Lag vs. Volatility Scatter):** A scatter plot that classifies commodities based on their market speed (lag) and price instability (volatility) for comprehensive risk analysis.

---

## References
* Inquirer.net. (2024, November 8). DA: Agriculture losses due to typhoons hit P6.83B.
* Philippine Atmospheric, Geophysical and Astronomical Services Administration (PAGASA). Annual reports and Preliminary reports.
* Philippine Statistics Authority (PSA) OpenSTAT.
