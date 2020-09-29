# sparqly
SPARQL semantic translator and object-mapper for Python (wip).

## Example
We define a query object as an instance of `sparqly.Item`, with the predicates
listed as attributes following the idiom of `pretty_name = "actual name"`. For
example, to query Pre-Raphaelite aritsts on WikiData, the schema we define could
look like

```py
from sparqly import Item

class Artist(Item):
  movement      = "wdt:P135"
  instance_of   = "wdt:P31"
```

We can then generate the query text for a selection with
```py
from sparqly import query

q = query()
q.select(Artist).where(
  movement = "wd:Q184814", # pre-raphaelite
  instance_of = "wd:Q5"    # human
)

print(q.all())
```
Which will print to the console:
```
SELECT ?Artist WHERE {
	?Artist wdt:P135 wd:Q184814 ;
	wdt:P31 wd:Q5 .
}
```

## Changelog
Version 0.1.0:
- Object-Relational-Mapping (ORM)
- `SELECT`
- `WHERE`

## Planned Features
- Ability to attach service
- `CONSTRUCT`/`ASK`/`DESCRIBE`
- Filters like `ORDER`, `LIMIT`, `GROUP`
- More semantic support
- Additional methods for constructing queries depending on circumstance and complexity
