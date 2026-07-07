from agent import agent_pipeline
from langsmith import evaluate,traceable

class Evaluators:
    
    @staticmethod
    def contains_headers(run,exp):
        if not run.outputs or "output" not in run.outputs:
            return {"key": "has_sections", "score": None}
        
        ans = run.outputs["output"]
        pass_ = ("Features" in ans) or ("Bug Fixes" in ans) or ("Improvements" in ans)

        return {
            "key": "contains headers",
            "score":int(pass_)
            }
    
    @staticmethod
    def handles_no_commit_record(run,exp):
        if not run.outputs or "output" not in run.outputs:
            return {"key": "has_sections", "score": None}
        
        if exp.outputs.get("should_find_commits") is not False:
            return {
                "key": "handles_no_commits",
                "score": None
            }
        
        ans = run.outputs["output"].lower()
        pass_ = "no commits" in ans
        
        return {
            "key": "handles_no_commits",
            "score": int(pass_)
            }
    

def predict(inputs:dict) -> dict:
    ans = agent_pipeline(inputs["question"])
    return {"output":ans}

results = evaluate(
    predict,
    data="changelog-writer-eval-v1",
    evaluators=[
        Evaluators.contains_headers,
        Evaluators.handles_no_commit_record],
    experiment_prefix= "eval-v1"
)