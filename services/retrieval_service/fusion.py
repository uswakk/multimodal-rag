def fuse_results(text_results, image_results):

    combined = text_results + image_results

    # sort by score
    combined.sort(key=lambda x: x["score"], reverse=True)

    return combined[:5]