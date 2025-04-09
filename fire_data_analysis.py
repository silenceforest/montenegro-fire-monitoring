#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fire Data Analysis Script
--------------------------
This script processes and visualizes fire event data derived from satellite observations.
It leverages data produced by the MODIS C6.1 sensor, with the following metadata:

    Data Source     : MODIS C6.1
    Start Date      : 2000-11-01
    End Date        : 2025-01-16
    Output Format   : csv
    Area of Interest: Montenegro

The original data can be accessed at: https://firms.modaps.eosdis.nasa.gov

The script executes the following workflow:
  1. Loads the data with robust error handling.
  2. Preprocesses the data by cleaning and converting date‐time fields.
  3. Summarizes the data by aggregating fire events on annual and monthly bases.
  4. Generates visualizations including:
       - A line chart showing the number of fires per year.
       - A bar chart illustrating the average number of fires per month.
       - A heatmap representing the distribution of fire events by year and month.

Requirements:
  - Python 3.x
  - numpy, pandas, matplotlib, seaborn

This modular code is ready for publication on GitHub.

Author: [Your Name]
Date: [YYYY-MM-DD]
License: [Your License, e.g., MIT License]
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import logging
from pathlib import Path

# Configure logging to display information and errors for debugging purposes.
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# Define the path to the CSV file containing the fire archive data.
fire_data_path = Path('fire_archive_(1km)_M-C61_566833.csv')


def load_data(path):
    """
    Load data from a CSV file using pandas.
    
    Parameters:
        path (Path): The file path of the CSV file to be loaded.
    
    Returns:
        pd.DataFrame: A DataFrame containing the loaded data.
    
    The function includes error handling to capture issues during loading and logs the
    shape of the DataFrame upon successful load.
    """
    try:
        data = pd.read_csv(
            path,
            na_values=['', ' ', 'NA', 'NaN', None],
            low_memory=False
        )
        logging.info(f"Loaded {data.shape[0]} rows and {data.shape[1]} columns.")
        return data
    except Exception as e:
        logging.error(f"Error loading data: {e}")
        raise


def preprocess_data(df):
    """
    Preprocess the fire event data by cleaning and converting date-time information.
    
    Parameters:
        df (pd.DataFrame): The raw DataFrame loaded from the CSV file.
        
    Returns:
        pd.DataFrame: A cleaned DataFrame with properly formatted date-time fields and new columns:
                      'year', 'month', and 'year_month' for further aggregation.
    
    Steps performed:
      1. Remove rows with missing 'acq_date' or 'acq_time' fields.
      2. Convert 'acq_time' to a string of four digits (e.g., "0705").
      3. Create a new datetime column by combining 'acq_date' and 'acq_time'.
      4. Eliminate rows where date-time conversion fails.
      5. Extract and add 'year' and 'month' columns.
      6. Create a 'year_month' column as a Period object for monthly grouping.
    """
    # Drop rows missing 'acq_date' or 'acq_time'
    df = df.dropna(subset=['acq_date', 'acq_time'])
    
    # Convert 'acq_time' to a 4-character string with leading zeros if necessary.
    df['acq_time'] = df['acq_time'].astype(str).str.zfill(4)
    
    # Combine 'acq_date' and 'acq_time' to form a new 'datetime' column.
    df['datetime'] = pd.to_datetime(
        df['acq_date'] + ' ' + df['acq_time'],
        format='%Y-%m-%d %H%M',
        errors='coerce'
    )
    
    # Drop rows where the datetime conversion was unsuccessful.
    initial_count = df.shape[0]
    df = df.dropna(subset=['datetime'])
    logging.info(f"Dropped {initial_count - df.shape[0]} rows due to invalid datetime conversion.")
    
    # Extract the year and month from the 'datetime' column.
    df['year'] = df['datetime'].dt.year
    df['month'] = df['datetime'].dt.month
    # Create a 'year_month' column as a Period (monthly) for grouping purposes.
    df['year_month'] = df['datetime'].dt.to_period('M')
    
    return df


