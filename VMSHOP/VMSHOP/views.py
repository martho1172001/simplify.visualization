from contextvars import Context
import pandas as pd
import pymongo
import numpy as np
from django.shortcuts import render
from statsmodels.tsa.statespace.sarimax import SARIMAX
import matplotlib.pyplot as plt
import io
import urllib, base64

client = pymongo.MongoClient("mongodb+srv://simplify:mineeproject@cluster0.glsg7.mongodb.net/?retryWrites=true&w=majority")
db = client.simplify
collection = db.newsales
collection1 = db.producer

def vmshop(request):
   # shop_id = request.user.shop_id

    shop_id = "1"
    data = pd.DataFrame(list(collection.find({'shop_id' : shop_id})))
    print(data)
    data['Sales'] = pd.to_numeric(data['Sales'], errors='coerce')
    product = "Product"
    date = "Date"
    # Get a list of all products in the shop
    products = list(data[product].unique())    
    # Pass the list of products to the template
    currentdate = data[date].max()
    print(currentdate)
    product_data = data[data[date] == currentdate]
    
  #  sales_by_product = data.groupby('Product')['Sales'].sum()
    print(product_data)

    forecast_dict = dict(zip(product_data['Product'], np.round(product_data['Sales'], 2)))
    print(forecast_dict)
    plot_data = generate_plotbar(forecast_dict)
    
  
    context = {'products': products,'plot_data':plot_data}
    return render(request, 'vmshop.html', context)

def outvms(request):
     # shop_id = request.user.shop_id

    shop_id = "1"
    data = pd.DataFrame(list(collection.find({'shop_id' : shop_id})))
    data['Sales'] = pd.to_numeric(data['Sales'], errors='coerce')
    products = "Product"
    if request.method == 'POST':
        # Get selected product from dropdown
        selected_product = request.POST.get('selected_product')
        startdate = request.POST.get('startdate')
        # Filter data to get sales of the selected product
        product_data = data[(data[products] == selected_product) & (data['Date'] >= startdate)]
      #  product_data = produc_data.iloc[:-12, :]
      
      #  model = SARIMAX(product_data['Sales'], order=(1, 1, 1), seasonal_order=(1, 1, 0, 12)).fit()

       

        # Create a list of months for the forecast
        months = pd.date_range(start=startdate,end=product_data['Date'].max(),freq='MS').strftime('%B %Y')

        # Combine forecast and months into a dictionary
        forecast_dict = dict(zip(months, np.round(product_data['Sales'], 2)))
       # forecast_dict = dict(zip(months, np.round(forecast, 2)))
       # forecast_dict = dict(zip(months, np.round(forecast.values, 2)))
        plot_data = generate_plot(forecast_dict)
        print(forecast_dict)
        # Pass the forecast dictionary and the list of products to the template
        context = {'plot_data': plot_data,'startdate': startdate,'forecast': forecast_dict, 'selected_product':selected_product, 'shopid': shop_id, 'product_data':product_data['Sales']}
        return render(request, 'outvms.html', context)

  

def vmowner(request):
    data = pd.DataFrame(list(collection.find()))
    data['Sales'] = pd.to_numeric(data['Sales'], errors='coerce')
    print(data)
    product = "Product"
    shop_id = "shop_id"
    date = "Date"
    # Get a list of all products in the shop
    products = list(data[product].unique())
    shop_ids = list(data[shop_id].unique())
    
    currentdate = data[date].max()
    print(currentdate)
    product_data = data[data[date] == currentdate]
    print(product_data)
    prod_data = product_data.loc[:, ['Product', 'Sales',]]
    print(prod_data)
    prod_data = product_data.groupby('Product')['Sales'].sum()

    forecast_dict = dict(zip(prod_data.index, prod_data.values))
    print(forecast_dict)
    plot_data = generate_plotbar(forecast_dict)   

    # Pass the list of products to the template
    context = {'products': products, 'shop_ids': shop_ids, 'plot_data': plot_data }
    return render(request, 'vmowner.html', context)


