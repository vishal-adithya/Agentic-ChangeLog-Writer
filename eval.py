from agent import agent_pipeline
from langsmith import evaluate,traceable
import re
import json
from langchain_groq import ChatGroq

judge_llm = ChatGroq(
    model = "openai/gpt-oss-20b",
    temperature=0,
    reasoning_format="parsed"
) 
JUDGE_PROMPT = """You are grading a changelog written by an AI agent from a repo's \
commit history. Rate it from 1 (poor) to 5 (excellent) as a single overall score, \
considering:
 
- Structure: follows Features / Bug Fixes / Improvements / Documentation / \
Maintenance / Breaking Changes headings, omitting empty categories.
- Grouping: related or duplicate commits merged into concise bullets, not \
listed one-for-one.
- Prioritization: user-facing changes favored over internal chores/refactors.
- Honesty: no fabricated commits, features, or details not implied by the content.
- Readability: concise, professional, ready to publish as release notes.
- If no commits were found, the changelog should say so clearly and end with \
(COMMITS_NOT_FOUND) rather than inventing content.
 
Be strict — most real outputs should NOT get a 5.
 
Respond with ONLY a JSON object, no markdown fences, no commentary:
{{"score": <int 1-5>, "rationale": "<one or two sentences>"}}
 
CHANGELOG TO GRADE:
{changelog}
"""

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
    @staticmethod
    def judge_changelog(run, exp):
        if not run.outputs or "output" not in run.outputs:
            return {"key": "changelog_quality", "score": None}
 
        ans = run.outputs["output"]
        if not ans or not ans.strip():
            return {"key": "changelog_quality", "score": 0.0}
 
        response = judge_llm.invoke(JUDGE_PROMPT.format(changelog=ans))
        raw = response.content if hasattr(response, "content") else str(response)
 
        try:
            cleaned = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
            parsed = json.loads(cleaned)
            score = parsed.get("score", 0)
            rationale = parsed.get("rationale", "")
        except (json.JSONDecodeError, AttributeError):
            return {"key": "changelog_quality", "score": None, "comment": f"Could not parse judge output: {raw[:200]}"}
 
        return {"key": "changelog_quality", "score": score / 5, "comment": rationale}

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
    data="changelog-writer-eval-models",
    evaluators=[Evaluators.judge_changelog],
    experiment_prefix= "gpt-oss-120b")