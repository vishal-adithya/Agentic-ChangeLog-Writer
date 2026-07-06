from langsmith import Client
from dotenv import load_dotenv
load_dotenv()

client = Client()

dataset = client.create_dataset(
    dataset_name="github-changelog-agent",
    description="Evaluation dataset for GitHub changelog agent"
)

examples = [
    {
        "inputs": {
            "question":
            "Generate a changelog for https://github.com/vishal-adithya/changelog-test-repo from 2026-06-29 to 2026-07-02"
        }
    },
    {
        "inputs": {
            "question":
            "Summarize commits for https://github.com/vishal-adithya/changelog-test-repo from 2026-06-25 to 2026-06-30"
        }
    },
    {
        "inputs": {
            "question":
            "Generate release notes for https://github.com/vishal-adithya/changelog-test-repo between 2026-06-29 and 2026-07-01"
        }
    },
    {
        "inputs": {
            "question":
            "Create a changelog from https://github.com/vishal-adithya/changelog-test-repo for the last week of June 2026."
        }
    },
]

client.create_examples(
    dataset_id=dataset.id,
    examples=examples
)

print("Dataset Created")