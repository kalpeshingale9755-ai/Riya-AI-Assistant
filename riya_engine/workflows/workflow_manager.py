import uuid

from riya_engine.workflows.workflow_state import *


class WorkflowManager:

    def __init__(self):

        self.active_workflows = {}

        self.completed_workflows = {}

        self.failed_workflows = {}

    # ==========================================
    # CREATE WORKFLOW
    # ==========================================

    def create_workflow(self, intent, steps):

        workflow_id = str(uuid.uuid4())

        workflow = {

            "workflow_id": workflow_id,

            "intent": intent,

            "state": WORKFLOW_PENDING,

            "steps": [],

        }

        for step in steps:

            workflow["steps"].append({

                "step": step.get("step"),

                "capability": step.get("capability"),

                "payload": step.get("payload"),

                "state": STEP_PENDING

            })

        self.active_workflows[workflow_id] = workflow

        return workflow

    # ==========================================
    # START WORKFLOW
    # ==========================================

    def start_workflow(self, workflow):

        workflow["state"] = WORKFLOW_RUNNING

    # ==========================================
    # STEP SUCCESS
    # ==========================================

    def complete_step(self, workflow, step_number):

        for step in workflow["steps"]:

            if step["step"] == step_number:

                step["state"] = STEP_SUCCESS

    # ==========================================
    # STEP FAILED
    # ==========================================

    def fail_step(self, workflow, step_number):

        for step in workflow["steps"]:

            if step["step"] == step_number:

                step["state"] = STEP_FAILED

    # ==========================================
    # FAIL WORKFLOW
    # ==========================================

    def fail_workflow(self, workflow):

        workflow["state"] = WORKFLOW_FAILED

        workflow_id = workflow["workflow_id"]

        self.failed_workflows[workflow_id] = workflow

        if workflow_id in self.active_workflows:

            del self.active_workflows[workflow_id]

    # ==========================================
    # COMPLETE WORKFLOW
    # ==========================================

    def complete_workflow(self, workflow):

        workflow["state"] = WORKFLOW_SUCCESS

        workflow_id = workflow["workflow_id"]

        self.completed_workflows[workflow_id] = workflow

        if workflow_id in self.active_workflows:

            del self.active_workflows[workflow_id]

    
    def start_step(self, workflow, step_number):
        for step in workflow["steps"]:
            if step["step"] == step_number:
                step["state"] = STEP_RUNNING
                break


workflow_manager = WorkflowManager()