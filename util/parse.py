from math import sqrt
from xml.dom.minidom import parse, parseString

def getPoints(path):
    points = []
    pathString = path.getAttribute("d")
    mode = pathString[0]
    
    if not (mode == "M" or mode == "m"):
        die("unsupported line mode")
    
    lastx, lasty = None, None
    for point in pathString[2:].split(" "):
        x, y = point.split(",")
        x, y = float(x), float(y)
        if mode == "M" or lastx is None:
            points.append((x, y))
        elif mode == "m":
            points.append((x + lastx, y + lasty))
        lastx, lasty = x, y
    return points
    
def getTimeStamps(texts):
    timestamps = []
    for text in texts:
        x = float(text.getAttribute("x"))
        y = float(text.getAttribute("y"))
        data = text.getElementsByTagName("tspan")[0].firstChild.data
        timestamps.append(((x, y), data))
    return timestamps
    
def getHitbox(hb):
    x = float(hb.getAttribute("sodipodi:cx"))
    y = float(hb.getAttribute("sodipodi:cy"))
    r = float(hb.getAttribute("sodipodi:radius"))
    return (x, y, r)
    
def associate(points, timestamps):
    results = []
    for i in range(len(points)):
        best = None
        bestdist = 9999999
        for j in range(len(timestamps)):
            dist = distance(points[i], timestamps[j][0])
            if dist < bestdist:
                best = timestamps[j][1]
                bestdist = dist
        results.append((points[i], best))
    return results

def distance(a, b):
    x = a[0] - b[0]
    y = a[1] - b[1]
    return sqrt(x * x + y * y)

dom = parse("./move.svg")
dom = dom.getElementsByTagName("svg")[0]


movement = None
damage = None
for layer in dom.getElementsByTagName("g"):
    type = layer.getAttribute("inkscape:label")
    if type == "Movement":
        points = getPoints(layer.getElementsByTagName("path")[0])
        timestamps  = getTimeStamps(layer.getElementsByTagName("text"))
        path = associate(points, timestamps)
        
        # differentiate
        movement = [ ((y[0][0] - x[0][0], y[0][1] - x[0][1]), y[1]) for x,y in zip(path, path[1:]) ]

        
    elif type == "Damage":
        hitboxes = []
        knockbacks = []
        for path in layer.getElementsByTagName("path"):
            spiral = path.getAttribute("sodipodi:type")
            if spiral:
                hitboxes.append(getHitbox(path))
            else:
                knockbacks.append(getPoints(path))
        
        # get the delta of each knockback vector
        knockbacks = [ ((x[0][0], x[0][1]), (x[1][0] - x[0][0], x[1][1] - x[0][1])) for x in knockbacks ]
        timestamps  = getTimeStamps(layer.getElementsByTagName("text"))

        hitKnocks = associate(hitboxes, knockbacks)
        hitTimes = associate(hitboxes, timestamps)
        
        damage = [ ((x[0][0], x[0][1]), (x[0][2], x[1], y[1])) for x,y in zip(hitKnocks, hitTimes) ]
        


print("# ---------------")
print("class ParsedAttack(Attack):")
print("    def start(self, instigator):")
print("        scene = investigator.scene")
print("        dir = Vec2d(investigator.direction, -1)")

lastTime = 0
for hitbox in damage:
    time, amount = [ float(x) for x in hitbox[1][2].split(":") ]
    deltaTime = time - lastTime
    print("        for i in range(%d):" % (deltaTime))
    print("            yield")
    tuple = (hitbox[0][0], hitbox[0][1], hitbox[1][0], amount, hitbox[1][1][0], hitbox[1][1][1])
    print("        scene.hitbox(instigator.position + Vec2d(%d, %d) * dir, %d, Damage(DamageType.NORMAL, %d, Vec2d(%d, %d) * dir * 10), instigator)" % tuple)
    lastTime = time
