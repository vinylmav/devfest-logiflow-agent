"""Analytics Agent — specialist agent for reports, KPIs, and trends."""

from logiflow.config import MODEL
from google.adk.agents import LlmAgent

from logiflow.tools.data import (
    generate_report,
    run_python_code,
    aggregate_metrics,
)

analytics_agent = LlmAgent(
    name="analytics_agent",
    model=MODEL,
    description=(
        "Generates logistics reports, analyses trends, tracks KPIs, and provides "
        "data-driven insights for operational decisions."
    ),
    instruction="""\
You are LogiFlow's Analytics & Business Intelligence Specialist.

CAPABILITIES:
- Generate structured reports using generate_report
  (types: daily_summary, weekly_performance, inventory_status, shipment_analytics, cost_analysis)
- Execute custom data analysis using run_python_code
- Aggregate and group metrics using aggregate_metrics

RESPONSE FORMAT:
## 📊 <Report Title>
**Period:** <date_range>
**Generated:** <timestamp>

### Key Metrics
<table of primary KPIs>

### Performance Highlights
<3-5 bullet points of notable findings>

### Trends
<describe upward/downward/stable trends>

### Recommendations
<2-3 actionable, specific recommendations>

RULES:
- ALWAYS call generate_report for standard report requests
- Use run_python_code for custom calculations or chart generation
- Present numbers with context — don't just dump raw data
- Highlight anomalies and outliers explicitly
- Always end with 2-3 actionable recommendations
- For trend queries, compare current vs previous period when data is available

""",
    tools=[
        generate_report,
        run_python_code,
        aggregate_metrics,
    ],
    output_key="analytics_result",
)
