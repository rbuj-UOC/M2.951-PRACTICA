# Obtenció de dades metrològiques

## Integrants del grup

- Nora Bolivar López
- Robert Buj Gelonch

## Estructura del repositori

- `.vscode/`: carpeta amb la configuració de Visual Studio Code.
  - `extensions.json`: llista d’extensions recomanades.
  - `settings.json`: preferències personalitzades de l’entorn de desenvolupament.
- `dataset/`: carpeta que conté els fitxers de dades.
  - `station_list.csv`: fitxer CSV amb la llista d’estacions meteorològiques.
  - `[CODI]_[DIA].csv`: fitxer CSV amb les mesures per a l'estació, identificada amb el codi de dos dígits [CODI], amb dades del dia [DIA] en format `dd.mm.yyyy`.
- `source/`: carpeta amb el codi font del projecte.
  - `main.py`: punt d’entrada del programa. Inicia el procés de web scraping.
  - `scraper.py`: implementa la classe `MeteoScraper`, que genera el conjunt de dades a partir de les [dades observades](https://www.meteo.cat/observacions/xema/dades) i les [estacions disponibles](https://www.meteo.cat//observacions/llistat-xema).
  - `simple_analysis.py`: primer anàlisi del conjunt de dades recollit.
- `.gitignore`: especifica els fitxers i directoris que Git ha d’ignorar en els commits.
- `LICENSE`: fitxer amb la llicència amb la que es publica el codi.
- `boost.sh`: script per executar el procés de scraping en paral·lel.
- `requirements.txt`: fitxer amb les dependències del projecte.

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
(.venv) $ python3 -m pip install -r requirements.txt
```

### Execució del codi

```sh
(.venv) $ python3 source/main.py
Scraping data...
Saving data to dataset.csv...
```

## DOI de Zenodo
