# Obtenció de dades metrològiques

## Integrants del grup

- Nora Bolivar López
- Robert Buj Gelonch

## Estructura del repositori

- `dataset/`: carpeta amb els fitxers de dades.
   - `station_list.csv`: fitxer csv amb la llista de les estacions.
- `src/`: carpeta amb els fitxers de codi font.
  - `main.py`: punt d'entrada al programa. Inicia el procés de scraping.
  - `scraper.py`: conté la implementació de la classe MeteoScraper amb els mètodes que generen el conjunt de dades a partir de les [dades](https://www.meteo.cat/observacions/xema/dades) recollides de les [estacions](https://www.meteo.cat//observacions/llistat-xema).
- `requirements.txt`: fitxer ams els requisits.

## Utilització del codi

### Creació d'un entorn virtual amb venv

```sh
python3 -m venv .venv
```

### Activació de l'entorn virtual

```sh
source .venv/bin/activate
```

### Instal·lació dels requisits

```sh
python -m pip install -r requirements.txt
```

### Execució del codi

```sh
(.venv) $ python3 src/main.py
Scraping data...
Saving data to dataset.csv...
```

## DOI de Zenodo