def generate_plotbar(forecast_dict):
    # Create a figure and axis object
    plt.clf()
    fig, ax = plt.subplots(figsize=(10, 10))

    # Plot the forecast
    ax.bar(forecast_dict.keys(), forecast_dict.values())
    # Set the title and labels
    ax.set_title('Visualization plot')
    ax.set_xlabel('Product')
    ax.set_ylabel('Sales')


    # Rotate x-axis labels
    
    # Save the plot to a temporary buffer
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)

    # Encode the plot as base64 string
    plot_data = base64.b64encode(buffer.read()).decode('utf-8')

    return plot_data

def generate_plotbarshop(forecast_dict):
    # Create a figure and axis object
    plt.clf()
    fig, ax = plt.subplots(figsize=(10, 10))

    # Plot the forecast
    ax.bar(forecast_dict.keys(), forecast_dict.values())
    # Set the title and labels
    ax.set_title('Visualization plot')
    ax.set_xlabel('Shop ids')
    ax.set_ylabel('Sales')


    # Rotate x-axis labels
    
    # Save the plot to a temporary buffer
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)

    # Encode the plot as base64 string
    plot_data = base64.b64encode(buffer.read()).decode('utf-8')

    return plot_data

def generate_plot(forecast_dict):
    # Create a figure and axis object
    plt.clf()
    fig, ax = plt.subplots(figsize=(13, 14))

    # Plot the forecast
    ax.plot(forecast_dict.keys(), forecast_dict.values())

    # Set the title and labels
    ax.set_title('Visualization plot')
    ax.set_xlabel('Month')
    ax.set_ylabel('Sales')


    # Rotate x-axis labels
    plt.xticks(rotation='vertical')
    # Save the plot to a temporary buffer
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)

    # Encode the plot as base64 string
    plot_data = base64.b64encode(buffer.read()).decode('utf-8')

    return plot_data


def generate_plotgrp(compare_data,present_data):
   # current_data = current_data.pivot(index='Product', columns='Date' , values='Sales')
    #compare_data = compare_data.pivot(index='Product', columns='Date',values='Sales')
    plt.clf()
# plot stacked bar chart
    print(present_data)
    print(compare_data)
# Plotting the sales data using a line chart
    plt.plot(present_data['Product'], present_data['Sales'], label='Current Data')
    plt.plot(compare_data['Product'], compare_data['Sales'], label='Compare Data')

    # Set the title and labels
    plt.title('Comparison')
    plt.xlabel('Sales')
    plt.ylabel('Product')
    # add legend to the plot
    plt.legend()

   
    # Save the plot to a temporary buffer
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)

    # Encode the plot as base64 string
    plot_data = base64.b64encode(buffer.read()).decode('utf-8')

    return plot_data



def outvmo(request):
    if request.method == 'POST':
        # Get selected shop from dropdown
        selected_shop = request.POST.get('selected_shop')
        # Get selected product from dropdown
        selected_product = request.POST.get('selected_product')
        data = pd.DataFrame(list(collection.find()))
        data['Sales'] = pd.to_numeric(data['Sales'], errors='coerce')
        # Filter data to get sales of the selected product
        product = "Product"
        shop_id = "shop_id"
        produc_data = data[data[product] == selected_product]
        
        product_data = produc_data[produc_data[shop_id] == selected_shop]
      
        startdate = request.POST.get('startdate')
        # Filter data to get sales of the selected product
        product_data = data[(data[product] == selected_product) & (data['Date'] >= startdate)]
      #  product_data = produc_data.iloc[:-12, :]
      
        
        # Create a list of months
        months = pd.date_range(end=product_data['Date'].max(), start=startdate, freq='MS').strftime('%B %Y')

        # Combine sales values and months into a dictionary
        sales_dict = dict(zip(months, np.round(product_data['Sales'], 2)))
        
        # Generate the plot
        plot_data = generate_plot(sales_dict)


        context = {'plot_data': plot_data,'startdate': startdate, 'forecast': sales_dict, 'selected_product':selected_product, 'shopid': shop_id, 'selected_shop': selected_shop}
        return render(request, 'outvmo.html', context)


