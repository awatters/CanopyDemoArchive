
import json
f = file("demo_metadata.json")
t = f.read()
j = json.loads(t)
print "json ok"
