import json, os, sys
os.chdir(os.path.dirname(os.path.abspath(__file__)))
total = 0
for f in ["part1.json", "part2.json", "part3a.json", "part3b.json"]:
    d = json.load(open(f, encoding="utf-8"))
    items = [(c["title"], len(c["items"])) for c in d["categories"]]
    n = sum(len(c["items"]) for c in d["categories"])
    total += n
    print(f, "->", items)
    # validate schema
    for c in d["categories"]:
        for it in c["items"]:
            assert set(it) >= {"n", "title", "desc", "examples"}, it["n"]
            for ex in it["examples"]:
                assert set(ex) >= {"name", "loc", "facts", "v"}, it["n"]
                assert ex["v"] in ("ok", "warn"), ex
print("TOTAL items:", total)
