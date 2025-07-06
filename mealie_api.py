#!/usr/bin/env python3
"""A simple customized Mealie API wrapper.

Requires:
  - mealie.key
  - openai.key
  - domain.txt
  - group.txt

"""
#pylint: disable=line-too-long

import json
import requests
from openai import OpenAI

# pull in the mealie API key
with open('mealie.key', 'r', encoding='utf8') as ifile:
    MEALIE_API_KEY=ifile.read().strip()
HEADERS = {'Authorization': f'Bearer {MEALIE_API_KEY}'}

# pull in the openai API key
with open('openai.key', 'r', encoding='utf8') as ifile:
    OPENAI_API_KEY=ifile.read().strip()
client = OpenAI(api_key=OPENAI_API_KEY)

# load the domain
with open('domain.txt', 'r', encoding='utf8') as ifile:
    DOMAIN=ifile.read().strip()
PRE = f'https://{DOMAIN}/api/'

with open('group.txt', 'r', encoding='utf8') as ifile:
    GROUP=ifile.read().strip()


def get_(uri):
    """Get json from the given URI."""
    response = requests.get(PRE + uri, headers=HEADERS, timeout=(3, 10))

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the response JSON and do something with it
        r = response.json()
    else:
        raise ValueError(f'Failed to connect to Mealie API: {response.status_code}')
    return r

def set_(uri, jsondata):
    """Set json at the given URI."""
    response = requests.put(PRE + uri, json=jsondata, headers=HEADERS, timeout=(3, 10))

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the response JSON and do something with it
        r = response.json()
    else:
        print(f'Failed to connect to Mealie API: {response.status_code}')
        raise ValueError
    return r

def get_slugs():
    """Return all recipe slugs (disable pagination)."""
    return [i['slug'] for i in get_('recipes?perPage=-1')['items']]

def get_base_recipes():
    """Return all basic recipes (no extra details.)."""
    return get_('recipes?perPage=-1')['items']

def get_full_recipes():
    """Return all fully detailed recipes."""
    return [get_recipe(i) for i in get_slugs()]

def get_recipes():
    """Return all fully detailed recipes."""
    return get_full_recipes()

def get_recipe(slug):
    """Return a fully detailed recipe."""
    return Recipe(get_('recipes/' + slug))

def with_(recipes, ingredient, exact=False):
    """Filter to recipes with a given ingredient (exact food name)."""
    out = []
    for r in recipes:
        ingredients = [i['food']['name'] for i in r['recipeIngredient']]
        if exact:
            if ingredient in ingredients:
                out.append(r)
        else:
            for food in ingredients:
                if ingredient in food:
                    out.append(r)
    return out

def without_(recipes, ingredient, exact=False):
    """Filter to recipes without a given ingredient (exact food name)."""
    out = []
    for r in recipes:
        try:
            ingredients = [i['food']['name'] for i in r['recipeIngredient']]
        except TypeError:
            print(r)
        if exact:
            if not ingredient in ingredients:
                out.append(r)
        else:
            if all(ingredient not in food for food in ingredients):
                out.append(r)
    return out

def recipes_w_category_slug(slug='mixed-drink', recipes=None):
    """Filter to recipes with a given category (category slug)."""
    if not recipes:
        recipes = get_base_recipes()
    out = []
    for i in recipes:
        if slug in [j['slug'] for j in i['recipeCategory']]:
            out.append(i)
    return out

def recipes_wo_category_slug(slug='mixed-drink', recipes=None):
    """Filter to recipes without a given category (category slug)."""
    if not recipes:
        recipes = get_base_recipes()
    out = []
    for i in recipes:
        if slug not in [j['slug'] for j in i['recipeCategory']]:
            out.append(i)
    return out

def recipes_w_undefined_ingredients(recipes=None):
    """Return problem recipes with ingredients that are undefined."""
    if not recipes:
        recipes = get_recipes()
    return [i for i in recipes if i['recipeIngredient'][0]['unit'] is None]

