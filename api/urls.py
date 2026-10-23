from django.urls import path
from .views import ( 
    MenuViewSet, CategoriesListView, LoginView, RegisterView, 
    CreateOrderView, ClientAddressesView, ClientOrderHistoryView, 
    UpdateProfileView, ManageAddressView, ManageFavoriteView, 
    ClientFavoritesView, DeleteProfileView, SyncCartItemView, 
    ClientBonusBalanceView, ClientActiveOrdersView, ClientCardsView, 
    ManageCardView, OrderDetailsView,
    DownloadReceiptView, # <-- 1. ДОБАВИЛИ ИМПОРТ НОВОГО КЛАССА СКАЧИВАНИЯ ЧЕКА
    UpdateOrderStatusView # <-- 2. ДОАБВИЛИ ИМПОРТ НОВОГО КЛАССА ОБНОВЛЕНИЯ БОНУСОВ
)

urlpatterns = [
    path('menu/', MenuViewSet.as_view({'get': 'list', 'post': 'create'}), name='get-menu'),
    path('categories/', CategoriesListView.as_view(), name='get-categories'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('order/create/', CreateOrderView.as_view(), name='create-order'),
    path('client/<int:client_id>/addresses/', ClientAddressesView.as_view(), name='client-addresses'),
    path('client/<int:client_id>/history/', ClientOrderHistoryView.as_view(), name='client-history'),
    path('client/update-profile/', UpdateProfileView.as_view(), name='update-profile'),
    path('auth/update/', UpdateProfileView.as_view(), name='update-profile'), 
    path('client/addresses/manage/', ManageAddressView.as_view(), name='manage-address'),
    path('menu/favorite/', ManageFavoriteView.as_view(), name='manage-favorite'),
    path('client/<int:client_id>/favorites/', ClientFavoritesView.as_view(), name='client-favorites'),
    path('auth/delete/', DeleteProfileView.as_view(), name='delete-profile'),
    path('cart/manage/', SyncCartItemView.as_view(), name='cart-manage'),
    path('client/<int:client_id>/bonuses/', ClientBonusBalanceView.as_view(), name='client-bonuses'),
    path('client/<int:client_id>/active-orders/', ClientActiveOrdersView.as_view(), name='client-active-orders'),
    path('clients/<int:client_id>/cards/', ClientCardsView.as_view(), name='client-cards'),
    path('clients/cards/manage/', ManageCardView.as_view(), name='manage-card'),
    path('orders/<int:order_id>/details/', OrderDetailsView.as_view(), name='order-details'),
    
    path('orders/<int:order_id>/receipt/', DownloadReceiptView.as_view(), name='download-receipt'),
    path('orders/<int:order_id>/update-status/', UpdateOrderStatusView.as_view(), name='update-order-status'),
]
