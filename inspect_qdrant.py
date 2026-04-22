#!/usr/bin/env python3
"""
Inspect Qdrant collections and their data.
"""
from qdrant_client import QdrantClient
import json

client = QdrantClient(url="http://localhost:6333")

print("=" * 60)
print("QDRANT COLLECTIONS OVERVIEW")
print("=" * 60)

try:
    collections = client.get_collections()
    print(f"\nTotal collections: {len(collections.collections)}\n")
    
    for col in collections.collections:
        print(f"Collection: {col.name}")
        print(f"  Points count: {col.points_count}")
        print(f"  Status: {col.status}")
        
        # Get collection info
        info = client.get_collection(col.name)
        vector_size = info.config.params.vectors.size
        print(f"  Vector size: {vector_size}-dim")
        print()
    
    # Get point counts
    print("\n" + "=" * 60)
    print("DETAILED POINT COUNTS")
    print("=" * 60)
    
    for col in collections.collections:
        try:
            count = client.count(col.name)
            print(f"{col.name}: {count.count} points")
            
            # Sample a point if available
            if count.count > 0:
                points = client.scroll(col.name, limit=1)
                if points[0]:
                    sample = points[0][0]
                    print(f"  Sample point ID: {sample.id}")
                    if sample.payload:
                        print(f"  Payload keys: {list(sample.payload.keys())}")
        except Exception as e:
            print(f"{col.name}: Error retrieving info - {e}")
    
except Exception as e:
    print(f"Error: {e}")
