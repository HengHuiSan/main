from django.http.response import HttpResponse
from django.shortcuts import render
from ecommerce.models import *
import pandas as pd
import numpy as np
# import the class containing the dimensionality reduction method
from sklearn.decomposition import TruncatedSVD

# Create your views here.
def goHompage(request):
    result = Furniture.objects.all()
    # result = pd.DataFrame(list(Order.objects.get(userId=1)))
    # return HttpResponse(result.to_html())
    return render(request,'homepage.html', {'furniture':result})

def goCatalog(request): 
    category = Category.objects.all()

    if request.method == 'GET' and 'cid' in request.GET:
        cid = request.GET['cid']
    else:
        cid = 1

    furniture = Furniture.objects.filter(categoryId_id=cid)
    context = {"furniture":furniture, "categories":category}

    return render(request,'catalog.html', context)

def goDonate(request):
    return render(request,'donate.html')

def goAbout(request):
    return render(request,'about.html')


# ====================================================================================== # 

def generate_recommendation(request):
    if request.method == 'POST':
        if(request.POST.get('btnTopPicks')):
            user = 1
        elif(request.POST.get('btnPopular')):
            user = 2
        elif(request.POST.get('btnAll')):
            getAllRecommendation()

# Model-based collaborative filtering system based on customer's purchase history and 
# page views by other users who views items similar items
def getAllRecommendation(request):
    furniture_profile_df = getMergeDf()

    #Creating a sparse pivot table with items in rows and users in columns
    items_users_pivot_matrix_df = furniture_profile_df.pivot_table(index='furnitureId', columns='userId_id', values='viewCount').fillna(0)

    # Decomposing the Matrix
    SVD = TruncatedSVD(n_components=10) # n_components=10: final number of dimensions

    # Fit the instance on the data and then transform the data
    decomposed_matrix = SVD.fit_transform(items_users_pivot_matrix_df)

    # Compute correlation coefficients 
    correlation_matrix = np.corrcoef(decomposed_matrix)

    # get all the orders that made by target user from 'Order' table
    oid_list = list(Order.objects.filter(userId=2).values_list('orderId', flat=True)) # flat=True : mean that the returned result is a single value, not a tuple. 

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
    # df = contentBasedRec()
    category_list = []
    furniture = Furniture.objects.all()
    category = Category.objects.all()

    for i in category:
        category_list.append(i.categoryName)

    context = {"getData":furniture, "categories":category_list}
    return HttpResponse("sda")


# Content-based Recommendation System
def contentBasedRec():
    furniture_df = pd.DataFrame(list(Furniture.objects.all().values()))
    furniture_df = furniture_df.drop(c )
    furniture_df['furnitureDesc'] = furniture_df.furnitureDesc.str.split('|')

    furniture_with_desc = furniture_df.copy(deep=True)

    # Let's iterate through furniture_df, then append the description as columns of 1s or 0s.
    # 1 if that column contains product in the description at the present index and 0 if not.
    for index, row in furniture_df.iterrows(): # iterrows(): iterate over DataFrame rows
        for desc in row['furnitureDesc']:
            furniture_with_desc.at[index, desc] = 1   
    
    #Filling in the NaN values with 0 to show that a movie doesn't have that column's genre
    furniture_with_desc = furniture_with_desc.fillna(0)
    user_profile_df = pd.DataFrame(list(User_Profile.objects.all().values()))
    user_profile_df.rename(columns={'furnitureId_id':'furnitureId'}, inplace=True)

    target_user_profile = user_profile_df[user_profile_df['userId_id'] == 2]
    target_user_profile = target_user_profile.merge(furniture_df, on='furnitureId').drop(columns=['id', 'furnitureDesc'])

    # filter the selection by outputing movies that exist in both lawrence_movie_ratings and movies_with_genres
    profile_with_desc = furniture_with_desc[furniture_with_desc.furnitureId.isin(target_user_profile.furnitureId)]
    profile_with_desc.reset_index(drop=True, inplace=True)
    profile_with_desc = profile_with_desc.drop(columns=['furnitureId', 'furnitureName', 'furnitureDesc'])
    
    # print('Shape of user1_profile is:',target_user_profile.shape)
    # print('Shape of user1_desc_df is:',profile_with_desc.shape)
    # furniture_with_desc = furniture_with_desc.drop(columns=['furnitureId', 'furnitureName', 'furnitureDesc'])

    view_df = target_user_profile.drop(columns=['userId_id','furnitureId','furnitureName'])
    user_profile = profile_with_desc.T.dot(view_df)

    recommend_furniture = furniture_with_desc.set_index(furniture_with_desc.furnitureId)
    recommend_furniture = (furniture_with_desc.drop(columns=['furnitureId','furnitureName', 'furnitureDesc']).T.dot(user_profile)) / user_profile.sum()

    # print(user_profile.sum())
    
    return recommend_furniture.to_html()


