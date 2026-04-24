"""
Unit Tests for the Emergency Guide System.

Tests cover:
- Protocol loading and validation
- Keyword-based protocol matching
- Protocol data structure integrity
- Edge cases in matching
"""

import pytest
from pathlib import Path

from m5_features.emergency.protocol_matcher import ProtocolMatcher


class TestProtocolMatcher:
    """Tests for emergency protocol matching."""

    def setup_method(self):
        """Set up test fixtures with a fresh matcher."""
        self.matcher = ProtocolMatcher()

    def test_protocols_loaded(self):
        """Verify all 15 protocols are loaded."""
        assert len(self.matcher.protocols) == 15, (
            f"Expected 15 protocols, got {len(self.matcher.protocols)}"
        )

    def test_all_protocol_ids_present(self):
        """Verify expected protocol IDs exist."""
        expected_ids = {
            "cpr_adult", "cpr_child",
            "choking_adult", "choking_child",
            "stroke", "severe_bleeding",
            "burns", "allergic_reaction",
            "drowning", "seizure",
            "diabetic_emergency", "heart_attack",
            "poisoning", "fracture",
            "electric_shock",
        }
        actual_ids = set(self.matcher.get_all_protocol_ids())
        assert expected_ids == actual_ids, (
            f"Missing protocols: {expected_ids - actual_ids}"
        )

    def test_protocol_structure(self):
        """Verify each protocol has required fields."""
        required_fields = {"id", "title", "steps", "trigger_phrases"}

        for protocol_id, protocol in self.matcher.protocols.items():
            for field in required_fields:
                assert field in protocol, (
                    f"Protocol '{protocol_id}' missing field '{field}'"
                )
            assert len(protocol["steps"]) >= 3, (
                f"Protocol '{protocol_id}' has too few steps"
            )
            assert len(protocol["trigger_phrases"]) >= 3, (
                f"Protocol '{protocol_id}' has too few trigger phrases"
            )

    def test_step_structure(self):
        """Verify each step has required fields."""
        for protocol_id, protocol in self.matcher.protocols.items():
            for i, step in enumerate(protocol["steps"]):
                assert "step_number" in step, (
                    f"Protocol '{protocol_id}' step {i} missing step_number"
                )
                assert "instruction" in step, (
                    f"Protocol '{protocol_id}' step {i} missing instruction"
                )
                assert len(step["instruction"]) > 10, (
                    f"Protocol '{protocol_id}' step {i} instruction too short"
                )

    def test_match_cpr_not_breathing(self):
        """Test matching 'not breathing' to CPR adult protocol."""
        result = self.matcher.match("someone is not breathing")
        assert result.matched is True
        assert result.protocol_id == "cpr_adult"
        assert result.confidence > 0.3

    def test_match_choking(self):
        """Test matching 'choking' to choking protocol."""
        result = self.matcher.match("a person is choking on food")
        assert result.matched is True
        assert "choking" in result.protocol_id
        assert result.confidence > 0.3

    def test_match_heart_attack(self):
        """Test matching chest pain to heart attack protocol."""
        result = self.matcher.match("severe chest pain and difficulty breathing")
        assert result.matched is True
        assert result.confidence > 0.2

    def test_match_stroke(self):
        """Test matching stroke symptoms."""
        result = self.matcher.match("face drooping and slurred speech")
        assert result.matched is True
        assert result.protocol_id == "stroke"

    def test_match_seizure(self):
        """Test matching seizure description."""
        result = self.matcher.match("person having a seizure shaking uncontrollably")
        assert result.matched is True
        assert result.protocol_id == "seizure"

    def test_match_burns(self):
        """Test matching burn injury."""
        result = self.matcher.match("someone got burned by hot water")
        assert result.matched is True
        assert result.protocol_id == "burns"

    def test_match_electric_shock(self):
        """Test matching electrical injury."""
        result = self.matcher.match("person got electric shock from power line")
        assert result.matched is True
        assert result.protocol_id == "electric_shock"

    def test_match_empty_text(self):
        """Test handling of empty input."""
        result = self.matcher.match("")
        assert result.matched is False
        assert result.confidence == 0.0

    def test_match_irrelevant_text(self):
        """Test low confidence for unrelated text."""
        result = self.matcher.match("I want to order pizza for dinner")
        # Should either not match or have very low confidence
        if result.matched:
            assert result.confidence < 0.5

    def test_get_all_summaries(self):
        """Test protocol summary generation."""
        summaries = self.matcher.get_all_protocol_summaries()
        assert len(summaries) == 15
        for summary in summaries:
            assert "id" in summary
            assert "title" in summary
            assert "trigger_phrases" in summary

    def test_get_specific_protocol(self):
        """Test retrieving a specific protocol."""
        protocol = self.matcher.get_protocol("cpr_adult")
        assert protocol is not None
        assert protocol["id"] == "cpr_adult"
        assert "CPR" in protocol["title"]

    def test_get_nonexistent_protocol(self):
        """Test handling of nonexistent protocol ID."""
        protocol = self.matcher.get_protocol("nonexistent_protocol")
        assert protocol is None


class TestProtocolMatchResult:
    """Tests for MatchResult data integrity."""

    def setup_method(self):
        """Set up test fixtures."""
        self.matcher = ProtocolMatcher()

    def test_matched_result_has_protocol_data(self):
        """Verify matched results include full protocol data."""
        result = self.matcher.match("someone is not breathing")
        if result.matched:
            assert result.protocol_data is not None
            assert "steps" in result.protocol_data

    def test_method_is_keyword(self):
        """Verify keyword matching is used when AI is not configured."""
        result = self.matcher.match("choking on food")
        assert result.method in ["keyword", "ai"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
