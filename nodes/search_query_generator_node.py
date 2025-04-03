from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langgraph.types import Command
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics import silhouette_score
from scipy.cluster.hierarchy import linkage, fcluster
from .llm_object_provider import get_llm
import warnings
from .constants import CONTINUE_TO_SEARCH
from .blog_state import  BlogState
from .common_methods import extract_key_points

warnings.filterwarnings("ignore")


def generate_google_search_query(cluster_points):
    """
    Example function that calls an LLM to create a search query
    based on the content of the cluster.
    """
    # We'll create a short prompt that summarizes the cluster
    # and asks for a relevant Google search query.
    prompt_text = """
    The following key points are semantically related:
    {cluster_points}

    Combine the all key points and provide a concise Google search query
    that would capture the whole key points.
    Return only the query, nothing else.
    """

    prompt = PromptTemplate(
        template=prompt_text,
        input_variables=["cluster_points"]
    )
    chain = prompt | get_llm() | StrOutputParser()

    query_text = chain.invoke({
        "cluster_points": cluster_points,
    })

    return query_text

def generate_search_query(state: BlogState) -> str:
    """
    Generate a search query based on the blog outline.
    """

    print("---GENERATING SEARCH QUERY---")
    blog_outline = state.get("outline")
    key_points = extract_key_points(blog_outline)

    with open("key_points.txt", "w") as f:
        f.write(str(key_points))

    # 1. Get embeddings using Sentence Transformers
    model = SentenceTransformer('all-MiniLM-L6-v2')  
    embeddings = model.encode(key_points)  # Returns a list of embeddings (np.ndarray)

    # 2. Compute the linkage matrix using, for example, the Ward method
    Z = linkage(embeddings, method='ward')  # shape: (num_points-1, 4)

    # Z[i, 2] is the distance at which the merge occurs at the i-th step

    # 3. Build a sorted list of candidate distance thresholds
    #    We'll take the unique distances in Z[:, 2].
    all_distances = Z[:, 2]
    unique_distances = np.unique(all_distances)

    candidate_thresholds = unique_distances

    best_threshold = None
    best_score = -1
    best_labels = None

    # 4. Evaluate silhouette score for each candidate threshold
    for t in candidate_thresholds:
        # Generate cluster labels for this threshold
        labels = fcluster(Z, t=t, criterion='distance')
        
        # If all points end up in a single cluster or if each point is its own cluster,
        # silhouette_score is not defined. We'll skip those cases.
        num_clusters = len(np.unique(labels))
        if num_clusters < 2 or num_clusters == len(labels):
            continue
        
        score = silhouette_score(embeddings, labels)
        
        if score > best_score:
            best_score = score
            best_threshold = t
            best_labels = labels

    print(f"Best threshold found: {best_threshold:.4f}")
    print(f"Best silhouette score: {best_score:.4f}")

    # 5. Now 'best_labels' contains the clustering at the best threshold
    #    We can group the key points using these labels
    cluster_dict = {}
    for kp, lbl in zip(key_points, best_labels):
        cluster_dict.setdefault(lbl, []).append(kp)

    # Let's see how many clusters we got
    print(f"Number of clusters: {len(cluster_dict)}")

    # 6) LOOP OVER CLUSTERS -> GENERATE QUERIES
    cluster_queries = []
    with open("cluster_dict.txt", "w") as f:
        for cluster_id, c_points in cluster_dict.items():
            query = generate_google_search_query(c_points)
            cluster_queries.append(query) 
            f.write(f"Cluster {cluster_id}:\n")
            f.write(str(c_points))
            f.write("\n")
            f.write(f"Query: {query}")
            f.write("\n\n")

    with open("cluster_queries.txt", "w") as f:
        f.write(str(cluster_queries))
    # 7) Return the cluster queries
    return Command(
        update = {
            "cluster_queries": cluster_queries
        },
        goto =  CONTINUE_TO_SEARCH
    )