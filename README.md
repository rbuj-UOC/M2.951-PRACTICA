# Obtencio de dades metrològiques

## Integrants del grup

- Nora Bolivar López
- Robert Buj Gelonch

## Estructura del repositori

- `src/main.py`: punt d'entrada al programa. Inicia el procés de scraping.
- `src/scraper.py`: conté la implementació de la classe MeteoScraper amb els mètodes que generen el conjunt de dades a partir de les dades recollides del llista d'estacions https://www.meteo.cat//observacions/llistat-xema.
- `requirements.txt`: fitxer ams els requisits

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
