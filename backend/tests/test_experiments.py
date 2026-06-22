import tempfile
from pathlib import Path

from app.services.experiment_tracker_service import ExperimentTracker


def test_experiment_crud():
    with tempfile.TemporaryDirectory() as tmp:
        store = Path(tmp) / "experiments.json"
        tracker = ExperimentTracker(store_path=store)

        run_id = tracker.log_run(
            session_id="sess-1",
            model_name="xgboost",
            task_type="regression",
            metrics={"rmse": 0.5},
        )
        assert run_id

        runs = tracker.list_runs("sess-1")
        assert len(runs) == 1
        assert runs[0]["model_name"] == "xgboost"

        record = tracker.get_run(run_id)
        assert record is not None
        assert record["metrics"]["rmse"] == 0.5