def vmprod(request):
   # producer_id = request.user.producer_id
    producer_id = "1"
    data = pd.DataFrame(list(collection1.find({'producer_id' : producer_id})))
    
    print(data)
    product = "Product"
    date = "Date"
    sales = "Sales"
    # Get a list of all products in the shop
    products = list(data[product].unique())

    data = pd.DataFrame(list(collection.find({'Product': {'$in': products}})))
    data['Sales'] = pd.to_numeric(data['Sales'], errors='coerce')
    shopids = list(data['shop_id'].unique())
    print(data)
    currentdate = data[date].max()
    print(currentdate)
    product_data = data[data[date] == currentdate]
    print(product_data)
    prod_data = product_data.loc[:, ['Product', 'Sales',]]
    print(prod_data)
    prod_data = product_data.groupby('Product')['Sales'].sum()

    

    forecast_dict = dict(zip(prod_data.index, prod_data.values))
    print(forecast_dict)
    plot_data = generate_plotbar(forecast_dict)    
    # Pass the list of products to the template
    context = {'products': products,'plot_data': plot_data,'shopids': shopids ,'data':data}
    return render(request, 'vmprod.html', context)

def outvmp(request):
     # shop_id = request.user.shop_id
    sales_by_date = {}
    products = "Product"
    if request.method == 'POST':
        # Get selected product from dropdown
        selected_product = request.POST.get('selected_product')
        start_date = request.POST.get('startdate')
      
        collection = db.newsales
        product_data = pd.DataFrame(list(collection.find({products: selected_product})))
        product_data['Sales'] = pd.to_numeric(product_data['Sales'], errors='coerce')
        print(product_data)
        # group rows by date and sum the sales values for each date
        sales_by_date = product_data.groupby('Date')['Sales'].sum()

        # visualize sales data by date using matplotlib
  
        print(sales_by_date)
        months = pd.date_range(start=start_date,end=sales_by_date.index.max(),freq='MS').strftime('%B %Y')

        # Combine forecast and months into a dictionary
        forecast_dict = dict(zip(months, np.round(sales_by_date.values, 2)))
   
  
        plot_data = generate_plot(forecast_dict)

        # Pass the forecast dictionary and the list of products to the template
        context = {'plot_data': plot_data,'startdate': start_date,'forecast': forecast_dict, 'selected_product':selected_product, 'product_data':product_data['Sales']}
        return render(request, 'outvmp.html', context)

def outvmscompare(request):
    # shop_id = request.user.shop_id

    shop_id = "1"
    data = pd.DataFrame(list(collection.find({'shop_id' : shop_id})))
    data['Sales'] = pd.to_numeric(data['Sales'], errors='coerce')
    product = "Product"
    date = "Date"  
    currentdate = data[date].max()
    if request.method == 'POST':
        # Get selected product from dropdown
        comparedate = request.POST.get('comparedate')
        product_data = data[data[date] == currentdate]
        compare_data = data[data[date] == comparedate]
        
        # Select two columns from the dataframe
        product_data = product_data.loc[:, ['Product', 'Sales','Date']]
        compare_data = compare_data.loc[:, ['Product', 'Sales','Date']]
        plot_compare = generate_plotgrp(compare_data,product_data)
    
    
  
    context = {'plot_compare': plot_compare , 'comparedate':comparedate}
    return render(request, 'outVMScompare.html', context)

