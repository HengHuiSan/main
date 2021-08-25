from django.http.response import HttpResponse
from ecommerce.models import *
import pandas as pd
import numpy as np
# import the class containing the dimensionality reduction method
from sklearn.decomposition import TruncatedSVD


# ============= PART 1: Recommend Popular Items to New Users ============= # 





# ============= PART 2: Recommend Popular Item to New Users ============= # 

"""
 Model-based collaborative filtering system 
 based on customer's purchase history and 
 page views by other users who views items similar items
"""
def getAllRecommendation():
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

                # Recommend_list.sort(reverse=True) for top pick

                # [:12]
                Recommend_list = Recommend_list
   
    for i in Recommend_list:
        print(i)

    # objects = dict([(obj.id, obj) for obj in Recommend_list])
    # sorted_objects = [objects[id] for id in id_list]

    # objects = Furniture.objects.filter(furnitureId=Recommend_list)

    return Recommend_list
    # return HttpResponse(item_purchased)
    
     
def getMergeDf():
    furniture_df = pd.DataFrame(list(Furniture.objects.all().values()))
    user_views_df = pd.DataFrame(list(User_Views.objects.all().values()))

    user_views_df.rename(columns={'furnitureId_id':'furnitureId'}, inplace=True)
    merge_df = furniture_df.merge(user_views_df, on='furnitureId')
    merge_df = merge_df.drop(columns=['furnitureImg', 'unitPrice', 'categoryId_id', 'furnitureDesc', 'stock', 'id'])
    
    return merge_df

# Content-based Recommendation System
def contentBasedRec():
    collaborative_rec_list = getAllRecommendation()

    furniture_df = pd.DataFrame(list(Furniture.objects.all().values()))
    furniture_df = furniture_df.drop(columns=['furnitureImg', 'unitPrice', 'categoryId_id', 'stock'])
    furniture_df['furnitureDesc'] = furniture_df.furnitureDesc.str.split('|')

    furniture_with_desc = furniture_df.copy(deep=True)

    # Let's iterate through furniture_df, then append the description as columns of 1s or 0s.
    # 1 if that column contains product in the description at the present index and 0 if not.
    for index, row in furniture_df.iterrows(): # iterrows(): iterate over DataFrame rows
        for desc in row['furnitureDesc']:
            furniture_with_desc.at[index, desc] = 1   
    
    # Filling in the NaN values with 0 to show that a movie doesn't have that column's genre
    furniture_with_desc = furniture_with_desc.fillna(0)
    user_profile_df = pd.DataFrame(list(User_Views.objects.all().values()))
    user_profile_df.rename(columns={'furnitureId_id':'furnitureId'}, inplace=True)

    target_user_profile = user_profile_df[user_profile_df['userId_id'] == 2]
    target_user_profile = target_user_profile.merge(furniture_df, on='furnitureId').drop(columns=['id', 'furnitureDesc'])

    # filter the selection by outputing movies that exist in both lawrence_movie_ratings and movies_with_genres
    profile_with_desc = furniture_with_desc[furniture_with_desc.furnitureId.isin(target_user_profile.furnitureId)]
    profile_with_desc.reset_index(drop=True, inplace=True)
    profile_with_desc = profile_with_desc.drop(columns=['furnitureId', 'furnitureName', 'furnitureDesc'])
    
    # print('Shape of user1_profile is:',target_user_profile.shape)
    # print('Shape of user1_desc_df is:',profile_with_desc.shape)
    furniture_with_desc = furniture_with_desc.set_index(furniture_with_desc.furnitureId)
    furniture_with_desc = furniture_with_desc.drop(columns=['furnitureId', 'furnitureName', 'furnitureDesc'])

    view_df = target_user_profile.drop(columns=['userId_id','furnitureId','furnitureName'])
    user_profile = profile_with_desc.T.dot(view_df) 
    user_profile = user_profile / user_profile.values.sum()
    user_profile = pd.DataFrame(user_profile)
    # print(user_profile.values.sum())

    # recommend_furniture = furniture_with_desc.set_index('furnitureId')
    # recommend_furniture = (furniture_with_desc.drop(columns=['furnitureId','furnitureName', 'furnitureDesc']).T.dot(user_profile)) / user_profile.sum()
    # furniture_with_desc = furniture_with_desc.T
    # recommend_furniture = recommend_furniture / recommend_furniture.values.sum()
    recommend_furniture = furniture_with_desc.dot(user_profile)
    recommend_furniture = recommend_furniture / recommend_furniture.values.sum()

    recommend_furniture = pd.DataFrame(recommend_furniture)
    recommend_furniture = recommend_furniture[recommend_furniture['viewCount'] != 0]
    recommend_furniture.sort_values(by=['viewCount'], ascending=False, inplace=True)

    recommend_list = list(recommend_furniture.index)
    # recommend_list.remove('0')

    # recpd = pd.DataFrame(recommend_list)

    # recommend_list.sort(key=lambda x: x.get('viewCount'),  reverse=True)

    # remove similar items in both lists
    recommend_items = []
    for j in collaborative_rec_list:
        for i in recommend_list:
            if j != i:
                recommend_items.append(i)


    # print(recommend_furniture.info())

    # print(furniture_with_desc.shape)
    # print(user_profile.shape)
    # print(profile_with_desc.shape)
    # print(view_df.shape)

    return recommend_items
    # return HttpResponse(recommend_furniture.to_html())