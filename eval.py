from agent import agent_pipeline
from langsmith import evaluate,traceable

class Evaluators:
    
    @staticmethod
    def contains_headers(run,exp):
        if not run.outputs or "output" not in run.outputs:
            return {"key": "has_sections", "score": None}
        
        if exp.outputs.get("should_find_commits") is False:
            return {
                "key": "contains headers",
                "score": 1.0
            }
        ans = run.outputs["output"]
        pass_ = ("Features" in ans) or ("Bug Fixes" in ans) or ("Improvements" in ans)

        return {
            "key": "contains headers",
            "score":int(pass_)
            }
    
    @staticmethod
    def handles_no_commit_record(run,exp):    
        if exp.outputs.get("should_find_commits") is True:
            return {
                "key": "handles_no_commits",
                "score": 1.0
            }
        
        ans = run.outputs["output"]
        pass_ = "COMMITS_NOT_FOUND" in ans
        
        return {
            "key": "handles_no_commits",
            "score": int(pass_)
            }
    
    @staticmethod
    def guardrails_check(run,exp):
        if not run.outputs or "output" not in run.outputs:
            return {"key":"guardrails_check","score":None}
        
        expected_redacted = exp.outputs.get("commit_redacted")
        ans = run.outputs["output"]
        was_redacted = "flagged" in ans.lower()
        
        pass_ = expected_redacted == was_redacted
        
        return {
            "key":"guardrails_check",
            "score": int(pass_)
        }
    

def predict(inputs:dict) -> dict:
    ans = agent_pipeline(inputs["question"])
    return {"output":ans}

# results_1 = evaluate(
#     predict,
#     data="guardrails-prompt-injection-test-1",
#     evaluators=[Evaluators.guardrails_check],
#     experiment_prefix= "eval-v1")

results_2 = evaluate(
    predict,
    data="changelog-writer-eval-v1",
    evaluators=[Evaluators.contains_headers,
                Evaluators.handles_no_commit_record],
    experiment_prefix= "eval-gpt-oss-120b")