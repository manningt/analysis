#!/usr/bin/env python3

'''
columns looked at in .csv file
Date, Category, Quantity
Date format: YYYY-MM-DD
'''

import sys
#import os

import csv
import datetime

import argparse
from tkinter import Tk
from tkinter.filedialog import askopenfilename

class Parsed_results:
   def __init__(self):
      # profit_thold calc: per day; 2 days at $21, 1 day at $18 in 2024; the 1.3 multiplier is for taxes
      self.PROFIT_THRESHOLD= round(3.5*(20+16)*1.3)
      self.row_number = 0
      self.days_tour_count_list_date_key = [dict() for x in range(7)]
      self.days_tour_count_list_doys_key = [dict() for x in range(7)] #day of year scaled
      self.START= 0
      self.END= 1
      self.day_of_year= [365,0] #START, END
      self.week_of_year= [52,0] #START, END
      self.graphed_year = None
      self.tours_total = 0
      self.tours_wo_groups = 0
      self.tours_per_day_maximum = 0
      self.revenue_total = 0
      self.paid_weeks= 0
      self.expense= 0


   def parse_csv(self, filename):
      csvReader = csv.DictReader(open(filename))
      for row in csvReader:
         self.row_number += 1
         if row['Category'] == 'Tours':
            row_tour_count= round(float(row['Qty']))
            self.tours_total += row_tour_count
            if row_tour_count < 11: # skip group tours
               tour_date = datetime.datetime.strptime(row['Date'], '%Y-%m-%d') #tour_date includes HH:MM:SS
               date_w_year= tour_date.strftime('%Y-%m-%d')
               self.graphed_year= tour_date.strftime('%Y')
               # date_wo_year= tour_date.strftime('%m-%d')

               day_of_week= tour_date.weekday()
               week_of_year= tour_date.isocalendar().week
               day_of_year = tour_date.timetuple().tm_yday

               if week_of_year < self.week_of_year[self.START]:
                  self.week_of_year[self.START]= week_of_year
               if week_of_year > self.week_of_year[self.END]:
                  self.week_of_year[self.END]= week_of_year

               if day_of_year < self.day_of_year[self.START]:
                  self.day_of_year[self.START]= day_of_year
                  # adjust start_day if there were no sales on Friday or Saturday
                  if day_of_week == 5:
                     self.day_of_year[self.START] -= 1
                  if day_of_week == 6:
                     self.day_of_year[self.START] -= 2
               if day_of_year > self.day_of_year[self.END]:
                  self.day_of_year[self.END]= day_of_year

               self.tours_wo_groups += row_tour_count
               self.revenue_total += int(float(row['Gross Sales'].replace('$', '')))

               if date_w_year in self.days_tour_count_list_date_key[day_of_week]:
                  self.days_tour_count_list_date_key[day_of_week][date_w_year] += row_tour_count
               else:
                  self.days_tour_count_list_date_key[day_of_week][date_w_year] = row_tour_count

               # days_tour_count_list_doy_key[day_of_week][day_of_year] = days_tour_count_list_date_key[day_of_week][date_w_year]
         # else:
         #    print(f"Skipping row={row_number} with category={row['Category']}")

      # make another list using scaled day of year for key instead of year-day-month
      printed_once = True
      for day_of_week in range(4, 7):
         for date, tour_count in self.days_tour_count_list_date_key[day_of_week].items():
            tour_date = datetime.datetime.strptime(date, '%Y-%m-%d')
            week_of_year= tour_date.isocalendar().week
            day_of_week= tour_date.weekday()
            scaled_doy= ((week_of_year - self.week_of_year[self.START]) * 4) + (day_of_week - 4) #the 4 multiplier leaves a gap between weeks
            self.days_tour_count_list_doys_key[day_of_week][scaled_doy] = tour_count
            if tour_count > self.tours_per_day_maximum:
               self.tours_per_day_maximum= tour_count
            if not printed_once:
               print(f"{self.week_of_year[self.START]= } {tour_date= } {week_of_year= } {day_of_week= } {scaled_doy= } ")
               printed_once= True

      self.paid_weeks= (self.week_of_year[self.END]-self.week_of_year[self.START]) + 1 # undetermined why off by 1
      self.expense= self.paid_weeks*self.PROFIT_THRESHOLD*3


   def print_parse_info(self):
      print(f"processed {self.row_number} rows;  starting day of year = {self.day_of_year[self.START]} starting week of year = {self.week_of_year[self.START]}")
      day_label_list= ["Fri", "Sat", "Sun"]
      for day_of_week in range(4, 7):
         print(f"{day_label_list[day_of_week-4]}")
         print(f"\t{day_label_list[day_of_week-4]}: {self.days_tour_count_list_date_key[day_of_week]}")
         # print(f"{day_label_list[day_of_week-4]}: {days_tour_count_list_doy_key[day_of_week]}")
         print(f"\t{day_label_list[day_of_week-4]} length={len(self.days_tour_count_list_date_key[day_of_week])}: {self.days_tour_count_list_doys_key[day_of_week]}")


   def print_analysis_info(self):
      profitable_days_count= [0]*7
      for day_of_week in range(4, 7):
         for date, tour_count in self.days_tour_count_list_date_key[day_of_week].items():
            if (tour_count * 10) > self.PROFIT_THRESHOLD:
               profitable_days_count[day_of_week] += 1
               
         print(f"day={day_of_week} "
               f"tours={sum(self.days_tour_count_list_date_key[day_of_week].values())} "
               f"days={len(self.days_tour_count_list_date_key[day_of_week])} "
               f"profitable_days={profitable_days_count[day_of_week]}")
      print(f"{self.PROFIT_THRESHOLD=} {self.tours_per_day_maximum=} {self.paid_weeks=} {self.expense=} \
{self.tours_total=} {self.tours_wo_groups=}")


   def plot_it(self):
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

      loss= self.revenue_total - self.expense
      # text(x, y, string, kwarg**) 
      ax.text((width/2), self.tours_per_day_maximum-3, 
               f"Total Tours (not including groups)={self.tours_wo_groups}\nRevenue=${self.revenue_total}\nExpense=${self.expense} (Approximate)\n      Loss=${loss}", 
               bbox={'facecolor': font_color, 'alpha': 0.8, 'pad': 8})

      for day_of_week in range(4, 7):
         plt.bar(list(self.days_tour_count_list_doys_key[day_of_week].keys()), list(self.days_tour_count_list_doys_key[day_of_week].values()))
      
      plt.axhline(9,color='red') #horizontal profitability line

      y_tick_spacing = 2
      plt.yticks(range(0,self.tours_per_day_maximum + y_tick_spacing, y_tick_spacing))

      weekend_count = math.ceil((self.day_of_year[self.END] - self.day_of_year[self.START])/7)
      BARS_PER_WEEKEND = 4
      plt.xticks(range(1, weekend_count*BARS_PER_WEEKEND, BARS_PER_WEEKEND))
      labels = [item.get_text() for item in ax.get_xticklabels()]
      for index, value in enumerate(labels):
         labels[index] = datetime.datetime.strptime(self.graphed_year + "-" + str(self.day_of_year[self.START] + 1 + (index*7)), "%Y-%j").strftime("%b%d")
      # print(f"labels={labels}")
      ax.set_xticklabels(labels)

      USE_XLABEL = False
      if USE_XLABEL:
         start_date = datetime.datetime.strptime(self.graphed_year + "-" + str(self.day_of_year[self.START]), "%Y-%j").strftime("%B%d")
         end_date = datetime.datetime.strptime(self.graphed_year + "-" + str(self.day_of_year[self.END]), "%Y-%j").strftime("%B%d")
         print(f"end_day_of_year={self.day_of_year[self.END]} ({end_date}); \
               start_day_of_year{self.day_of_year[self.START]} ({start_date}); \
               diff={self.day_of_year[self.END] - self.day_of_year[self.START]}")
         plt.xlabel(f"{start_date}  -through-  {end_date}", color=font_color)

      plt.ylabel("Tours", color=font_color)
      plt.title(f"Tours per day for {self.graphed_year}", color=font_color)
      plt.legend(['Profitability','Friday', 'Saturday', 'Sunday'])
      plt.show()

