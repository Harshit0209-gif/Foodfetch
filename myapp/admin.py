from django.contrib import admin
from myapp.models import Product, Cart, CartItem
from myapp.models import Contact, Category, Team, Dish, Profile,Order




admin.site.site_header = "FoodFetch | Admin"

class ContactAdmin(admin.ModelAdmin):
    list_display = ['id','name','email','subject','added_on','is_approved']

class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id','name','added_on','updated_on']

class TeamAdmin(admin.ModelAdmin):
    list_display = ['id','name','added_on','updated_on']

class DishAdmin(admin.ModelAdmin):
    list_display = ['id','name','price','added_on','updated_on']


class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'address', 'status')  # Display fields in the admin list view
    list_filter = ('status',)  # Add filters for status field
    search_fields = ('id', 'address')


admin.site.register(Contact, ContactAdmin)
admin.site.register(Category,CategoryAdmin)
admin.site.register(Team, TeamAdmin )
admin.site.register(Dish, DishAdmin )
admin.site.register(Profile)
admin.site.register(Order)
admin.site.register(Product)
admin.site.register(Cart)
admin.site.register(CartItem)