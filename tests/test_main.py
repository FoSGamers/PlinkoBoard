import json
import os

def test_rewards_template(tmp_path):
    rewards = ["A", "B", "C"]
    file_path = tmp_path / "rewards.json"
    with open(file_path, "w") as f:
        json.dump(rewards, f)
    with open(file_path, "r") as f:
        loaded = json.load(f)
    assert loaded == rewards 