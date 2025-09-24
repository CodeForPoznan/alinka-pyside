import pytest

from alinka.db.queries import (
    create_decision_in_db,
    filter_decisions_by_pesel_child_name,
    get_decision_data_by_id,
    get_decisions_list_from_db,
    get_support_center_data,
    update_decision_in_db,
    upsert_support_center,
)
from alinka.schemas.db_schema import SupportCenterDbSchema
from tests.factories import DecisionFactory, SupportCenterFactory
from tests.fixtures import decision_data


class TestQuery:
    def setup_method(self):
        DecisionFactory.create_batch(
            2,
            create_new_school=True,
            create_new_meeting_members=True,
        )
        self.decision_data = decision_data.copy()
        self.decision_1, self.decision_2 = get_decisions_list_from_db()

    def test_get_decision_list_from_db_successful(self):
        decisions = get_decisions_list_from_db()
        assert decisions == [self.decision_1, self.decision_2]

    def test_get_decision_data_from_db(self):
        decision = get_decision_data_by_id(decision_id=self.decision_1.id)
        assert decision == self.decision_1

    def test_create_decision_id_db(self):
        del decision_data["id"], decision_data["created_at"], decision_data["modified_at"]
        decision = create_decision_in_db(decision_data=decision_data)
        assert decision.child_full_name == decision_data["child_full_name"]

    def test_update_decision_in_db(self):
        new_child_name = "new child name"
        decision = update_decision_in_db(self.decision_1.id, decision_data={"child_full_name": new_child_name})
        assert decision.child_full_name == new_child_name

    def test_upsert_support_center__not_existing(self):
        support_center_data = SupportCenterDbSchema(
            province_id=5,
            district_id=3,
            rspo=12,
            name_nominative="Poradnia Psychologiczno - Pedagogiczna w Kłecku",
            name_genitive="Poradni Psychologiczno - Pedagogicznej w Kłecku",
            institute_name="zespół orzekający przy Poradni Psychologiczno - Pedagogicznej w Kłecku",
            kurator="kurator w Poznaniu",
            address="ul. Urocza 12",
            town="Kłecko",
            postal_code="78-222",
            post="Kłecko",
        )

        support_center = upsert_support_center(support_center_data.model_dump())
        assert support_center.name_nominative == support_center_data.name_nominative

    def test_upsert_support_center__existing(self):
        SupportCenterFactory()

        support_center_data = SupportCenterDbSchema(
            province_id=5,
            district_id=3,
            rspo=12,
            name_nominative="Poradnia Psychologiczno - Pedagogiczna w Kłecku",
            name_genitive="Poradni Psychologiczno - Pedagogicznej w Kłecku",
            institute_name="zespół orzekający przy Poradni Psychologiczno - Pedagogicznej w Kłecku",
            kurator="kurator w Poznaniu",
            address="ul. Urocza 12",
            town="Kłecko",
            postal_code="78-222",
            post="Kłecko",
        )

        support_center = upsert_support_center(support_center_data.model_dump())
        assert support_center.name_nominative == support_center_data.name_nominative

    def test_get_support_center__exists(self):
        SupportCenterFactory()

        assert get_support_center_data()

    @pytest.mark.parametrize(
        "filter_by, expected_ids", [("7411", [3, 5]), ("xx", [3, 4]), ("abc", [3, 5]), (None, [1, 2, 3, 4, 5])]
    )
    def test_get_decisions_by_pesel_child_name(self, filter_by, expected_ids):
        DecisionFactory(child_full_name="Xxxxabc", child_pesel="74112442575")
        DecisionFactory(child_full_name="xxx", child_pesel="94111076597")
        DecisionFactory(child_full_name="abc", child_pesel="74110952166")

        result = filter_decisions_by_pesel_child_name(filter_by)
        assert set([r.id for r in result]) == set(expected_ids)


class TestQueryWithoutDecisions:
    # It was moved here, as running DecisionFactory
    # creates SupportCenter
    def test_get_support_center__not_exists(self):
        assert not get_support_center_data()
