import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics import silhouette_score
from scipy.cluster.hierarchy import linkage, fcluster
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from decouple import config
import warnings

warnings.filterwarnings("ignore")

GPT_MODEL = config('GPT_MODEL', default='gpt-3.5-turbo')
OPENAI_API_KEY = config('OPENAI_API_KEY')

llm = ChatOpenAI(model_name=GPT_MODEL, temperature=0.7, openai_api_key=OPENAI_API_KEY)

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
    chain = prompt | llm | StrOutputParser()

    query_text = chain.invoke({
        "cluster_points": cluster_points,
    })

    return query_text


file_path = "key_points.txt"

with open(file_path, "r", encoding="utf-8") as file:
    key_points_list = [line.strip() for line in file.readlines()]

# 1. Get embeddings using Sentence Transformers
model = SentenceTransformer('all-MiniLM-L6-v2')  
embeddings = model.encode(key_points_list)  # Returns a list of embeddings (np.ndarray)

# 2. Compute the linkage matrix using, for example, the Ward method
Z = linkage(embeddings, method='ward')  # shape: (num_points-1, 4)

# Z[i, 2] is the distance at which the merge occurs at the i-th step

# 3. Build a sorted list of candidate distance thresholds
#    We'll take the unique distances in Z[:, 2].
all_distances = Z[:, 2]
unique_distances = np.unique(all_distances)

candidate_thresholds = unique_distances

print(f"Number of candidate thresholds: {len(candidate_thresholds)}")

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
for kp, lbl in zip(key_points_list, best_labels):
    cluster_dict.setdefault(lbl, []).append(kp)

# Let's see how many clusters we got
print(f"Number of clusters: {len(cluster_dict)}")


# 6) LOOP OVER CLUSTERS -> GENERATE QUERIES
cluster_queries = []
for cluster_id, c_points in cluster_dict.items():
    query = generate_google_search_query(c_points)
    print(f"Cluster {cluster_id}: {query}\n")