def outvmpprodwise(request):

    # producer_id = request.user.producer_id
    producer_id = "1"
    data = pd.DataFrame(list(collection1.find({'producer_id' : producer_id})))
    
    print(data)
    product = "Product"
    date = "Date"
    sales = "Sales"
    # Get a list of all products in the shop
    products = list(data[product].unique())

    data = pd.DataFrame(list(collection.find({'Product': {'$in': products}})))
    data['Sales'] = pd.to_numeric(data['Sales'], errors='coerce')
    shopids = list(data['shop_id'].unique())
    product = "Product"
    date = "Date" 
    if request.method == 'POST':
        print(products)
        print(data)
        currentdate = data[date].max()
        current_data = data[data[date] == currentdate]
        selected_shop = request.POST.get('selected_shop')
        print(selected_shop)
        product_data = current_data[current_data['shop_id'] == selected_shop]
        # visualize sales data by date using matplotlib
        forecast_dict = dict(zip(product_data['Product'], np.round(product_data['Sales'], 2)))
        print(forecast_dict)
        plot_data = generate_plotbar(forecast_dict)  
        
        # Pass the forecast dictionary and the list of products to the template
        context = {'plot_data': plot_data,'forecast': forecast_dict,'selected_shop':selected_shop}
        return render(request, 'outvmpprodwise.html', context)

def outvmpshopwise(request):

    # producer_id = request.user.producer_id
    producer_id = "1"
    data = pd.DataFrame(list(collection1.find({'producer_id' : producer_id})))
    
    print(data)
    product = "Product"
    date = "Date"
    sales = "Sales"
    # Get a list of all products in the shop
    products = list(data[product].unique())

    data = pd.DataFrame(list(collection.find({'Product': {'$in': products}})))
    data['Sales'] = pd.to_numeric(data['Sales'], errors='coerce')
    shopids = list(data['shop_id'].unique())
    product = "Product"
    date = "Date" 
    if request.method == 'POST':
        print(products)
        print(data)
        currentdate = data[date].max()
        current_data = data[data[date] == currentdate]
        selected_product = request.POST.get('selected_product')
        print(selected_product)
        product_data = current_data[current_data['Product'] == selected_product]
        # visualize sales data by date using matplotlib
        forecast_dict = dict(zip(product_data['shop_id'], np.round(product_data['Sales'], 2)))
        print(forecast_dict)
        plot_data = generate_plotbarshop(forecast_dict)  
        
        # Pass the forecast dictionary and the list of products to the template
        context = {'plot_data': plot_data,'forecast': forecast_dict,'selected_product':selected_product}
        return render(request, 'outvmpshopwise.html', context)


##########################################################################################################################################################




def outvmoshop(request):
   # shop_id = request.user.shop_id
    if request.method == 'POST':
        shop_id = request.POST.get('selected_shop')
        data = pd.DataFrame(list(collection.find({'shop_id' : shop_id})))
        print(data)
        data['Sales'] = pd.to_numeric(data['Sales'], errors='coerce')
        product = "Product"
        date = "Date"
        # Get a list of all products in the shop
        products = list(data[product].unique())    
        # Pass the list of products to the template
        currentdate = data[date].max()
        print(currentdate)
        product_data = data[data[date] == currentdate]
        
    #  sales_by_product = data.groupby('Product')['Sales'].sum()
        print(product_data)

        forecast_dict = dict(zip(product_data['Product'], np.round(product_data['Sales'], 2)))
        print(forecast_dict)
        plot_data = generate_plotbar(forecast_dict)
        
    
        context = {'products': products,'plot_data':plot_data,'selected_shop':shop_id}
        return render(request, 'outvmoshop.html', context)

