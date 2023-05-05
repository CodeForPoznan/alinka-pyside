from db.queries import (
    create_decision_in_db,
    get_decision_data_from_db,
    get_decisions_list_from_db,
    update_decision_in_db,
)
from tests.factories import DecisionFactory
from tests.fixtures import decision_data


class TestQuery:
    def setup_method(self):
        DecisionFactory()
        DecisionFactory()
        self.decision_data = decision_data.copy()
        self.decision_1, self.decision_2 = get_decisions_list_from_db()

    def test_get_decision_list_from_db_successful(self):
        decisions = get_decisions_list_from_db()
        assert decisions == [self.decision_1, self.decision_2]

    def test_get_decision_data_from_db(self):
        decision = get_decision_data_from_db(decision_id=self.decision_1.id)
        assert decision == self.decision_1

    def test_create_decision_id_db(self):
        del decision_data["id"], decision_data["created_at"], decision_data["modified_at"]
        decision = create_decision_in_db(decision_data=decision_data)
        assert decision.child_first_name == decision_data["child_first_name"]

    def test_update_decision_in_db(self):
        new_child_name = "new child name"
        decision = update_decision_in_db(self.decision_1.id, decision_data={"child_first_name": new_child_name})
        assert decision.child_first_name == new_child_name