def pick_file():
   from tkinter import Tk
   from tkinter.filedialog import askopenfilename

   # root = Tk.Tk()
   Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
   file_path = askopenfilename(title="Select an items...csv File")
    
   if file_path:
      filename = file_path.split('/')[-1]  # For Unix/Linux
      # filename = file_path.split('\\')[-1]  # For Windows
      # print(f"Selected filename: {filename}")
      return filename
   else:
      print("No file selected.")
      return None


if __name__ == "__main__":
   argParser = argparse.ArgumentParser()
   argParser.add_argument("input", nargs='?', type=str, help="input CSV filename with path")
   argParser.add_argument("-p", "--print_parsed_data", action='store_true', help="if true, print parsed info & dont plot")
   argParser.add_argument("-a", "--analyze_info_output", action='store_true', help="if true, print analysis info")

   args = argParser.parse_args()
   # print(f'{args.input= } {args.parse_info_output= } {args.analyze_info_output= }')

   if args.input is None:
      csv_filename = pick_file()
      if csv_filename is None:
         sys.exit("No PDF files selected to parse.")
      csv_filename = f'../{csv_filename}'
   else:
      csv_filename = args.input

   results= Parsed_results()
   results.parse_csv(csv_filename)

   if args.print_parsed_data:
      results.print_parse_info()
      sys.exit(0)

   if args.analyze_info_output:
      results.print_analysis_info()
      sys.exit(0)

   results.plot_it()
