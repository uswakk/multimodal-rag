def fuse_results(text_results, image_results):
    """
    Combine results intelligently
    """

    # Prioritize text more than images
    for t in text_results:
        t["score"] *= 1.2

    combined = text_results + image_results

    # Sort
    combined.sort(key=lambda x: x["score"], reverse=True)

    # Remove duplicates
    seen = set()
    unique = []

    for item in combined:
        key = item.get("text", "")[:100]  # avoid duplicates
        if key in seen:
            continue
        seen.add(key)
        unique.append(item)

    return unique[:5]