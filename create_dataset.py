from langsmith import Client
from dotenv import load_dotenv
load_dotenv()

client = Client()

DATASET_NAME = "changelog-writer-eval-v1"

EXAMPLES = [
    {
        "inputs": {
            "question": "https://github.com/vishal-adithya/changelog-test-repo, from 2026-06-29 to 2026-07-02"
        },
        "outputs": {
            "should_find_commits": True,
        },
    },
    {
        "inputs": {
            "question": "https://github.com/vishal-adithya/changelog-test-repo, from 2020-01-01 to 2020-01-02"
        },
        "outputs": {
            "should_find_commits": False,
        },
    },
]

dataset = client.create_dataset(dataset_name=DATASET_NAME)
client.create_examples(
    inputs=[ex["inputs"] for ex in EXAMPLES],
    outputs=[ex["outputs"] for ex in EXAMPLES],
    dataset_id=dataset.id)

print("Dataset Created!!")