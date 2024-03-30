### Python library to parse PNG Tavern v2 character cards.

```
pip3 install -r requirements.txt
```

Usage:
```
>>> import v2_card
>>> d = v2_card.parse('SillyTavern/public/characters/Alice.png')
>>> d.data.name # Example
'Alice'
```
