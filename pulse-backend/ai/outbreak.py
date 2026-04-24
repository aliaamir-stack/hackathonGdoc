import numpy as np
from sklearn.cluster import DBSCAN

def run_dbscan(coords):
    if not coords or len(coords) < 5:
        return []
    
    # DBSCAN: eps=0.02 degrees (~2km), min_samples=5
    db = DBSCAN(eps=0.02, min_samples=5).fit(coords)
    labels = db.labels_
    
    clusters = []
    unique_labels = set(labels)
    for label in unique_labels:
        if label == -1:
            continue # Noise points
        
        cluster_points = [coords[i] for i in range(len(coords)) if labels[i] == label]
        centroid = np.mean(cluster_points, axis=0).tolist()
        clusters.append({
            "size": len(cluster_points),
            "centroid": centroid
        })
        
    return clusters
