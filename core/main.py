# core/main.py

import riya_engine.runtime.runtime_subscribers

from riya_engine.intent.detector import intent_detector

from riya_engine.planner.planner import planner

from riya_engine.runtime.task_manager import task_manager

from riya_engine.runtime.orchestrator import orchestrator

from riya_engine.runtime.execution_context import ExecutionContext

from riya_engine.state.runtime_state import runtime_state

from riya_engine.memory.runtime_memory import runtime_memory

from riya_engine.nlp.pipeline import nlp_pipeline

from riya_engine.runtime.event_bus import event_bus

from riya_engine.runtime.event_types import (
    INPUT_RECEIVED,
    INTENT_DETECTED,
    PLAN_CREATED,
    WORKFLOW_STARTED,
    WORKFLOW_COMPLETED,
    WORKFLOW_FAILED,
    STEP_STARTED,
    STEP_COMPLETED,
    STEP_FAILED,
)

import riya_engine.runtime.debug_subscriber

from riya_engine.workflows.workflow_manager import workflow_manager





def run():

    print("\n========== RIYA V2 ==========\n")

    while True:

        user_input = input("You: ")

        event_bus.emit(
            INPUT_RECEIVED,
            {"input": user_input}
        )

        # ==========================================
        # EXIT
        # ==========================================

        if user_input.lower() in ["exit", "quit"]:

            print("\nRiya: Goodbye\n")

            break

        # ==========================================
        # EXECUTION CONTEXT
        # ==========================================

        context = ExecutionContext(user_input=user_input)

        # ==========================================
        # NLP PIPELINE
        # ==========================================

        processed_commands = nlp_pipeline.process(user_input)

        # ==========================================
        # PER-COMMAND LIFECYCLE
        # ==========================================

        for command in processed_commands:

            print("\n[NLP COMMAND]")
            print(command)

            # ---- Intent Detection ----

            intent_response = intent_detector.detect(command)

            print("\n[INTENT]")
            print(intent_response.to_dict())

            if intent_response.intent == "UNKNOWN":

                print("\nRiya: I don't understand that command.\n")

                continue

            event_bus.emit(
                INTENT_DETECTED,
                intent_response.to_dict()
            )

            # ---- Planning ----

            plan = planner.create_plan(intent_response)

            print("\n[PLAN]")
            print(plan)

            if not plan:

                print("\nRiya: No plan generated for this intent.\n")

                continue

            event_bus.emit(
                PLAN_CREATED,
                {"plan": plan}
            )


            workflow = workflow_manager.create_workflow(
                intent_response.intent,
                plan
            )

            workflow_manager.start_workflow(workflow)

            event_bus.emit(
                WORKFLOW_STARTED,
                workflow
            )

            # ---- Task Execution ----

            step_failed_flag = False

            for step in workflow["steps"]:

                try:

                    # STEP RUNNING
                    workflow_manager.start_step(
                        workflow,
                        step["step"]
                    )

                    event_bus.emit(
                        STEP_STARTED,
                        step
                    )

                    task = task_manager.create_task(
                        step["capability"],
                        step["payload"]
                    )

                    task["workflow_id"] = workflow["workflow_id"]

                    success = orchestrator.execute_task(task)

                    # CONTROLLED FAILURE PROPAGATION
                    # (task already marked failed by orchestrator)
                    if not success:

                        step["error"] = task.get(
                            "error",
                            "Unknown task failure"
                        )

                        workflow_manager.fail_step(
                            workflow,
                            step["step"]
                        )

                        event_bus.emit(
                            STEP_FAILED,
                            step
                        )

                        step_failed_flag = True
                        break

                    workflow_manager.complete_step(
                        workflow,
                        step["step"]
                    )

                    event_bus.emit(
                        STEP_COMPLETED,
                        step
                    )

                except Exception as e:

                    # Unexpected exception from capability or plumbing
                    step["error"] = str(e)

                    workflow_manager.fail_step(
                        workflow,
                        step["step"]
                    )

                    event_bus.emit(
                        STEP_FAILED,
                        step
                    )

                    step_failed_flag = True
                    break

            if step_failed_flag:

                workflow_manager.fail_workflow(workflow)

                event_bus.emit(
                    WORKFLOW_FAILED,
                    workflow
                )

            else:

                workflow_manager.complete_workflow(
                    workflow
                )

                event_bus.emit(
                    WORKFLOW_COMPLETED,
                    workflow
                )

        # ==========================================
        # STATE OUTPUT
        # ==========================================

        print("\n[ACTIVE TASKS]")
        print(runtime_state.active_tasks)

        print("\n[COMPLETED TASKS]")
        print(runtime_state.completed_tasks)

        print("\n[FAILED TASKS]")
        print(runtime_state.failed_tasks)

        print("\n[MEMORY]")
        print(runtime_memory.get_history())

        print("\n[EXECUTION FINISHED]\n")


if __name__ == "__main__":

    run()