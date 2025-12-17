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
  - `[CODI]_[DIA].csv`: fitxer CSV amb les mesures per a l'estació, identificada
  amb el codi de dos dígits [CODI], amb dades del dia [DIA] en format `dd.mm.yyyy`.
- `source/`: carpeta amb el codi font del projecte.
  - `main.py`: punt d’entrada del programa. Inicia el procés de web scraping.
  - `scraper.py`: implementa la classe `MeteoScraper`, que genera el conjunt de
  dades a partir de les [dades observades](https://www.meteo.cat/observacions/xema/dades)
  i les [estacions disponibles](https://www.meteo.cat//observacions/llistat-xema).
  - `simple_analysis.py`: primer anàlisi del conjunt de dades recollit.
- `.gitignore`: especifica els fitxers i directoris que Git ha d’ignorar en els
commits.
- `.editorconfig`: fitxer de configuració per a editors de text compatibles
amb EditorConfig com ara Visual Studio Code.
- `LICENSE`: fitxer amb la llicència amb la que es publica el codi.
- `README.md`: fitxer amb la documentació general del projecte.
- `boost.sh`: script per executar el procés de scraping en paral·lel.
- `compress.sh`: script per comprimir el directori de treball, el dataset o els registres.
- `dataset.tar.xz`: arxiu del dataset sense cap preprocessament, que s'ha
obtingut amb l'execució de l'script `boost.sh`. Veure fitxer logs.tar.zst.
- `environment.yml`: fitxer per crear un entorn virtual amb conda i instal·lar
les dependències.
- `init.sh`: script per preparar l'entorn virtual amb venv i instal·lar les
dependències.
- `logs.tar.zst`: arxiu amb registres de l'execució de l'scrapper amb l'script
`boost.sh`.
- `requirements.txt`: fitxer amb les dependències del projecte.

## Requisits

- Python 3.9 o superior
- bash shell >= 4.3 (`wait -n` en l'script boost.sh)
- Biblioteques de Python:
  - pandas: per al processament de dades
  - selenium: per al web scraping
- Altres biblioteques de Python, incloses a la biblioteca estàndard:
  - argparse: per al processament d'arguments de línia d'ordres
  - datetime: per al maneig de dates i hores
  - os: per a la interacció amb el sistema operatiu
  - re: per a l'ús d'expressions regulars
  - time: per a funcions relacionades amb el temps
- Visual Studio Code: [baixar](https://code.visualstudio.com/) (opcional)
  - `shfmt` és necessari per donar format als scripts, en entorns macos es pot
  instal·lar amb l'ordre: [baixar](https://github.com/mvdan/sh/releases) (opcional)

```sh
brew install shfmt
```

## Utilització del codi

L'avantatge d'utilitzar un entorn virtual és que permet aïllar les
dependències del projecte de les del sistema operatiu, evitant conflictes
entre diferents projectes i versions de biblioteques.

Per utilitzar el codi, primer cal preparar l'entorn virtual i instal·lar les
dependències. Es pot utilitzar venv o conda per crear l'entorn virtual.

Un cop creat i activat l'entorn virtual, ja es pot executar el codi.

> [!TIP]
> Podeu utilitzar l'script `init.sh` per automatitzar la creació de l'entorn
> virtual amb venv i la instal·lació de les dependències.

> [!NOTE]
> Podeu utilitzar l'extensió de Visual Studio Code
> [Python](https://marketplace.visualstudio.com/items?itemName=ms-python.python)
> per gestionar entorns virtuals i executar codi Python dins de l'editor.
> Per crear un entorn virtual amb venv o conda, accediu a la paleta d'ordres
> (`Ctrl+Shift+P` o `Cmd+Shift+P` a macOS) i escriviu "Python: Create Environment".

> [!IMPORTANT]
> Si voleu canviar l'intèrpret de Python utilitzat per Visual Studio Code,
> podeu fer-ho des de la paleta d'ordres (`Ctrl+Shift+P` o `Cmd+Shift+P` a macOS)
> escrivint "Python: Select Interpreter" i seleccionant l'intèrpret de l'entorn
> virtual que heu creat. Cal tenir en compte que l'intèrpret se seleccionarà
> automàticament amb l'entorn virtual quant aquest s'hagi creat amb l'extensió
> comentada en la nota anterior.

### Entorn virtual amb venv

#### Creació de l'entorn virtual amb venv

Per crear un entorn virtual amb venv, executeu la següent ordre al directori
arrel del projecte:

```sh
python3 -m venv .venv
```

Per tal d'assegurar que l'entorn virtual s'ha creat correctament, podeu
comprovar que el directori `.venv/` s'ha creat al directori arrel del projecte.

> [!TIP]
> En macos, python ja inclou venv per defecte. En altres sistemes operatius,
> pot ser necessari instal·lar el paquet `python3-venv`. Per exemple, en sistemes
> basats en Debian/Ubuntu, podeu instal·lar-lo amb l'ordre següent:

```sh
sudo apt-get install python3-venv
```

#### Activació i desactivació de l'entorn virtual amb venv

Per activar l'entorn virtual, executeu la següent ordre:

```sh
source .venv/bin/activate
```

Per a desactivar l'entorn virtual, executeu la següent ordre:

```sh
deactivate
```

#### Instal·lació i actualització de dependències amb venv

Per a instal·lar les biblioteques de Python es pot utilitzar el fitxer
`requirements.txt` amb l'ordre:

```sh
python3 -m pip install -r requirements.txt
```

Si no voleu utilitzar el fitxer `requirements.txt`, podeu instal·lar les
biblioteques necessàries amb la següent ordre després d'activar l'entorn virtual:

```sh
python3 -m pip install pandas selenium --upgrade pip
```

Un cop instal·lades les dependències, es poden actualitzar amb l'ordre:

```sh
python3 -m pip install --upgrade pandas selenium
```

> [!IMPORTANT]
> Assegureu-vos d'estar dins de l'entorn virtual abans d'instal·lar o
> actualitzar les dependències.

### Entorn virtual amb conda

#### Creació de l'entorn virtual amb conda

Per crear un entorn virtual amb conda, executeu la següent ordre al directori
arrel del projecte:

```sh
conda env create --prefix=./.conda --file=environment.yml python=3.11
```

Per tal d'assegurar que l'entorn virtual s'ha creat correctament, podeu
comprovar que el directori `.conda/` s'ha creat al directori arrel del projecte.

> [!NOTE]
> Si no voleu utilitzar el fitxer `environment.yml`, podeu crear l'entorn virtual
amb les següents ordres:

```sh
conda create --prefix=./.conda python=3.11
conda activate ./.conda
conda install pip pandas selenium r-base=4.5.2 r-corrplot r-ggplot2 r-dplyr \
    r-kableextra r-knitr r-readr r-rmarkdown r-tidyverse
```

> [!TIP]
> Miniconda requereix menys espai i és més lleuger que Anaconda. Per a
> instal·lar Miniconda en sistemes macOS, podeu utilitzar Homebrew:

```sh
brew install --cask miniconda
conda init
conda config --set auto_activate_base False
source ~/.bash_profile
conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main
conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r
```

#### Activació i desactivació de l'entorn virtual amb conda

Per activar l'entorn virtual, executeu la següent ordre:

```sh
conda activate ./.conda
```

Per a desactivar l'entorn virtual, executeu la següent ordre:

```sh
conda deactivate
```

> [!TIP]
> Per canviar el prompt de l'entorn virtual i que mostri el nom de l'entorn,
> un cop activat, podeu executar la següent ordre per escurçar-lo:

```sh
conda config --set env_prompt '({name}) '
```

#### Actualització de dependències amb conda

Un cop instal·lades les dependències, es poden actualitzar amb l'ordre:

```sh
conda update pandas selenium
```

> [!IMPORTANT]
> Assegureu-vos d'estar dins de l'entorn virtual abans d'actualitzar les
> dependències.

### Execució del codi

Per baixar les dades de les estacions de l'ultim any fins al 3 de desembre de
2025:

```sh
python3 source/main.py -d 365 -b 03.12.2025 -m
python3 source/main.py -w
```

En cas que no es vulguin baixar les dades i es desitgi utilitzar el dataset
comprimit:

```sh
tar xvfa dataset.tar.xz
python3 source/main.py -w
```

Per consultar els arguments opcionals de l'aplicació:

```sh
$ python3 source/main.py -h
usage: main.py [-h] [-b BEGIN_DATE] [-d DAYS] [-w] [-m] [-o OUTPUT]

Meteo.cat scraper

optional arguments:
  -h, --help            show this help message and exit
  -b BEGIN_DATE, --begin-date BEGIN_DATE
                        The start date for data scraping (format: DD.MM.YYYY)
  -d DAYS, --days DAYS  Number of days to scrape
  -w, --skip-download   Skip the downloading of data files
  -m, --skip-merge      Do not merge the data files into a single CSV
  -o OUTPUT, --output OUTPUT
                        Output CSV file
```

## DOI de Zenodo

Bolivar, N. i Buj, R. (2025) «Dades recollides per la xarxa d'estacions meteorològiques automàtiques del servei meteorològic de Catalunya de l'últim any». Zenodo. doi:[10.5281/zenodo.17505763](https://doi.org/10.5281/zenodo.17505763)
