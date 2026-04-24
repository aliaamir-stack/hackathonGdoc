def run_dbscan(coords):
    if not coords:
        return []
    return [{"size": len(coords), "centroid": coords[0]}]