def outvmovms(request,selected_shop=None):
     # shop_id = request.user.shop_id
    if request.method == 'POST':
        shop_id = selected_shop

        data = pd.DataFrame(list(collection.find({'shop_id' : shop_id})))
        data['Sales'] = pd.to_numeric(data['Sales'], errors='coerce')
        products = "Product"
   
        # Get selected product from dropdown
        selected_product = request.POST.get('selected_product')
        startdate = request.POST.get('startdate')
        # Filter data to get sales of the selected product
        product_data = data[(data[products] == selected_product) & (data['Date'] >= startdate)]
      #  product_data = produc_data.iloc[:-12, :]
      
      #  model = SARIMAX(product_data['Sales'], order=(1, 1, 1), seasonal_order=(1, 1, 0, 12)).fit()

       

        # Create a list of months for the forecast
        months = pd.date_range(start=startdate,end=product_data['Date'].max(),freq='MS').strftime('%B %Y')

        # Combine forecast and months into a dictionary
        forecast_dict = dict(zip(months, np.round(product_data['Sales'], 2)))
       # forecast_dict = dict(zip(months, np.round(forecast, 2)))
       # forecast_dict = dict(zip(months, np.round(forecast.values, 2)))
        plot_data = generate_plot(forecast_dict)
        print(forecast_dict)
        # Pass the forecast dictionary and the list of products to the template
        context = {'plot_data': plot_data,'startdate': startdate,'forecast': forecast_dict, 'selected_product':selected_product, 'selected_shop': shop_id, 'product_data':product_data['Sales']}
        return render(request, 'outvmovms.html', context)

  
def outvmovmscompare(request,selected_shop=None):
    # shop_id = request.user.shop_id
    print(selected_shop)
    if request.method == 'POST':
        shop_id = selected_shop
        data = pd.DataFrame(list(collection.find({'shop_id' : shop_id})))
        data['Sales'] = pd.to_numeric(data['Sales'], errors='coerce')
        product = "Product"
        date = "Date"  
        currentdate = data[date].max()
        # Get selected product from dropdown
        comparedate = request.POST.get('comparedate')
        product_data = data[data[date] == currentdate]
        compare_data = data[data[date] == comparedate]
        
        # Select two columns from the dataframe
        product_data = product_data.loc[:, ['Product', 'Sales','Date']]
        compare_data = compare_data.loc[:, ['Product', 'Sales','Date']]
        plot_compare = generate_plotgrp(compare_data,product_data)

    
  
    context = {'plot_compare': plot_compare , 'comparedate':comparedate, 'selected_shop':shop_id}
    return render(request, 'outvmoVMScompare.html', context)






def outvmoprod(request):
   # producer_id = request.user.producer_id
    date = "Date" 
    if request.method == 'POST':
        selected_product = request.POST.get('selected_product')
        data = pd.DataFrame(list(collection.find({'Product': selected_product})))
        data['Sales'] = pd.to_numeric(data['Sales'], errors='coerce')
        currentdate = data[date].max()
        current_data = data[data[date] == currentdate]
        print(current_data)
        print(selected_product)
        product_data = current_data[current_data['Product'] == selected_product]
        # visualize sales data by date using matplotlib
        forecast_dict = dict(zip(product_data['shop_id'], np.round(product_data['Sales'], 2)))
        print(forecast_dict)
        plot_data = generate_plotbarshop(forecast_dict)  
        
        # Pass the forecast dictionary and the list of products to the template
        context = {'plot_data': plot_data,'forecast': forecast_dict,'selected_product':selected_product}
        return render(request, 'outvmoprod.html', context)

def outvmovmp(request,selected_product=None):
     # shop_id = request.user.shop_id
    sales_by_date = {}
    products = "Product"
    if request.method == 'POST':
        # Get selected product from dropdown
        start_date = request.POST.get('startdate')
      
        collection = db.newsales
        product_data = pd.DataFrame(list(collection.find({products: selected_product})))
        product_data['Sales'] = pd.to_numeric(product_data['Sales'], errors='coerce')

        # group rows by date and sum the sales values for each date
        sales_by_date = product_data.groupby('Date')['Sales'].sum()

        # visualize sales data by date using matplotlib
  
        
        months = pd.date_range(start=start_date,end=sales_by_date.index.max(),freq='MS').strftime('%B %Y')

        # Combine forecast and months into a dictionary
        forecast_dict = dict(zip(months, np.round(sales_by_date.values, 2)))
   
  
        plot_data = generate_plot(forecast_dict)

        # Pass the forecast dictionary and the list of products to the template
        context = {'plot_data': plot_data,'startdate': start_date,'forecast': forecast_dict, 'selected_product':selected_product, 'product_data':product_data['Sales']}
        return render(request, 'outvmovmp.html', context)


