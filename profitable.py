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
PROFIT_THRESHOLD= round(3*(20+15))
days_tour_count_list_date_key = [dict() for x in range(7)]
days_tour_count_list_doys_key = [dict() for x in range(7)] #day of year scaled
start_day_of_year= 365
end_day_of_year= 0
start_week_of_year= 52
graphed_year = None
tours_total = 0
tours_per_day_maximum = 0
revenue_total = 0

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
      tours_total += row_tour_count
      revenue_total += int(float(row['Gross Sales'].replace('$', '')))

      if date_w_year in days_tour_count_list_date_key[day_of_week]:
         days_tour_count_list_date_key[day_of_week][date_w_year] += row_tour_count
      else:
         days_tour_count_list_date_key[day_of_week][date_w_year] = row_tour_count

      # days_tour_count_list_doy_key[day_of_week][day_of_year] = days_tour_count_list_date_key[day_of_week][date_w_year]
   # else:
   #    print(f"Skipping row={row_number} with category={row['Category']}")

# make another list using scaled day of year for key instead of year-day-month
for day_of_week in range(4, 7):
   for date, tour_count in days_tour_count_list_date_key[day_of_week].items():
      tour_date = datetime.datetime.strptime(date, '%Y-%m-%d')
      week_of_year= tour_date.isocalendar().week
      day_of_week= tour_date.weekday()
      scaled_doy= ((week_of_year - start_week_of_year) * 4) + (day_of_week - 4) #the 4 multiplier leaves a gap between weeks
      days_tour_count_list_doys_key[day_of_week][scaled_doy] = tour_count
      if tour_count > tours_per_day_maximum:
         tours_per_day_maximum= tour_count

print_it = False
if print_it:
   print(f"processed {row_number} rows;  starting day of year = {start_day_of_year} starting week of year = {start_week_of_year}")
   day_label_list= ["Fri", "Sat", "Sun"]
   for day_of_week in range(4, 7):
      print(f"{day_label_list[day_of_week-4]}: {days_tour_count_list_date_key[day_of_week]}")
      # print(f"{day_label_list[day_of_week-4]}: {days_tour_count_list_doy_key[day_of_week]}")
      print(f"{day_label_list[day_of_week-4]} length={len(days_tour_count_list_date_key[day_of_week])}: {days_tour_count_list_doys_key[day_of_week]}")
 
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
   # import numpy as np
   import matplotlib.pyplot as plt
   import math

   background_color = 'black'
   font_color = 'white'
   
   width = 16
   height = 6
   fig = plt.figure(figsize = (width, height), facecolor=background_color) #size in inches
   ax = plt.axes()
   ax.set_facecolor(background_color) #plot background color
   ax.spines['bottom'].set_color(font_color)
   ax.tick_params(axis='x', colors=font_color)
   ax.spines['left'].set_color(font_color)
   ax.tick_params(axis='y', colors=font_color)

   revenue = revenue_total
   expense= int(round((end_day_of_year-start_day_of_year)*PROFIT_THRESHOLD, -2))

   # text(x, y, string, kwarg**) 
   ax.text((width/2), tours_per_day_maximum-3, f"Total Tours={tours_total}\nRevenue=${revenue}\nExpense=${expense} (Approximate)\n      Loss=${revenue-expense}", 
         bbox={'facecolor': font_color, 'alpha': 0.8, 'pad': 8})

   for day_of_week in range(4, 7):
      plt.bar(list(days_tour_count_list_doys_key[day_of_week].keys()), list(days_tour_count_list_doys_key[day_of_week].values()))
   
   plt.axhline(9,color='red') #horizontal profitability line

   # print(f"tours_per_day_maximum= {tours_per_day_maximum}")
   y_tick_spacing = 2
   plt.yticks(range(0,tours_per_day_maximum + y_tick_spacing, y_tick_spacing))

   weekend_count = math.ceil((end_day_of_year - start_day_of_year)/7)
   BARS_PER_WEEKEND = 4
   plt.xticks(range(1, weekend_count*BARS_PER_WEEKEND, BARS_PER_WEEKEND))
   labels = [item.get_text() for item in ax.get_xticklabels()]
   for index, value in enumerate(labels):
      labels[index] = datetime.datetime.strptime(graphed_year + "-" + str(start_day_of_year + 1 + (index*7)), "%Y-%j").strftime("%b%d")
   # print(f"labels={labels}")
   ax.set_xticklabels(labels)

   USE_XLABEL = False
   if USE_XLABEL:
      start_date = datetime.datetime.strptime(graphed_year + "-" + str(start_day_of_year), "%Y-%j").strftime("%B%d")
      end_date = datetime.datetime.strptime(graphed_year + "-" + str(end_day_of_year), "%Y-%j").strftime("%B%d")
      print(f"end_day_of_year={end_day_of_year} ({end_date}); start_day_of_year{start_day_of_year} ({start_date}); diff={end_day_of_year - start_day_of_year}")
      plt.xlabel(f"{start_date}  -through-  {end_date}", color=font_color)

   plt.ylabel("Tours", color=font_color)
   plt.title(f"Tours per day for {graphed_year}", color=font_color)
   plt.legend(['Profitability','Friday', 'Saturday', 'Sunday'])
   plt.show()
