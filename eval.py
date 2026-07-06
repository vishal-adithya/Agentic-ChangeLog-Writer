from langsmith import traceable,evaluate
from agent import agent_pipeline

from langchain_google_genai import ChatGoogleGenerativeAI

judge = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-lite",
    temperature=0
)
@traceable
def target(inputs):
    answer = agent_pipeline(inputs["question"])

    return {
        "answer": answer
    }

def debug_evaluator(*args, **kwargs):
    print("=" * 80)
    print("ARGS:")
    for i, arg in enumerate(args):
        print(f"arg[{i}] ({type(arg)}):")
        print(arg)

    print("=" * 80)
    print("KWARGS:")
    for k, v in kwargs.items():
        print(f"{k} ({type(v)}):")
        print(v)

    return {
        "key": "debug",
        "score": 1
    }

results = evaluate(
    target,
    data="github-changelog-agent",
    evaluators=[debug_evaluator],
)

# def markdown_evaluator(outputs, **kwargs):
#     answer = outputs["answer"]

#     score = "#" in answer

#     return {
#         "key": "markdown",
#         "score": score
#     }

# def hallucination(outputs, **kwargs):

#     answer = outputs["answer"].lower()

#     banned = [
#         "i assume",
#         "probably",
#         "maybe",
#         "likely"
#     ]

#     score = not any(x in answer for x in banned)

#     return {
#         "key": "hallucination",
#         "score": score
#     }

# def section_evaluator(outputs, **kwargs):

#     answer = outputs["answer"]

#     headers = [
#         "Features",
#         "Bug",
#         "Improvement",
#         "Documentation",
#         "Maintenance"
#     ]

#     found = sum(
#         h.lower() in answer.lower()
#         for h in headers
#     )

#     return {
#         "key": "sections",
#         "score": found / len(headers)
#     }

# def llm_judge(inputs, outputs, **kwargs):
#     print("=================================================================================================")
#     print("INPUTS:", inputs)
#     print("=================================================================================================")
#     print("OUTPUTS:", outputs)
#     print("=================================================================================================")
#     print("KWARGS:", kwargs)
#     print("=================================================================================================")

#     return {"key": "debug", "score": 1}

# results = evaluate(
#     target,
#     data="github-changelog-agent",
#     evaluators=[
#         markdown_evaluator,
#         section_evaluator,
#         hallucination,
#         llm_judge,
#     ],
#     experiment_prefix="v1"
# )

# print(results)