"""Search analytics schemas for HR analytics."""

from datetime import datetime

from pydantic import BaseModel, Field


class TopQueryStats(BaseModel):
    """Top query statistics."""

    query: str = Field(..., description="Search query text")
    count: int = Field(..., description="Number of times searched")
    avg_results_count: float = Field(..., description="Average number of results")
    zero_results_count: int = Field(..., description="Number of searches with zero results")


class ZeroResultQuery(BaseModel):
    """Query with zero results statistics."""

    query: str = Field(..., description="Search query text")
    count: int = Field(..., description="Number of times searched with zero results")
    last_searched_at: datetime = Field(..., description="Last time this query was searched")


class DepartmentSearchStats(BaseModel):
    """Department search statistics."""

    department_id: int | None = Field(..., description="Department ID")
    department_name: str = Field(..., description="Department name")
    search_count: int = Field(..., description="Total number of searches")
    unique_users: int = Field(..., description="Number of unique users who searched")


class SearchTimeseriesPoint(BaseModel):
    """Search timeseries data point."""

    bucket: str = Field(..., description="Time bucket (date or week)")
    search_count: int = Field(..., description="Number of searches in this bucket")
    unique_users: int = Field(..., description="Number of unique users in this bucket")


class SearchSummary(BaseModel):
    """Overall search summary statistics."""

    total_searches: int = Field(..., description="Total number of searches")
    unique_users: int = Field(..., description="Number of unique users who searched")
    unique_queries: int = Field(..., description="Number of unique search queries")
    avg_results_per_search: float = Field(..., description="Average number of results per search")
    zero_results_percentage: float = Field(..., description="Percentage of searches with zero results")
