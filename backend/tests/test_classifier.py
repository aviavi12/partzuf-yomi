import pytest
from app.classifiers.rule_classifier import classify_article


class TestEventClassification:
    def test_war_classification(self):
        result = classify_article(
            headline="Military forces launch attack on border region",
            summary="Troops engaged in combat operations near the border",
            source_name="AP", language="en",
        )
        assert result["event_type"] == "war"
        assert result["developmental_stage"] == "embryo"
        assert result["confidence"] > 0.5

    def test_peace_classification(self):
        result = classify_article(
            headline="Peace agreement signed after years of conflict",
            summary="The two nations signed a ceasefire and peace agreement",
            source_name="AP", language="en",
        )
        assert result["event_type"] == "peace"
        assert result["developmental_stage"] == "marriage"

    def test_economy_classification(self):
        result = classify_article(
            headline="Global economic growth slows amid trade tensions",
            summary="Economic indicators show declining GDP growth across markets",
            source_name="AP", language="en",
        )
        assert result["event_type"] == "economy"
        assert result["developmental_stage"] == "adult"

    def test_technology_classification(self):
        result = classify_article(
            headline="New AI startup raises $500M for innovation",
            summary="Tech company develops breakthrough digital technology",
            source_name="AP", language="en",
        )
        assert result["event_type"] == "technology"
        assert result["developmental_stage"] == "child"

    def test_education_hebrew(self):
        result = classify_article(
            headline="משרד החינוך מכריז על רפורמה בתכנית הלימודים",
            summary="תכנית לימודים חדשה לבתי ספר",
            source_name="Rotter", language="he",
        )
        assert result["event_type"] == "education"
        assert result["developmental_stage"] == "child"

    def test_defense_hebrew(self):
        result = classify_article(
            headline="צה\"ל מפעיל כיפת ברזל בעקבות ירי",
            summary="מערכת ההגנה כיפת ברזל הופעלה",
            source_name="Rotter", language="he",
        )
        assert result["event_type"] == "defense"
        assert result["developmental_stage"] == "embryo"

    def test_immigration_classification(self):
        result = classify_article(
            headline="Record immigration wave as refugees flee conflict",
            summary="Asylum seekers cross border amid humanitarian crisis",
            source_name="AP", language="en",
        )
        assert result["event_type"] in ["immigration", "refugees"]

    def test_elections_classification(self):
        result = classify_article(
            headline="National election campaign enters final week",
            summary="Voters prepare for ballot as parties compete for parliament seats",
            source_name="AP", language="en",
        )
        assert result["event_type"] == "elections"
        assert result["developmental_stage"] == "adult"

    def test_negotiation_classification(self):
        result = classify_article(
            headline="Diplomatic talks resume between rival nations",
            summary="Mediation and dialogue continue with new proposals",
            source_name="AP", language="en",
        )
        assert result["event_type"] in ["negotiation", "diplomacy"]

    def test_family_classification(self):
        result = classify_article(
            headline="Birth rate rises as family support programs expand",
            summary="New parenthood and fertility programs show results",
            source_name="AP", language="en",
        )
        assert result["event_type"] in ["family", "birth"]


class TestIsraelRelevance:
    def test_direct_relevance(self):
        result = classify_article(
            headline="Israel announces new defense agreement with ally",
            summary="Israeli government and IDF sign cooperation pact",
            source_name="AP", language="en",
        )
        assert result["israel_relevance"] == "direct"
        assert result["israel_relevance_score"] >= 60

    def test_direct_hebrew(self):
        result = classify_article(
            headline="ממשלת ישראל מאשרת תקציב חדש",
            summary="הכנסת אישרה את התקציב",
            source_name="Rotter", language="he",
        )
        assert result["israel_relevance"] == "direct"
        assert result["israel_relevance_score"] >= 50

    def test_indirect_relevance(self):
        result = classify_article(
            headline="Iran announces new nuclear program development",
            summary="Middle East tensions rise as Iran expands capabilities",
            source_name="AP", language="en",
        )
        assert result["israel_relevance"] == "indirect"

    def test_speculative_relevance(self):
        result = classify_article(
            headline="European trade deal finalized after long talks",
            summary="European nations agree on agricultural tariff reduction",
            source_name="AP", language="en",
        )
        assert result["israel_relevance"] == "speculative"
        assert result["israel_relevance_score"] < 30


