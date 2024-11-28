
from __future__ import annotations

from vertexai.language_models import TextEmbeddingInput, TextEmbeddingModel
from vertexai.language_models import TextEmbeddingInput, TextEmbeddingModel
import openparse

file_path = r'C:\work\yangji\src\insurance-demo\src\data'
file_path = r"C:\work\yangji\src\insurance-demo\src\data\★(제2024-181호, 9.12.) 요양급여의 적용기준 및 방법에 관한 세부사항 일부개정안_v3.pdf"

import openparse
from openparse import processing, Pdf


class MinimalIngestionPipeline(processing.IngestionPipeline):
    def __init__(self):
        self.transformations = [
            # combines bullets and weird formatting
            processing.CombineNodesSpatially(
                x_error_margin=10,
                y_error_margin=2,
                criteria="both_small",
            ),
            processing.CombineHeadingsWithClosestText(),
            processing.CombineBullets(),
            processing.RemoveMetadataElements(),
            processing.RemoveNodesBelowNTokens(min_tokens=10),
        ]

parser = openparse.DocumentParser(
    processing_pipeline=MinimalIngestionPipeline(),
)
# parsed_basic_doc = parser.parse(file_path)
parsed_content = parser.parse(file_path)

# for i in parsed_basic_doc.nodes:
#     print(i)

from openparse import Node
from openparse import processing
import numpy as np
from IPython.display import display, Image

MODEL_NAME = "text-multilingual-embedding-002"
DIMENSIONALITY = 768


def embed_text(
    texts: list[str] = ["Retrieve a function that adds two numbers"],
    task: str = "FACT_VERIFICATION",
    model_name: str = "text-embedding-005",
    dimensionality: int | None = 768,
) -> list[list[float]]:
    """Embeds texts with a pre-trained, foundational model."""
    model = TextEmbeddingModel.from_pretrained(model_name)
    inputs = [TextEmbeddingInput(text, task) for text in texts]
    kwargs = dict(output_dimensionality=dimensionality) if dimensionality else {}
    embeddings = model.get_embeddings(inputs, **kwargs)
    # Example response:
    # [[0.025890009477734566, -0.05553026497364044, 0.006374752148985863,...],
    return [embedding.values for embedding in embeddings]

def cosine_similarity(
    a: np.ndarray | list[float], b: np.ndarray | list[float]
) -> float:
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def get_node_similarities(nodes: list[Node]):
    # Filter out nodes with empty text
    non_empty_nodes = [node for node in nodes if node.text.strip()]
    
    # Get the similarity of each node with the node that precedes it
    embeddings = embed_text([node.text for node in non_empty_nodes], task="FACT_VERIFICATION")
    similarities = []
    for i in range(1, len(embeddings)):
        similarities.append(cosine_similarity(embeddings[i - 1], embeddings[i]))

    similarities = [round(sim, 2) for sim in similarities]
    return [0] + similarities


doc = Pdf(file=file_path)

# print("parsed_content.nodes", parsed_content.nodes)
print("text embedding started")
print([node.text for node in parsed_content.nodes])
annotations = get_node_similarities(parsed_content.nodes)
# Ensure the number of annotations matches the number of nodes
if len(annotations) < len(parsed_content.nodes):
    annotations.extend([0] * (len(parsed_content.nodes) - len(annotations)))
elif len(annotations) > len(parsed_content.nodes):
    annotations = annotations[:len(parsed_content.nodes)]

images = doc.display_with_bboxes(
    parsed_content.nodes, annotations=annotations, page_nums=[2, 3, 4]
)

# Display images in a separate window
if images:
    for img in images:
        display(Image(img))
else:
    print("No images to display")