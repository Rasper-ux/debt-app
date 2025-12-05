from django.urls import path
from .views import homePage, addDebt, deleteDebt

urlpatterns = [
    path('', homePage, name='home'),
    path('add_debt/', addDebt, name='add_debt'),
    path('delete_debt/<int:debt_id>/', deleteDebt, name='delete_debt'),
]