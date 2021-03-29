# BT4222 Project

BT4222 Mining Web Data for Business Insights - Effectiveness of Machine Learning and Text Mining Techniques in
Predicting Fed Rate Movement

## 00 Project Overview

### Introduction

Our project involves the application of relevant text mining and machine learning techniques to forecast the direction
of policy rates in the United States.

### Project Context

Policy rates is an important monetary policy tool that can be used to control economic activity in the country. For
instance, the Central Bank can increase the policy rates to battle inflation and prevent an overheating economy. On the
other hand, it can reduce policy rates to stimulate economic growth. Lower interest rates reduce the borrowing cost and
incentives investors to invest in the country, directing foreign capital into the country. Additionally, it reduces the
incentives for saving which bolsters domestic consumption.

In the U.S., policy rates are determined by the Federal Open Market Committee (FOMC). Each year, the FOMC meets eight
times to determine the near-term direction of monetary policy and interest rates. In particular, the Fed Fund Rate is
discussed, voted and determined during the meetings. Upon each meeting, FOMC publishes minutes, statements and
testimonials on its website, establishing their view on the current economic situation, and their forecast that result
in their monetary policy decision.

### Project Motivation

Many attributes result in the decision-making of the Fed Rates, but Natural Language Processing (NLP) has not been
utilized much in this area. We want to find out the effectiveness of FOMC textual data in helping to improve the
prediction of Fed Rate movement.

## 01 Data Collection

Run the following command to scrape data and write it to the respective folders

`python scripts/01_data.py`

### Macro Data

The market data was downloaded using the FRED API, which is a web service that facilitates the retrieval of economic
data from the Federal Reserve Economic Data (FRED) and Archival Federal Reserve Economic Data (ALFRED) websites hosted
by the Economic Research Division of the Federal Reserve Bank of St. Louis. Requests could be customized according to
the data source, release, series and other preferences.

### Textual Data

Since sentiment analysis is one of the NLP methods that we are looking to apply, our team looked for textual data that
would be valuable. The FOMC website updates 5 crucial materials after each meeting, namely the meeting statements,
meeting minutes, press conference transcripts, speeches and testimonies. To retrieve these textual data required for our
project, we developed python scripts to perform the web-scrape function. We made use of popular web-scraping libraries
like requests, Selenium to make HTTP requests. BeautifulSoup was subsequently used to parse the data so that the
relevant data may be extracted from the HTML content.

## 02 Preprocessing

`python scripts/02_preprocess.py`

## 03 Exploratory Data Analysis

## 04 Feature Engineering

## 05 Model Building
