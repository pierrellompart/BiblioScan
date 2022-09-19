GatherLitterature.ipynb
=========

GatherLitterature.ipynb is an unofficial notebook allowing to fetch references and download their .pdf using an API for Sci-hub. GatherLitterature.ipynb can search for numerous papers on Google Scholars using as input a litterature equation. The script will recover the title, citations, authors and link to each paper before downloading their pdf from Sci-hub. The litterature equation has to following this format:

Dog/Cat/Bat AND Food/Drink/Cake/_ AND Blue/Dark Red/Yellow/_

From it, every keyword combinations will be generated. The AND separate each SECTION of the combination. The _ define that the SECTION can be disgarded in the combination. For instance:
  - Dog AND Food AND Blue
  - Cat AND Drink AND Dark Red
  - Bat AND Yellow
  - Cat

If you believe in open access to scientific papers, please donate to Sci-Hub.

Features
--------
* Fetch all reference linked to a litterature aquation
* Download specific articles via Sci-hub

**Note**: A known limitation of scihub.py is that captchas show up every now and then, blocking any searches or downloads.


**Download** 
To download the package, use can either download the .zip or use the following command.
```
git clone https://github.com/pierrellompart/BiblioScan.git
cd ./BiblioScan
```
Setup
----- 
Install the required modules
```
pip install -r requirements.txt
```
Open the notebook. You should have install Jupyter Notebook or Anaconda.
```
jupyter notebook
```
You should detain a version of chromedriver in accordance with the version of chrome you are using.
If it is not the cause an error will ocur at:
```
driver = webdriver.Chrome(executable_path='./chromedriver.exe') 
```
Stating what is your current version of Chrome. To solve it, go on the chromedriver website and replace the chromedriver executable located in this folder by one adapted to your Chrome version.
To download ChromeDriver: https://chromedriver.chromium.org/downloads

License
-------
MIT
