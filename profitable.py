#!/usr/bin/env python3

'''
columns looked at in .csv file
Date, Category, Quantity
Date format: YYYY-MM-DD
'''

import sys
import os

import csv
import datetime

# export TK_SILENCE_DEPRECATION=1
from tkinter import Tk     # from tkinter import Tk for Python 3.x
from tkinter.filedialog import askopenfilename

Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
filename = askopenfilename() # show an "Open" dialog box and return the path to the selected file
# print(filename)

row_number = 0
PROFIT_THRESHOLD= round(3.25*(20+15))
days_tour_count_list_date_key = [dict() for x in range(7)]
# days_tour_count_list_doy_key = [dict() for x in range(7)] #by day of year
days_tour_count_list_doys_key = [dict() for x in range(7)] #day of year scaled
start_day_of_year= 365
end_day_of_year= 0
start_week_of_year= 52
graphed_year = None

csvReader = csv.DictReader(open(filename))
for row in csvReader:
   row_number += 1
   if row['Category'] == 'Tours':
      tour_date = datetime.datetime.strptime(row['Date'], '%Y-%m-%d') #tour_date includes HH:MM:SS
      date_w_year= tour_date.strftime('%Y-%m-%d')
      graphed_year= tour_date.strftime('%Y')
      # date_wo_year= tour_date.strftime('%m-%d')

      day_of_week= tour_date.weekday()
      week_of_year= tour_date.isocalendar().week
      if week_of_year < start_week_of_year:
         start_week_of_year= week_of_year
      day_of_year = tour_date.timetuple().tm_yday
      if day_of_year < start_day_of_year:
         start_day_of_year= day_of_year
         if day_of_week == 5:
            start_day_of_year -= 1
         if day_of_week == 6:
            start_day_of_year -= 2
      if day_of_year > end_day_of_year:
         end_day_of_year= day_of_year

      row_tour_count= round(float(row['Qty']))

      if date_w_year in days_tour_count_list_date_key[day_of_week]:
         days_tour_count_list_date_key[day_of_week][date_w_year] += row_tour_count
      else:
         days_tour_count_list_date_key[day_of_week][date_w_year] = row_tour_count

      # days_tour_count_list_doy_key[day_of_week][day_of_year] = days_tour_count_list_date_key[day_of_week][date_w_year]
   # else:
   #    print(f"Skipping row={row_number} with category={row['Category']}")

for day_of_week in range(4, 7):
   for date, tour_count in days_tour_count_list_date_key[day_of_week].items():
      tour_date = datetime.datetime.strptime(date, '%Y-%m-%d')
      week_of_year= tour_date.isocalendar().week
      day_of_week= tour_date.weekday()
      scaled_doy= ((week_of_year - start_week_of_year) * 4) + (day_of_week - 3) #the 4 multiplier leaves a gap between weeks; -3 make it 1 based
      days_tour_count_list_doys_key[day_of_week][scaled_doy] = tour_count

print_it = False
if print_it:
   print(f"processed {row_number} rows;  starting day of year = {start_day_of_year} starting week of year = {start_week_of_year}")
   day_label_list= ["Fri", "Sat", "Sun"]
   for day_of_week in range(4, 7):
      print(f"{day_label_list[day_of_week-4]}: {days_tour_count_list_date_key[day_of_week]}")
      # print(f"{day_label_list[day_of_week-4]}: {days_tour_count_list_doy_key[day_of_week]}")
      print(f"{day_label_list[day_of_week-4]}: {days_tour_count_list_doys_key[day_of_week]}")
 
analyze_it = False
if analyze_it:
   profitable_days_count= [0]*7
   for day_of_week in range(4, 7):
      for date, tour_count in days_tour_count_list_date_key[day_of_week].items():
         if (tour_count * 10) > PROFIT_THRESHOLD:
            profitable_days_count[day_of_week] += 1
            
      print(f"day={day_of_week} "
            f"tours={sum(days_tour_count_list_date_key[day_of_week].values())} "
            f"days={len(days_tour_count_list_date_key[day_of_week])} "
            f"profitable_days={profitable_days_count[day_of_week]}")

plot_it = True
if plot_it:
   start_date = datetime.datetime.strptime(graphed_year + "-" + str(start_day_of_year), "%Y-%j").strftime("%B %d")
   end_date = datetime.datetime.strptime(graphed_year + "-" + str(end_day_of_year), "%Y-%j").strftime("%B %d")

   # import numpy as np
   import matplotlib.pyplot as plt
   
   fig = plt.figure(figsize = (16, 6)) #size in inches
   for day_of_week in range(4, 7):
      plt.bar(list(days_tour_count_list_doys_key[day_of_week].keys()), list(days_tour_count_list_doys_key[day_of_week].values()))
   
   plt.yticks(range(0,24))
   plt.axhline(10,color='red') #horizontal profitability line
   plt.xlabel(f"{start_date}  -through-  {end_date}")
   plt.ylabel("Tours")
   plt.title(f"Tours per day for {graphed_year}")
   plt.show()
