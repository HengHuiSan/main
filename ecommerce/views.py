from django.http.response import HttpResponse
from django.shortcuts import render
from pandas.core.frame import DataFrame
from pandas.core.reshape.merge import merge
from ecommerce.models import *
# from django.http.response import HttpResponse
import pandas as pd
import numpy as np
# import the class containing the dimensionality reduction method
from sklearn.decomposition import TruncatedSVD

# Create your views here.
def getHompage(request):
    # result = Furniture.objects.all()
    result = pd.DataFrame(list(Order.objects.get(userId=1)))
    return HttpResponse(result.to_html())
    # return render(request,'homepage.html', {'furniture':result})

def goCatalog(request): 
    return render(request,'catalog.html')

def goDonate(request):
    return render(request,'donate.html')

def goAbout(request):
    return render(request,'about.html')

def generate_recommendation(request):
    if request.method == 'POST':
        if(request.POST.get('btnTopPicks')):
            user = 1
        elif(request.POST.get('btnPopular')):
            user = 2
        elif(request.POST.get('btnLatest')):
            user = 3
        elif(request.POST.get('btnAll')):
            getAllRecommendation()

# Model-based collaborative filtering system based on customer's purchase history and 
# page views by other users who views items similar items
def getAllRecommendation(request):
    furniture_profile_df = getMergeDf()

    #Creating a sparse pivot table with items in rows and users in columns
    items_users_pivot_matrix_df = furniture_profile_df.pivot_table(index='furnitureId', columns='userId_id', values='viewCount').fillna(0)

    # Decomposing the Matrix
    # n_components=10: final number of dimensions
    SVD = TruncatedSVD(n_components=10) 

    # Fit the instance on the data and then transform the data
    decomposed_matrix = SVD.fit_transform(items_users_pivot_matrix_df)
    # print(decomposed_matrix)

    # Compute correlation coefficients 
    correlation_matrix = np.corrcoef(decomposed_matrix)
    # print(correlation_matrix)

    # get all the orders that made by target user from 'Order' table
    oid_list = list(Order.objects.filter(userId=2).values_list('orderId', flat=True)) # flat=True : mean that the returned result is a single value, not a tuple. 
    # list() : change queryset to list

    # get all items purchased from the order list of target user
    all_items_purchased_list = list(Order_Products.objects.values_list('orderId', 'furnitureId'))

    items_purchased = []

    for oid in oid_list:
        for i in range(len(all_items_purchased_list)):
            if oid == all_items_purchased_list[i][0]:
                items_purchased.append(all_items_purchased_list[i][1])

    for i in items_purchased:
        for j in range(len(items_users_pivot_matrix_df)):
            if(items_users_pivot_matrix_df.index[j] == i):
                # print(items_users_pivot_matrix_df.index[j])
                fid_list = list(items_users_pivot_matrix_df.index) # change everything into list form
                # find the index(location) of the target item
                item_purchased = fid_list.index(i)
                # get correlation coefficients value of the item
                correlation = correlation_matrix[item_purchased]
                # r = 0.9 suggests a strong, positive association between two variables, 
                # whereas a correlation of r = -0.2 suggest a weak, negative association.
                Recommend_list = list(items_users_pivot_matrix_df.index[correlation > 0.90])
                # Removes the item already bought by the customer
                Recommend_list.remove(i) 

    return HttpResponse("ad")

     
def getMergeDf():
    furniture_df = pd.DataFrame(list(Furniture.objects.all().values()))
    user_profile_df = pd.DataFrame(list(User_Profile.objects.all().values()))

    user_profile_df.rename(columns={'furnitureId_id':'furnitureId'}, inplace=True)
    merge_df = furniture_df.merge(user_profile_df, on='furnitureId')
    merge_df = merge_df.drop(columns=['furnitureImg', 'unitPrice', 'categoryId_id', 'furnitureDesc', 'stock', 'id'])
    
    return merge_df

def testing(request):
    df = getMergeDf()

    return HttpResponse(df.to_html())