def recipes_w_disableamount_set(recipes=None):
    """Return recipes with disabled ingredient amounts."""
    if not recipes:
        recipes = get_recipes()
    return [i for i in recipes if i['settings']['disableAmount']]

def recipes_w_no_tags(recipes=None):
    """Filter recipes to those with zero tags."""
    if not recipes:
        recipes = get_base_recipes()
    return [i for i in recipes if not i['tags'] and not 'mixed drinks' in i['recipeCategory']]

def recipes_non_drink_wo_tags():
    """Retrieve all non-drinks that have no tags."""
    return recipes_wo_category_slug('drink', recipes_wo_category_slug('mixed-drink', recipes_w_no_tags()))

def recipes_without_ingredient_names(recipes=None):
    """Filter recipes to those that have missing ingredient names."""
    if not recipes:
        recipes = get_full_recipes()
    out = []
    for r in recipes:
        try:
            [i['food']['name'] for i in r['recipeIngredient']]
        except TypeError:
            out.append(r)
    return out

def recipes_without_ingredient_units(recipes=None):
    """Filter recipes to those that have missing ingredient amount units."""
    if not recipes:
        recipes = get_full_recipes()
    out = []
    for r in recipes:
        try:
            [i['unit']['name'] for i in r['recipeIngredient']]
        except TypeError:
            out.append(r)
    return out

def set_descriptions():
    '''Find empty descriptions and populate with results from an AI prompt

    "Please read the recipe hosted at each of the links provided and generate a Python dictionary mapping each URL slug to a concise description. Each description should be one or two sentences, focusing on what makes the dish unique or appealing. Be precise and keep it short."

    '''
    recipe_base = f'https://{DOMAIN}/g/{GROUP}/r/'
    r = get_recipes()
    no_desc = [i for i in r if not i['description']]
    for i in no_desc:
        print(recipe_base + i['slug'])

    #descripts={
    #    "dark-chocolate-raspberry-chia-banana-bread": "A moist and rich banana bread infused with dark chocolate, juicy raspberries, and nutrient-packed chia seeds.",
    #    "sushi-rice": "Perfectly seasoned short-grain rice, essential for authentic sushi, with a balance of vinegar, sugar, and salt.",
    #    "dolmades-stuffed-grape-leaves": "Tender grape leaves filled with a savory mixture of rice, herbs, and sometimes meat, a classic Mediterranean appetizer."}
    #for slug, desc in descripts.items():
    #    m.Recipe(slug)['description'] = desc


