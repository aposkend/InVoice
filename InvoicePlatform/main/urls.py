from django.urls import path

from . import views

app_name = 'main'
urlpatterns = [
    path('mainpage/', views.getMainpage, name='getMainpage'),
    path('file/upload/', views.uploadFile, name='uploadFile'),
    path('district/', views.getDistrict, name='getDistrict'),
    path('tags/', views.getSmallTags, name='getSmallTags'),
    path('product/', views.getProducts, name='getProducts'),
    path('draw_buy_with/', views.drawBuyWith, name='drawBuyWith'),
    path('draw_product_in_path/', views.drawPath, name='drawPath'),
    path('rfm/', views.drawRFM, name='drawRFM'),
    path('rfm_with_product/', views.drawRFMwithProduct, name='drawRFMwithProduct'),
    path('info/', views.showInfo, name='showInfo'),
    path('deeper_insight/', views.getDeeperInsight, name='getDeeperInsight'),
    path('analysis/', views.analyze, name='analyze'),
    path('analysisq1/', views.analyzeq1, name='analyzeq1'),
    path('analysisq2/', views.analyzeq2, name='analyzeq2'),
    path('analysisq3/', views.analyzeq3, name='analyzeq3'),
    path('analysisq4/', views.analyzeq4, name='analyzeq4'),
    path('analysisq5/', views.analyzeq5, name='analyzeq5'),
    path('display_overtime/', views.displayOvertime, name='displayOvertime'),
    path('buy_with_in_path/', views.displayBuyWithInPath, name='displayBuyWithInPath'),
    path(
        'buy_with_in_path_networks/<uuid:uu_ID>/',
        views.displayBuyWithInPathNetworks,
        name='displayBuyWithInPathNetworks'
    ),
    path('save_data/', views.saveData, name='saveData'),
    path('stored_picture/', views.getStoredPicture, name='getStoredPicture'),
    path('load_picture/', views.loadPicture, name='loadPicture'),
    path('delete_graph/', views.deleteGraph, name='deleteGraph'),
]
