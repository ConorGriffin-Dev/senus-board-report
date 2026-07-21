"""Model exports. Importing this module registers every table on Base.metadata."""

from app.models.insight import Insight

from app.models.financial import FinancialLineItem, Segment
from app.models.metrics import ComputedMetric, MetricLineItemLink, Target
from app.models.source import ExtractionRun, ReportingPeriod, SourceDocument

__all__ = [
    "ComputedMetric",
    "ExtractionRun",
    "FinancialLineItem",
    "Insight",
    "MetricLineItemLink",
    "ReportingPeriod",
    "Segment",
    "SourceDocument",
    "Target",
]
