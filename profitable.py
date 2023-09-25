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
days_tour_count_list = [dict() for x in range(7)]

csvReader = csv.DictReader(open(filename))
for row in csvReader:
   row_number += 1
   if row['Category'] == 'Tours':
      day_of_week= datetime.datetime.strptime(row['Date'], '%Y-%m-%d').weekday()
      date_wo_year= datetime.datetime.strptime(row['Date'], '%Y-%m-%d').strftime('%m-%d')
      row_tour_count= round(float(row['Qty']))
      if date_wo_year in days_tour_count_list[day_of_week]:
         days_tour_count_list[day_of_week][date_wo_year] += row_tour_count
      else:
         days_tour_count_list[day_of_week][date_wo_year] = row_tour_count
   # else:
   #    print(f"Skipping row={row_number} with category={row['Category']}")

if True:
   print(f"processed {row_number} rows")
   print(f"Fri: {days_tour_count_list[4]}")
   print(f"Sat: {days_tour_count_list[5]}")
   print(f"Sun: {days_tour_count_list[6]}")

profitable_days_count= [0]*7
for day_of_week in range(4, 7):
   for date, tour_count in days_tour_count_list[day_of_week].items():
      if (tour_count * 10) > PROFIT_THRESHOLD:
         profitable_days_count[day_of_week] += 1
         
   print(f"day={day_of_week} "
          f"tours={sum(days_tour_count_list[day_of_week].values())} "
          f"days={len(days_tour_count_list[day_of_week])} "
          f"profitable_days={profitable_days_count[day_of_week]}")
   
# import numpy as np
import matplotlib.pyplot as plt
  
fig = plt.figure(figsize = (10, 5)) #size in inches
for day_of_week in range(4, 7):
   plt.bar(list(days_tour_count_list[day_of_week].keys()), list(days_tour_count_list[day_of_week].values()), width = 0.4)

# days = list(days_tour_count_list[4].keys())
# tours = list(days_tour_count_list[4].values())
# plt.bar(days, tours, color ='maroon', width = 0.4)
 
plt.xlabel("Days")
plt.ylabel("Tours")
plt.title("Tours per day")
plt.show()
