from sparqly import Item, query

class Artist(Item):
    movement      = "wdt:P135"
    instance_of   = "wdt:P31"

q = query()
q.select(Artist).where(
    movement = "wd:Q184814", # pre-raphaelite
    instance_of = "wd:Q5"    # human
)

print(q.all())
