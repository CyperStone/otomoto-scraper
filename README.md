![scraper_logo](https://github.com/CyperStone/otomoto-scraper/assets/67295703/f5a644b5-9412-4cf7-9e05-ad65589b963f)

## Web scraper of car offers from Polish marketplace Otomoto.pl

### Getting Started
1. Clone the repository to your local machine and navigate to the project directory:
```
git clone https://github.com/CyperStone/otomoto-scraper.git
```
2. Create and activate new environment with Python 3.10 (example with using Anaconda):
```
conda create -n myenv python=3.10
conda activate myenv
```
3. Install required packages:
```
conda install pip
pip install -r requirements.txt
```

### Usage
1. To scrape all offers available on the website simply use the following command:
```
python scrape_all_offers.py [OPTIONS]
```
2. Available options:
```
  --results_dir [RESULTS_DIR]   Path to directory where results have to be saved
  --to_eng, --no-to_eng         Whether to translate results to english (default: False)
```
3. In case of being temporarily blocked by the server, try to change the number of used threads and/or the times between sending requests in `config.py`

### Dataset
The dataset gathered using this scraper can be accessed [HERE](https://www.kaggle.com/datasets/szymoncyperski/car-sales-offers-from-otomotopl-2023).
