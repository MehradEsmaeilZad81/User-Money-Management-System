from django.urls import path, include
from .views import GeneralSourceView, MySubscriptionView, GeneralSourceDetailView, MoneyAccountView

urlpatterns = [
    path('generalsources', GeneralSourceView.as_view()),
    path('mysubscriptions', MySubscriptionView.as_view()),
    path('generalsource/<int:pk>/', GeneralSourceDetailView.as_view()),
    path('moneyaccounts/', MoneyAccountView.as_view()),
]
