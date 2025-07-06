#!/usr/bin/env python3
"""
Project Orchestrator - Core brain of the SaaS Factory
Built with Google Cloud Pub/Sub for event-driven architecture
"""

import os
import json
import logging
import time
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod
from google.cloud import pubsub_v1
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pub/Sub configuration
PROJECT_ID = os.getenv("PROJECT_ID", "summer-nexus-463503-e1")
publisher = pubsub_v1.PublisherClient()
TOPIC_PATH = publisher.topic_path(PROJECT_ID, "agent-events")


def emit(event_type: str, payload: Dict[str, Any]):
    """Emit an event to Pub/Sub topic"""
    try:
        event_data = {"type": event_type, "timestamp": time.time(), **payload}
        data = json.dumps(event_data).encode("utf-8")
        future = publisher.publish(TOPIC_PATH, data)
        logger.info(f"Published event: {event_type} - {payload}")
        return future.result()  # Wait for the publish to complete
    except Exception as e:
        logger.error(f"Failed to publish event {event_type}: {str(e)}")
        # Don't raise the exception to avoid breaking the main flow
        return None


@dataclass
class TaskRequest:
    """Represents a task request to the orchestrator"""

    task_type: str
    payload: Dict[str, Any]
    request_id: str


@dataclass
class TaskResponse:
    """Represents a response from an agent"""

    request_id: str
    status: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class Agent(ABC):
    """Base Agent class following ADK patterns"""

    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(f"Agent.{name}")

    @abstractmethod
    def execute_task(self, task: TaskRequest) -> TaskResponse:
        """Execute a task and return response"""
        pass

    def log_info(self, message: str):
        """Log an info message"""
        self.logger.info(f"[{self.name}] {message}")

    def log_error(self, message: str):
        """Log an error message"""
        self.logger.error(f"[{self.name}] {message}")


class GreeterAgent(Agent):
    """Simple greeter agent for proof-of-life"""

    def __init__(self):
        super().__init__("GreeterAgent")

    def execute_task(self, task: TaskRequest) -> TaskResponse:
        """Greet the user"""
        self.log_info(f"Processing greeting task: {task.request_id}")

        # Emit START event
        emit(
            "START",
            {"stage": "greet", "agent": self.name, "request_id": task.request_id},
        )

        try:
            name = task.payload.get("name", "world")
            greeting = f"Hello, {name}! 🚀 SaaS Factory is ready to build!"

            # Emit FINISH event
            emit(
                "FINISH",
                {
                    "stage": "greet",
                    "agent": self.name,
                    "request_id": task.request_id,
                    "status": "success",
                    "result": {"greeting": greeting},
                },
            )

            return TaskResponse(
                request_id=task.request_id,
                status="success",
                result={"greeting": greeting},
            )
        except Exception as e:
            self.log_error(f"Error in greeting task: {str(e)}")

            # Emit ERROR event
            emit(
                "ERROR",
                {
                    "stage": "greet",
                    "agent": self.name,
                    "request_id": task.request_id,
                    "error": str(e),
                },
            )

            return TaskResponse(
                request_id=task.request_id, status="error", error=str(e)
            )


class IdeaAgent(Agent):
    """Agent responsible for idea generation and validation"""

    def __init__(self):
        super().__init__("IdeaAgent")

    def execute_task(self, task: TaskRequest) -> TaskResponse:
        """Generate and validate ideas"""
        self.log_info(f"Processing idea task: {task.request_id}")

        # Placeholder for actual idea generation logic
        return TaskResponse(
            request_id=task.request_id,
            status="success",
            result={"message": "Idea generation coming soon!"},
        )


class DevAgent(Agent):
    """Agent responsible for development tasks"""

    def __init__(self):
        super().__init__("DevAgent")

    def execute_task(self, task: TaskRequest) -> TaskResponse:
        """Handle development tasks"""
        self.log_info(f"Processing dev task: {task.request_id}")

        # Placeholder for actual development logic
        return TaskResponse(
            request_id=task.request_id,
            status="success",
            result={"message": "Development pipeline coming soon!"},
        )


class ProjectOrchestrator:
    """Main orchestrator that delegates tasks to specialized agents"""

    def __init__(self):
        self.logger = logging.getLogger("ProjectOrchestrator")

        # Initialize agents
        self.greeter = GreeterAgent()
        self.idea_agent = IdeaAgent()
        self.dev_agent = DevAgent()

        # Map task types to agents
        self.agents = {
            "greet": self.greeter,
            "idea": self.idea_agent,
            "dev": self.dev_agent,
        }

        self.logger.info(
            "ProjectOrchestrator initialized with agents: %s", list(self.agents.keys())
        )

    def process_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process an incoming request and delegate to appropriate agent"""
        self.logger.info(f"Processing request: {request_data}")

        try:
            # Extract task information
            task_type = request_data.get("task_type", "greet")
            payload = request_data.get(
                "payload", request_data
            )  # Use request_data as payload if no explicit payload
            import time

            request_id = request_data.get("request_id", f"req_{int(time.time())}")

            # Create task request
            task = TaskRequest(
                task_type=task_type, payload=payload, request_id=request_id
            )

            # Find appropriate agent
            agent = self.agents.get(task_type)
            if not agent:
                available_tasks = list(self.agents.keys())
                error_msg = (
                    f"Unknown task type: {task_type}. Available: {available_tasks}"
                )
                self.logger.error(error_msg)
                return {"request_id": request_id, "status": "error", "error": error_msg}

            # Execute task
            response = agent.execute_task(task)

            # Convert response to dict
            result = {
                "request_id": response.request_id,
                "status": response.status,
                "task_type": task_type,
                "agent": agent.name,
            }

            if response.result:
                result["result"] = response.result
            if response.error:
                result["error"] = response.error

            return result

        except Exception as e:
            self.logger.error(f"Error processing request: {str(e)}")
            return {
                "request_id": request_data.get("request_id", "unknown"),
                "status": "error",
                "error": str(e),
            }

    def run(self, payload: Dict[str, Any]) -> str:
        """Main entry point for the orchestrator (compatibility with original plan)"""
        self.logger.info("Running orchestrator with payload: %s", payload)

        # Default to greeting task if no task_type specified
        if "task_type" not in payload:
            payload["task_type"] = "greet"

        result = self.process_request(payload)

        # Return simple string for compatibility
        if result["status"] == "success" and "result" in result:
            if "greeting" in result["result"]:
                return result["result"]["greeting"]
            else:
                return json.dumps(result["result"])
        elif result["status"] == "error":
            return f"Error: {result['error']}"
        else:
            return json.dumps(result)


def main():
    """Main function for testing the orchestrator"""
    print("🚀 Starting SaaS Factory Project Orchestrator...")

    orchestrator = ProjectOrchestrator()

    # Test different scenarios
    test_cases = [
        {"name": "pong"},
        {"name": "Factory", "task_type": "greet"},
        {"task_type": "idea", "payload": {"description": "Build a todo app"}},
        {"task_type": "dev", "payload": {"project": "my-app"}},
        {"task_type": "unknown", "payload": {"test": "data"}},
    ]

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- Test Case {i} ---")
        print(f"Input: {test_case}")
        result = orchestrator.run(test_case)
        print(f"Output: {result}")


if __name__ == "__main__":
    main()
