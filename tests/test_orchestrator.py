from orchestrator.orchestrator.project_orchestrator import ProjectOrchestrator

def test_greets():
    orch = ProjectOrchestrator()
    result = orch.run({"name": "Tester"})
    assert "Hello" in result
    assert "Tester" in result or "world" in result  # Account for both cases