def summarize_data(df):
    """
    Aggregate fire event data for analysis.
    
    Parameters:
        df (pd.DataFrame): The cleaned DataFrame containing fire events.
        
    Returns:
        yearly_counts (pd.Series): The count of fire events for each year.
        monthly_counts (pd.Series): The aggregate count of fire events for each month across all years.
        seasonal_means (pd.Series): The average number of fires per month (monthly count divided by the number of years).
        monthly_heatmap (pd.DataFrame): A pivot table with years as rows and months as columns,
                                        representing the fire event counts for each combination.
    
    This summarization is instrumental for visualizing trends on both annual and seasonal bases.
    """
    # Group data by year and count the number of events per year.
    yearly_counts = df.groupby('year').size()
    # Group data by month (across all years) to get total counts.
    monthly_counts = df.groupby('month').size()
    # Calculate average fires per month by dividing monthly counts by the number of unique years.
    seasonal_means = df.groupby('month').size() / df['year'].nunique()
    # Create a pivot table: rows represent years, columns represent months.
    monthly_heatmap = df.groupby(['year', 'month']).size().unstack(fill_value=0)
    
    return yearly_counts, monthly_counts, seasonal_means, monthly_heatmap


def plot_yearly_fires(yearly_counts):
    """
    Plot a line chart showing the number of fire events per year.
    
    Parameters:
        yearly_counts (pd.Series): A pandas Series where the index represents the year and the values are fire event counts.
        
    The function creates a line plot with markers, sets appropriate chart titles, labels, and gridlines,
    and uses a tight layout for optimal display.
    
    Note: The data represented in the chart is based on satellite observations 
          (MODIS C6.1; 2000-11-01 to 2025-01-16; Area: Montenegro).
    """
    plt.figure(figsize=(12, 6))
    plt.plot(yearly_counts.index, yearly_counts.values, marker='o', linestyle='-')
    plt.title('Number of Fires per Year')
    plt.xlabel('Year')
    plt.ylabel('Number of Fires')
    plt.grid(True)
    plt.tight_layout()
    plt.show()


def plot_seasonal_trends(seasonal_means):
    """
    Plot a bar chart depicting the average number of fire events per month.
    
    Parameters:
        seasonal_means (pd.Series): A Series with month numbers as the index and average fire counts as values.
        
    The x-axis is labeled with abbreviated month names, which helps to visualize seasonal variations.
    
    Note: The data represented in the chart is based on satellite observations 
          (MODIS C6.1; 2000-11-01 to 2025-01-16; Area: Montenegro).
    """
    plt.figure(figsize=(12, 6))
    plt.bar(seasonal_means.index, seasonal_means.values)
    plt.title('Average Number of Fires per Month')
    plt.xlabel('Month')
    plt.ylabel('Average Monthly Fires')
    # Customize x-axis tick labels to show month abbreviations.
    plt.xticks(
        ticks=range(1, 13),
        labels=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    )
    plt.grid(axis='y')
    plt.tight_layout()
    plt.show()


def plot_monthly_heatmap(monthly_heatmap):
    """
    Create a heatmap visualizing monthly fire event counts across different years.
    
    Parameters:
        monthly_heatmap (pd.DataFrame): A pivot table with years as rows and months as columns containing fire counts.
        
    The heatmap uses a color gradient (YlOrRd colormap) to indicate the intensity of fire events,
    making it easier to identify patterns over time.
    
    Note: The data represented in the chart is based on satellite observations 
          (MODIS C6.1; 2000-11-01 to 2025-01-16; Area: Montenegro).
    """
    plt.figure(figsize=(12, 8))
    sns.heatmap(monthly_heatmap, cmap='YlOrRd', annot=False, linewidths=0.5)
    plt.title('Monthly Fire Events by Year (Heatmap)')
    plt.xlabel('Month')
    plt.ylabel('Year')
    plt.tight_layout()
    plt.show()


def main():
    """
    Main function orchestrating the workflow of the fire data analysis.
    
    It sequentially:
      1. Loads the CSV data.
      2. Preprocesses the data to extract and convert date-time information.
      3. Aggregates the data for both annual and seasonal analyses.
      4. Generates and displays visualizations: a yearly trend line, 
         a monthly averages bar chart, and a heatmap of monthly fire events.
    """
    # Step 1: Load the raw fire data.
    fire_data = load_data(fire_data_path)
    # Step 2: Preprocess the data to clean and format date-time fields.
    fire_data_clean = preprocess_data(fire_data)
    
    # Step 3: Summarize the data to obtain aggregates and pivot tables.
    yearly_counts, monthly_counts, seasonal_means, monthly_heatmap = summarize_data(fire_data_clean)
    
    # Step 4: Plot the visualizations.
    plot_yearly_fires(yearly_counts)
    plot_seasonal_trends(seasonal_means)
    plot_monthly_heatmap(monthly_heatmap)


if __name__ == '__main__':
    main()
