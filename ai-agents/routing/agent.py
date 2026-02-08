"""Routing agent: team assignment (Gemini + rules fallback), formatting, context links."""

from __future__ import annotations

import logging

from ai.models.report import IssueReport, Team
from ai.routing.rules import assign_team_by_rules, extract_context_links, format_alert_summary
from ai.routing.types import RoutedAlert

logger = logging.getLogger(__name__)


class RoutingAgent:
    """Enriches reports with team, context_links, and formatted_summary. Requires Gemini API key."""

    def __init__(self, gemini_api_key: str, gemini_model: str = "gemini-2.5-flash") -> None:
        if not (gemini_api_key and gemini_api_key.strip()):
            raise ValueError("gemini_api_key is required")
        self._gemini_api_key = gemini_api_key.strip()
        self._gemini_model = (gemini_model or "gemini-2.5-flash").strip()

    def enrich(
        self,
        report: IssueReport,
        screenshot_url: str,
        test_id: str,
    ) -> RoutedAlert:
        team = self._team_from_gemini(report)
        if team is not None:
            report.team = team
        else:
            report.team = assign_team_by_rules(report)

        if not isinstance(report.metadata, dict):
            report.metadata = {}
        context_links = extract_context_links(report)
        if context_links:
            report.metadata["context_links"] = context_links

        return RoutedAlert(
            report=report,
            screenshot_url=screenshot_url,
            test_id=test_id,
            context_links=context_links or None,
            formatted_summary=format_alert_summary(report),
        )

    def _team_from_gemini(self, report: IssueReport) -> Team | None:
        team_names = [t.value for t in Team]
        prompt = (
            f"Which team owns this bug? Reply with exactly one of: {', '.join(team_names)}\n\n"
            f"Title: {report.title}\nCategory: {report.category}\nRoot cause: {report.root_cause[:300]}"
        )
        try:
            text = self._gemini_generate(prompt)
        except Exception as e:
            logger.warning("Gemini team assignment failed: %s", e)
            return None
        if not text:
            return None
        text_upper = text.strip().upper()
        for t in Team:
            if t.value.upper() in text_upper or t.name in text_upper:
                return t
        return None

    def _gemini_generate(self, prompt: str) -> str:
        try:
            from google import genai
            client = genai.Client(api_key=self._gemini_api_key)
            response = client.models.generate_content(model=self._gemini_model, contents=prompt)
            return getattr(response, "text", None) or str(response) or ""
        except ImportError:
            import google.generativeai as genai
            genai.configure(api_key=self._gemini_api_key)
            model = genai.GenerativeModel(self._gemini_model)
            response = model.generate_content(prompt)
            return getattr(response, "text", None) or str(response) or ""