class Recipe:
    """A Mealie json recipe."""
    def __init__(self, slugorjson):
        if isinstance(slugorjson, str):
            self.j = get_recipe(slugorjson).j
        else:
            self.j = slugorjson

    def __getitem__(self, k):
        return self.j[k]

    def __setitem__(self, k, v):
        self.j[k] = v
        set_(f'recipes/{self.j["slug"]}', self.j)

    def __repr__(self):
        return self.j.__repr__()

    @property
    def slug(self):
        """Return the recipe's slug (common)."""
        return self.j['slug']

    @property
    def recipe_calories(self):
        """Return the recipe's calories (common)."""
        return float(self.j['nutrition']['calories'])

    @property
    def calories(self):
        """Return the recipe's calories (common)."""
        return self.recipe_calories

    @property
    def categories(self):
        """Return the recipe's category names (common)."""
        return [i['slug'] for i in self.j['recipeCategory']]

    @property
    def tags(self):
        """Return the recipe's tag names (common)."""
        return [i['slug'] for i in self.j['tags']]

    @property
    def tools(self):
        """Return the recipe's tool names (common)."""
        return [i['slug'] for i in self.j['tools']]

    @property
    def servings(self):
        """Return the recipe's servings (common)."""
        srv = float(self.j.get('recipeServings', 1))
        if srv == 0:
            print(f'problem with recipe, zero servings: {self.j.slug}')
        return srv

    @property
    def calorie_density(self):
        """Return the number of calories per serving."""
        return self.recipe_calories / self.servings

    @property
    def url(self):
        """Return the recipe url."""
        return f'https://{DOMAIN}/g/{GROUP}/r/{self.slug}'

    def set_description(self, dry_run=True):
        """
        Connects to the ChatGPT API to fetch a concise description of the recipe at the given URL.

        Prompt:
        "Please read the recipe hosted at each of the links provided and generate a Python dictionary mapping each URL slug to a concise description.
         Each description should be one or two sentences, focusing on what makes the dish unique or appealing. Be precise and keep it short."

        Args:
            dry_run (bool): Actually set or just retrieve and print the new description
        """
        prompt = f"""
                  Please parse the json Mealie recipe attached and return a concise, appealing description of it.
                  Return a json object mapping the slug to the description.

                  Format your response exactly like:
                  {{
                    "{self.slug}": "Your one- or two-sentence description here."
                  }}

                  recipe: {self.j}
                  """

        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that summarizes recipes concisely."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )

            content = response.choices[0].message.content
            result_dict = json.loads(content)
            if self.slug in result_dict:
                if not dry_run:
                    self['description'] = result_dict[self.slug]
                else:
                    print(result_dict[self.slug])
            else:
                print(f"Slug '{self.slug}' not found in response: {result_dict}")
        except (json.JSONDecodeError, AttributeError, IndexError, TypeError) as parse_err:
            print(f"Failed to parse OpenAI response:\n{content}\nError: {parse_err}")

def print_calorie_density_sorted(recipes):
    """Print a table of recipes, sorted by calorie density."""
    for i in sorted(recipes, key=lambda x: x.calorie_density, reverse=True):
        # throw away cocktails
        if 'drink' in i.categories or 'mixed-drink' in i.categories:
            continue
        print(f'{i.calories:6.0f} {i.calorie_density:5.0f} {i.servings:4.1f} {i.slug}')

def print_sat_fat_per_serving_sorted(recipes):
    """Print a table of recipes, sorted by saturated fat content."""
    for i in sorted(recipes, key=lambda x:float(x['nutrition']['saturatedFatContent'])/float(x['recipeServings']), reverse=True):
        # throw away cocktails
        if 'drink' in i.categories or 'mixed-drink' in i.categories:
            continue
        print("{float(i['nutrition']['saturatedFatContent'])/float(i['recipeServings']):6.0f} {i.calorie_density:5.0f} {i.servings:4.1f} {i.slug}")

if __name__ == '__main__':
    pass
    #r = get_base_recipes()

    #r = get_recipes()
    #print_sat_fat_per_serving_sorted(r)
    #print(without_(r, 'lime', exact=False))

    # filter down recipes by what ingredients they have and don't have
    #r = get_full_recipes()
    #l = with_(without_(r, 'sugar'), 'butter')

    #for i in r:
        #print(i)

    #for i in recipes_non_drink_wo_tags():
        #print(i['slug'])
    #for i in recipes_w_undefined_ingredients():
        #print(i)
    #for i in get_slugs_w_undefined_ingredients():
        #print(i)

    #recipes_non_drink_wo_tags()
    #recipes_wo_category_slug(slug='mixed-drink')
    #recipes_w_category_slug(slug='mixed-drink')
    #recipes_w_no_tags()
    #recipes_w_disableamount_set()
    #recipes_w_undefined_ingredients()
    #get_recipes()
    #get_full_recipes()
    #get_base_recipes()
    #get_slugs()
    #get_recipe(slug)

    # recipes_without_ingredient_names(recipes=None)
    # recipes_without_ingredient_units(recipes=None)

    #drinks=[i for i in r if any(['drink' in j['name'].lower() for j in i['recipeCategory']])]
    #without_(without_(without_(drinks, 'lime'), 'lemon'), 'champagne')

    #set_descriptions()
