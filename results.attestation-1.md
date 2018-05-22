# Attestation #1 updates

## Huidige proces
1. NER
   - NER tagging van pagina's uit hetarchief.be (OCR-data)
2. Namenlijst
   - Opzoeken namen uit IFFM en opzoeken in NER-getaggede data.
     - Hierbij bekijken we "Voornaam Achternaam" en "Achternaam Voornaam", en alle combinaties van alternatieve voor- en achternamen. Er mogen tot 3 andere woorden tussen staan.
       --> aanpassen naar 1 woord tussen voor- en achternaam
     - er wordt "genormaliseerd" vergeleken zonder rekening te houden met eventuele OCR-fouten (bvb. "Jean5-Luc Hervé" wordt vergeleken als "jeanluc herve")
     - Zowel een complete voor- en achternaam moeten beschikbaar zijn, anders wordt deze persoon overgeslagen (alsook namen als <...>eau)
3. Attestation
   - Het manueel controleren van deze mogelijke links
     - Er is een tool gebouwd om deze relatief efficiënt te kunnen controleren en classifiëren
     - Eens er een aantal positieve matches zijn gevonden kunnen we een algorithme ontwikkelen dat de slaagkans tot match bepaald op basis van omliggende woorden (woon- en sterfplaats, leeftijd, verwanten), datum krant (sterfdatum), etc. (Indien genoeg positieve matches mogelijks zelfs via machine learning, dit lijkt momenteel echter overkill)
     - Na een eerste ronde blijkt hieruit reeds het volgende:
       - Voorlopig relatief wijzig matches:
```
victim_type  status   
CIVILIAN     Matches        5
             No match      14
             Uncertain      2
MILITARY     Matches       19
             No match     177
             Uncertain     30
```
       - Een aantal namen die heel veel voorkomen kunnen we sowieso gaan overslaan in de attestation stap omdat de match kans heel klein is, bvb. gekende namen als "Victor Hugo", "Richard Wagner", "George LLyod" en veel voorkomende namen als "Albert Thomas".
         - In een latere fase kunnen we die mogelijk toch nog matchen, maar manuele attestation is tijdverspilling.

## Volgende stappen
1. NER 
  - Er zullen een aantal andere NER taggers worden uitgestest
2. Namenlijst
  - En aantal mogelijke aanpassingen worden overwogen:
    - Fuzzy matching gebruiken om eventuele OCR-fouten te omzeilen
    - Score berekenen die de slaagkans tot match reflecteert
    - Iets minder tolerant maken bij matching (er mag maar 1 woord meer tussen de voor- en achternaam staan)
      - Mogelijk secties waar veel namen in staan, bvb. lijsten krijgsgevangenen nog strenger matchen (voor- en achternaam moeten naast elkaar staan, bepalen over wat voor lijst het gaat en automatisch bekijken in namenlijst of dit overeenstemt met levensloop)
3. Attestation
  - Hogere scores uit linken namenlijst prioriteit geven
  - Workflow nog iets optimaliseren om efficiënter te kunnen mogelijke matches confirmeren


## Counts
Total pages in het archief: 274924
Pages checked: ~100k (~36 %)
Total names in NML: 545301
Names skipped: 11726 MILITARY, 1073 CIVILIAN
Names checked: 509357 MILITARY, 23082 CIVILIAN, 2 "NONE"
Possible links found: ~700k
Amount of names with at least one link: ~90k (so an average of around 8 links per found name)

