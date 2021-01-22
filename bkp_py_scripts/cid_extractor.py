import json

# def get_cid_from_hit(hits):
#     cids = []
#     for hit in hits:
#         cids.append(hit["_source"]["cid"])
#     return cids

def get_data_from_file(filepath):
    with open(filepath, 'r+') as jsonFile:
        file_data = json.load(jsonFile)
        total_hits = file_data["fruit"]
        return total_hits

def compare_the_cids(engine_cid,usg_cid):
    result = set(engine_cid) - set(usg_cid)
    result1 = set(usg_cid) - set (engine_cid)
    answer = result.union(result1)
    return answer

def main():
    engine_hits = get_data_from_file("C:\\Neha\\apple.json")  
    usg_hits = get_data_from_file("C:\\Neha\\strawberry.json")
    # engine_cid = get_cid_from_hit(engine_hits)
    # usg_cid = get_cid_from_hit(usg_hits)
    # uncommon_elements = compare_the_cids(engine_cid,usg_cid)
    # print (uncommon_elements)
    print (engine_hits)
    print (usg_hits)

if __name__ == "__main__":
    main()