class TestDevelopmentalStages:
    def _classify(self, headline, summary=""):
        return classify_article(headline, summary, "AP", "en")

    def test_embryo_stage(self):
        r = self._classify("Nation faces existential threat from missile attack", "Emergency alert as bombs strike infrastructure")
        assert r["developmental_stage"] == "embryo"

    def test_infant_stage(self):
        r = self._classify("WHO launches vaccination campaign for children", "Health workers provide care and food to refugees")
        assert r["developmental_stage"] == "infant"

    def test_child_stage(self):
        r = self._classify("Schools adopt new technology curriculum", "Education innovation and digital learning expand")
        assert r["developmental_stage"] == "child"

    def test_adult_stage(self):
        r = self._classify("Parliament passes new budget amid economy debate", "Government takes responsibility for fiscal policy")
        assert r["developmental_stage"] == "adult"

    def test_courtship_stage(self):
        r = self._classify("Diplomatic talks and dialogue begin between rivals", "Mediation proposals exchanged in negotiation")
        assert r["developmental_stage"] == "courtship"

    def test_marriage_stage(self):
        r = self._classify("Historic peace agreement signed between nations", "The two countries commit to long-term ceasefire truce")
        assert r["developmental_stage"] == "marriage"

    def test_new_generation_stage(self):
        r = self._classify("Record birth rate and population growth reported", "New generation demographics shift with rising fertility")
        assert r["developmental_stage"] == "new_generation"

    def test_primary_woman_stage(self):
        r = self._classify("Major bilateral cooperation agreement signed", "Nations commit to long-term joint partnership alliance")
        assert r["developmental_stage"] == "primary_woman"


class TestAnalysisStructure:
    def test_all_fields_present(self):
        result = classify_article("Test headline", "Test summary", "AP", "en")
        required = [
            "event_type", "developmental_stage", "stage_score",
            "israel_relevance", "israel_relevance_score",
            "mother_analogy", "father_analogy", "son_perspective",
            "scientific_context", "confidence", "reasoning_summary",
        ]
        for field in required:
            assert field in result, f"Missing field: {field}"

    def test_mother_analogy_structure(self):
        result = classify_article("Test", "", "AP", "en")
        assert "score" in result["mother_analogy"]
        assert "interpretation" in result["mother_analogy"]
        assert 0 <= result["mother_analogy"]["score"] <= 100

    def test_father_analogy_structure(self):
        result = classify_article("Test", "", "AP", "en")
        assert "score" in result["father_analogy"]
        assert "interpretation" in result["father_analogy"]
        assert 0 <= result["father_analogy"]["score"] <= 100

    def test_son_perspective_structure(self):
        result = classify_article("Test headline for analysis", "", "AP", "en")
        sp = result["son_perspective"]
        assert "what_is_happening" in sp
        assert "what_can_be_perceived" in sp
        assert "developmental_meaning" in sp
        assert "possible_long_term_pattern" in sp
        assert "certainty" in sp

    def test_scientific_context_metaphorical(self):
        result = classify_article("Test", "", "AP", "en")
        assert result["scientific_context"]["evidence_level"] == "metaphorical"

    def test_confidence_range(self):
        result = classify_article("Major war erupts", "Military conflict", "AP", "en")
        assert 0.0 <= result["confidence"] <= 1.0

    def test_score_range(self):
        result = classify_article("Test", "", "AP", "en")
        assert 0 <= result["stage_score"] <= 100
        assert 0 <= result["israel_relevance_score"] <= 100
