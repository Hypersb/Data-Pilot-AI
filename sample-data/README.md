# Sample Datasets

One-click demo datasets for Prisma AI. Load from the upload page or via API.

| File | Rows (approx.) | Best for |
|------|----------------|----------|
| `sales.csv` | Time series sales | Forecasting, trends, Ask Prisma |
| `churn.csv` | Customer churn | Classification, Model Arena |
| `housing.csv` | Property prices | Regression, correlations |
| `marketing.csv` | Campaign spend | Regression, segment compare |
| `netflix.csv` | Content catalog | Exploration, insights |
| `pokemon.csv` | Game stats | Classification, fun demos |
| `titanic.csv` | Passenger survival | Classification, SHAP |

## Quick start

```bash
# Load sales sample via API
curl -X POST http://127.0.0.1:8080/api/samples/sales/load
```

Or open the app → **Try sample dataset** on the upload page.
