# Grammatical-Dictionary-of-Polish

The aim of the project is to create a grammatical dictionary of the Polish language based on the [marisa-trie](https://github.com/pytries/marisa-trie) structure.

## Installation
```shell script
pip install https://github.com/kaszubab/Grammatical-Dictionary-of-Polish
```
## Usage
 - Build new grammatical dictionary from given array of files:
```python
>>> dictionary = dict.Dictionary(["words.txt"])
```
The file must be in the following form:  
```regexp
<infinitive>:<flexographic label>:<derivatives separated with colon>  
where:
    <flexographic label> is a sequence of capital letters, 
                         optionally with an asterisk at the beginning

    <derivatives separeted with colon> are word forms arranged in a fixed order 
                                       depending on the part of speech that is 
                                       defined by the first letter of the label.
```
Example line in file:
```
pies :  *ABABAB:pies:psa:psu:psa:psem:psie:psie:psy:psów:psom:psy:psami:psach:psy:
```
 - Get derivatives of a word:
```python
>>> dictionary.get_children("pies")
```
 - Get an infinitive of a word:
```python
>>> dictionary.get_parent("psa")
```

## Authors
 - [Bartosz Kaszuba](github.com/kaszubab)  
 - [Konrad Dębiec](github.com/kdebiec)