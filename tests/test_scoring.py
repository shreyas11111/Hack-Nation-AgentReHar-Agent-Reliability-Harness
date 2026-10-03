from types import SimpleNamespace
from gauntlet.scoring import score
def test_scoring(): assert score([SimpleNamespace(worst_severity="CRITICAL",failure_rate=1)]) == 75
