# -*- coding: utf-8 -*-

"""
Reference Scrapper
[Search|Download] research papers from [scholar.google.com|sci-hub.io].

@author pierrellompart 
"""

import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import pandas as pd
import os
import itertools
import scidownl
from tqdm import tqdm
import math
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
import pigeonXT as pixt
from ipywidgets import *
from IPython.display import display

plt.rcParams['figure.figsize'] = (10.0, 10.0)
plt.style.use('seaborn-dark-palette')
plt.rcParams['axes.grid'] = True
plt.rcParams["patch.force_edgecolor"] = True
sns.set_style("ticks")

class BiblioScan(object):
	def PrepareCombinations(researchRule, pageLimit, Waiting_time, Theme):
		IterationDid = {}
		titleCol = []
		linkCol = []
		citationCol = []
		authorCol = []
		
		researchRuleList = researchRule.split("AND")
		researchRuleList_Deep = [researchRule_One.split("/") for researchRule_One in researchRuleList]
		researchRuleList_Combinaison = list(itertools.product(*researchRuleList_Deep))
		reserveRuleList = []
		for itemEntry in tqdm(researchRuleList_Combinaison):
			tempListe = []
			for value in list(itemEntry):
				if "_" not in value:
					tempListe.append(value.strip())
			reserveRuleList.append(tempListe)
		listResearch = ["+".join("+AND+".join(iterElement).split()) for iterElement in reserveRuleList]
		print("Number of combinations:", len(listResearch))
		print("Number of page to iterate:", len(listResearch) * pageLimit)
		print("Estimated time: Around", (len(listResearch) * pageLimit* (Waiting_time+1))/60, "minutes")
		return(listResearch)
	
	def DownloadData(DataSaveFilter, Theme):
		TitleFilter = list(DataSaveFilter["Title"])
		Title_Download = []
		Failed_Download = []
		i = 0
		for title in tqdm(TitleFilter):
			print(i+1, "/", len(TitleFilter))
			DataSaveFilterSel = DataSaveFilter[DataSaveFilter["Title"] == title]
			ref = list(DataSaveFilterSel["Reference"])[0]
			os.system("scidownl download --doi {} --out ./{}/{}.pdf".format(ref, Theme, "_".join(title.strip().split())))
			Title_Download.append("_".join(title.split()))
			if "_".join(title.split()) + ".pdf" in os.listdir("./{}".format(Theme)):
				Failed_Download.append("Downloaded")
			else:
				Failed_Download.append("Fail")
			i+=1
		Data_Export = pd.DataFrame()
		Data_Export["Title"] = Title_Download
		Data_Export["Download"] = Failed_Download
		Data_Export.to_csv("./{}/Download.csv".format(Theme),sep = ";",
					   index = False,
					   columns = list(Data_Export.columns))

		
		fig = px.scatter(Data_Export, x="LogCitation", y="Count", color="Download",
		                 hover_name="Title", hover_data=["Reference", "Citation"],
                     template='simple_white',
                 width=800, height=800)
		fig.show()
		return(Data_Export)


	def FilterCitation(DataSave, ForbidenWord, Threshold, ThresholdCount, Theme):
		KeepList = []
		DataSaveFilter = DataSave.copy()
		countListe = list(DataSaveFilter["Count"])
		citationListe = list(DataSaveFilter["Citation"])
		i =0
		for title in tqdm(list(DataSaveFilter["Title"])):
			Keep = "no"
			for word in ForbidenWord:
				if word in title:
					Keep = "no"
				else:
					if countListe[i] < ThresholdCount:
						if citationListe[i] > Threshold:
							Keep = "yes"
						else:
							Keep = "no"
					else:
						Keep = "yes"
			i+=1
			KeepList.append(Keep)   
		DataSaveFilter["Keep"] = KeepList
		DataSaveFilter["LogCitation"] = [math.log10(i) if i > 0 else 0 for i in list(DataSaveFilter["Citation"])]
		
		##################################################################################
		
		DataSaveFilter.to_csv("./{}/BibliographyAndDownload_NoFilter.csv".format(Theme),
					   index = False,sep = "\t",
					   columns = list(DataSaveFilter.columns))
		fig = px.scatter(DataSaveFilter, x="LogCitation", y="Count", color = "Keep",
						 hover_name="Title", hover_data=["Reference", "Citation"],
                     template='simple_white',
                 width=800, height=800)
		fig.update_layout( legend=dict(title= None), hoverlabel=dict(bgcolor='rgba(255,255,255,0.75)', font=dict(color='black')))
		fig.show()
		return(DataSaveFilter)


	def EnumerateReferences(driver, listResearch, Waiting_time, Theme, pageLimit):
		IterationDid = {}
		o=0
		for textResearch in tqdm(listResearch):
			print(o+1, "/", len(listResearch))
			o+=1
			start = 0
			Error = False
			
			while Error == False:
		
				if start >= pageLimit:
					break
				
				if start == 0:
					
					link = 'https://scholar.google.com/scholar?hl=fr&as_sdt=8%2C5&q={}&btnG='.format(textResearch)
					driver.get(link)
					time.sleep(6)
		
					try:
			
						Element_list = driver.find_elements(By.CLASS_NAME, "gs_ri")
						if len(Element_list) <= 1:
							Error == True
							break
						for element in Element_list:
		
							Title = element.find_element(By.CLASS_NAME, "gs_rt")
							TitleText = Title.text
							TitleHref = Title.find_elements(By.XPATH, ".//descendant::a[@href]")
							LINKs = []
							for i in TitleHref:
								LINK = i.get_attribute('href')
								LINKs.append(LINK)
							ReferenceDOI = LINKs[0]
							# fetch href from titleand thus DOI
							Authors = element.find_element(By.CLASS_NAME, "gs_a")
							AuthorsText = Authors.text
							Citation = element.find_element(By.CLASS_NAME, "gs_fl")
							CitationText = Citation.text
							
							TitleSave = TitleText
							AuthorsSave = ", ".join(AuthorsText.split("-")[0].split(","))
							ReferenceSave = ReferenceDOI
							if "Cité" in CitationText:
								CitationSave = int(CitationText.split("Cité")[1].split()[0])
							else:
								CitationSave = 0
							InfoSave = [TitleSave, AuthorsSave, ReferenceSave, CitationSave]
							ID_Ref = "+".join([TitleSave, AuthorsSave])
							if ID_Ref not in IterationDid:
								IterationDid[ID_Ref] = {}
								IterationDid[ID_Ref]["Title"] = TitleSave
								IterationDid[ID_Ref]["Reference"] = ReferenceSave
								IterationDid[ID_Ref]["Citation"] = CitationSave
								IterationDid[ID_Ref]["Authors"] = AuthorsSave
								IterationDid[ID_Ref]["Count"] = 0
		
							else:
								IterationDid[ID_Ref]["Count"] += 1
					except:
						Error == True
						
							
				else:
					link = 'https://scholar.google.com/scholar?start={}0&q={}&btnG='.format(start, textResearch)
					driver.get(link)
					time.sleep(6)
					try:
						Element_list = driver.find_elements(By.CLASS_NAME, "gs_ri")
						if len(Element_list) <= 1:
							Error == True
							break
						for element in Element_list:
							Title = element.find_element(By.CLASS_NAME, "gs_rt")
							TitleText = Title.text
							TitleHref = Title.find_elements(By.XPATH, ".//descendant::a[@href]")
							LINKs = []
							for i in TitleHref:
								LINK = i.get_attribute('href')
								LINKs.append(LINK)
							ReferenceDOI = LINKs[0]
							# fetch href from titleand thus DOI
							Authors = element.find_element(By.CLASS_NAME, "gs_a")
							AuthorsText = Authors.text
							Citation = element.find_element(By.CLASS_NAME, "gs_fl")
							CitationText = Citation.text
							
							TitleSave = TitleText
							AuthorsSave = ", ".join(AuthorsText.split("-")[0].split(","))
							ReferenceSave = ReferenceDOI
							if "Cité" in CitationText:
								CitationSave = int(CitationText.split("Cité")[1].split()[0])
							else:
								CitationSave = 0
							InfoSave = [TitleSave, AuthorsSave, ReferenceSave, CitationSave]
							ID_Ref = "+".join([TitleSave, AuthorsSave])
							if ID_Ref not in IterationDid:
								IterationDid[ID_Ref] = {}
								IterationDid[ID_Ref]["Title"] = TitleSave
								IterationDid[ID_Ref]["Reference"] = ReferenceSave
								IterationDid[ID_Ref]["Citation"] = CitationSave
								IterationDid[ID_Ref]["Authors"] = AuthorsSave
								IterationDid[ID_Ref]["Count"] = 0
		
							else:
								IterationDid[ID_Ref]["Count"] += 1
					except:
						Error == True
				start += 1

		DataSave = pd.DataFrame.from_dict(IterationDid).T.sort_values(['Count', 'Citation'], ascending = [False, False]).reset_index()[["Title", "Reference", "Citation", "Authors", "Count"]]
		return(DataSave)


	def AnnotateData(DataSaveFilter, Theme):
		DataSaveFilterTitle = DataSaveFilter[DataSaveFilter["Keep"]=="yes"]
		to_iterate = []
		for i , titre in enumerate(list(DataSaveFilterTitle.Title)):
			to_iterate

		annotations = pixt.annotate(
		        list(DataSaveFilterTitle.Title), 
		        options=['yes', 'no'], 
		        buttons_in_a_row=2,
		        reset_buttons_after_click=True,
		        include_next=True,
		        include_back=True,
		    ) 
		return(annotations)


	def PlotAnnotate(annotations, DataSaveFilterTitle, Theme):
		annotations["Title"] = annotations.example
		DataSaveFilterTitle_All = DataSaveFilterTitle.merge(annotations, on = "Title")
		DataSaveFilterTitle_All_Remaining = DataSaveFilterTitle_All[DataSaveFilterTitle_All["label"] == "yes"]
		DataSaveFilterTitle_All_Remaining.to_csv("./Bibliography_Annotated.csv".format(Theme),
		               index = False,sep = "\t",
		               columns = list(DataSaveFilterTitle_All_Remaining.columns))
		fig = px.scatter(DataSaveFilterTitle_All, x="LogCitation", y="Count", color = "label",
		                 hover_name="Title", hover_data=["Reference", "Citation"],
                     template='simple_white',
                 width=800, height=800)
		fig.update_layout( legend=dict(title= None), hoverlabel=dict(bgcolor='rgba(255,255,255,0.75)', font=dict(color='black')))
		fig.show()
		return(DataSaveFilterTitle_All_Remaining, DataSaveFilterTitle_All, DataSaveFilterTitle_All)

if __name__ == '__main__':
	main()
