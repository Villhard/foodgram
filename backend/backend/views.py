from django.shortcuts import get_object_or_404, redirect
from rest_framework.decorators import api_view

from api.utils import Base52
from backend.settings import HOST
from recipes.models import Recipe


@api_view(['GET'])
def get_recipe_by_short_link(request, link):
    recipe_id = Base52.from_base52(link)
    get_object_or_404(Recipe, id=recipe_id)
    return redirect(f'{HOST}/recipes/{recipe_id}')
