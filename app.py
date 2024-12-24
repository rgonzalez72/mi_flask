from flask import Flask, request, session, redirect
from flask_session import Session
import json
import sys
import os
import hashlib
import re

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

def getHeader ():

    if 'r_list' not in session:
        session ['r_list'] = []

    component = 'Mi <a href="/my_list">lista</a> tiene ' + str(len(session['r_list'])) + " receta/s.\n"
    component += "</br>\n"
    return component

def recipeInList (recipe):
    return recipe ["hash_value"] in session['r_list']

def hashInList (hash_value):
    return hash_value in session['r_list']

def addToList (hash_value):
    if not hashInList (hash_value):
        session['r_list'].append (hash_value)

def removeFromList (hash_value):
    session['r_list'].remove (hash_value)

def calculateHash (name):
    return hashlib.sha1(name.encode("utf-8")).hexdigest()


def loadRecipes ():
    recipes = []

    recipes_dir = os.path.join (os.path.dirname (__file__), "recipes")

    for root, _, files in os.walk (recipes_dir):
        for name in files:
            if name.endswith (".json"):
                path = os.path.join (root, name)
                with open (path) as fp:
                    list_of_recipes = json.load (fp)
                    for recipe in list_of_recipes:
                        if "name" in recipe and recipe["name"] != "":
                            recipe ["hash_value"] = calculateHash (recipe["name"])
                            recipes.append (recipe)
    return recipes


def recipes_name_select (recipes):
    component = '<form method="GET" action="/recipe">'
    component += '<label for="recipe_names">Seleccionar por nombre(' + str(len(recipes)) + '): </label>\n'
    component += '<select name="recipe_names" id="names">\n'
    list_of_names = [d["name"] for d in recipes]
    for name in sorted (list_of_names):
        hash_value = calculateHash (name)
        component += '\t<option value="' + hash_value +'">' + name + '</option>\n'
    component += '</select>\n'
    component += '<button type="submit">Ir</button>\n'
    component += '</form>\n'
    component += '<br>\n'
    return component

def getListOfIngredients (recipes):
    ingredients = []
    for R in recipes:
        for i in R["ingredients"]:
            if not findInList (i, ingredients):
                ingredients.append (i.lower())
    return sorted(ingredients)

def ingredient_select (recipes):
    ing_list = getListOfIngredients (recipes)
    component = '<form method="GET" action="/ingredient">'
    component += '<label for="ingredients">Seleccionar por ingrediente(' + str(len(ing_list)) + '): </label>\n'
    component += '<select name="ingredients" id="inames">\n'
    for ing in ing_list:
        component += '\t<option value="' + ing + '">' + ing + '</option>\n'
    component += '</select>\n'
    component += '<button type="submit">Ir</button>\n'
    component += '</form>\n'
    component += '<br>\n'
    return component

def getListOfTags (recipes):
    tags = []
    for R in recipes:
        for i in R["tags"]:
            if not findInList (i, tags):
                tags.append (i.lower())
    return sorted(tags)

def tag_select (recipes):
    tag_list = getListOfTags (recipes)
    component = '<form method="GET" action="/tag">'
    component += '<label for="tags">Seleccionar por etiqueta(' + str(len(tag_list)) + '): </label>\n'
    component += '<select name="tags" id="tnames">\n'
    for tag in tag_list:
        component += '\t<option value="' + tag + '">' + tag + '</option>\n'
    component += '</select>\n'
    component += '<button type="submit">Ir</button>\n'
    component += '</form>\n'
    component += '<br>\n'
    return component

def search_area ():
    component = '<form method="GET" action="/search">'
    component += '<label for="search_term">Buscar: </label>\n'
    component += '<input name="search_term" id="snames">\n'
    component += '<button type="submit">Ir</button>\n'
    component += '</form>\n'
    component += '<br>\n'
    return component


@app.route('/')
def main_page ():
    page = getHeader ()
    page += '<h2>Consulta recetas</h2>\n'
    recipes = loadRecipes ()

    page += recipes_name_select (recipes)
    page += ingredient_select (recipes)
    page += tag_select (recipes)
    page += search_area ()
    return page

def find_recipe (recipes, hash_value):
    recipe = None
    for R in recipes:
        if R["hash_value"]  == hash_value:
            recipe = R
            break
    return recipe


@app.route('/recipe')
def show_recipe ():
    hash_value = request.args.get("recipe_names")
    return get_recipe_page (hash_value)

def get_recipe_page (hash_value):
    recipes = loadRecipes()
    recipe = find_recipe (recipes, hash_value)
    if recipe is None:
        return "Recipe not found", 404

    page = getHeader()
    page += '<h2>' + recipe["name"] + '</h2>\n'
    page += '<br>\n'
    page += '<a href="/">Página principal</a>\n'
    page += '<br>\n'

    if recipeInList (recipe):
        page += 'Esta receta está en tu lista. <a href="/remove/' + recipe ["hash_value"] + '">Quitar</a>.'
    else:
        page += 'Esta receta no está en tu lista. <a href="/add/' + recipe ["hash_value"] + '">Añadir</a>.'
    page += '<br>\n'
    session['url'] = request.full_path



    page += '<h3>Ingredientes</h3>\n'
    page += "<UL>\n"
    for ing in recipe["ingredients"]:
        page += "\t<li>" + ing + "</li>\n"
    page += "</UL>\n"

    page += '<h3>Pasos</h3>\n'
    page += "<UL>\n"
    for step in recipe["steps"]:
        page += "\t<li>" + step + "</li>\n"
    page += "</UL>\n"

    if len (recipe["tags"]) > 0:
        page += "Etiquetas: "
        for tag in recipe["tags"]:
            page += '<a href="/tag?tags=' + tag + '">' + tag +  "</a>" + " "
        page += "<br>\n"
    page += '<br>\n'
    page += '<a href="/">Página principal</a>\n'

    return page


def getRecipesWithTag (recipes, tag_name):
    recipesTag = []
    for R in recipes:
        if findInList (tag_name, R["tags"]):
            recipesTag.append (R)
    return recipesTag


def getListOfRecipes(recipes):
    page = '<a href="/">Página principal</a>\n'
    page += "<br>\n"

    page += "<UL>\n"
    list_of_names = [d["name"] for d in recipes]
    for name in sorted(list_of_names):
        hash_value = calculateHash (name)
        
        listStr = ' <a href="/'
        if hashInList (hash_value):
            listStr += 'remove/' + hash_value + '">-'
        else:
            listStr += 'add/' + hash_value + '">+'
        listStr += "</a> "

        # Save the path to redirect back here
        session ['url'] = request.full_path
        
        page += '\t<li><a href="/recipe?recipe_names=' + hash_value + '">' + name + '</a>' + listStr + '</li>\n'
    page += "</UL>\n"

    page += '<a href="/">Página principal</a>\n'
    return page
    

@app.route ('/tag')
def show_tag ():
    tag_name = request.args.get("tags")
    recipes = loadRecipes ()
    page = getHeader()
    page += "<h2>Platos con etiqueta: " + tag_name + "</h2>\n"
    recipesTag = getRecipesWithTag (recipes, tag_name)
    page += getListOfRecipes (recipesTag)
    return page

def getRecipesWithIngredient (recipes, ing):
    recipesIng = []
    for R in recipes:
        if findInList (ing, R["ingredients"]):
            recipesIng.append (R)
    return recipesIng

@app.route ('/ingredient')
def show_ingredient ():
    recipes = loadRecipes ()
    ing = request.args.get("ingredients")
    page = getHeader ()
    page += "<h2>Platos con ingrediente: " + ing + "</h2>\n"
    recipesIng =  getRecipesWithIngredient (recipes, ing)
    page += getListOfRecipes (recipesIng)
    return page

def normalizeString (string):
    fromStr = "áéíóúÁÉÍÓÚüÜ"
    toStr = "aeiouaeiouuu"
    trans = str.maketrans(fromStr, toStr)
    return string.casefold().translate(trans)

def findInList (term, listOfTerms):
    """ Find is case insensitive. """
    found = False
    term = normalizeString (term)
    for t in listOfTerms:
        if normalizeString(term) in normalizeString(t):
            found = True
            break
    return found

def findInRecipes (recipes, term):
    foundRecipes = []

    for R in recipes:
        if normalizeString (term) in normalizeString(R["name"]):
            foundRecipes.append (R)
            continue

        if findInList (term, R["ingredients"]):
            foundRecipes.append (R)
            continue

        if findInList (term, R["steps"]):
            foundRecipes.append (R)
            continue

    return foundRecipes

@app.route ('/search')
def search_term ():
    recipes = loadRecipes ()
    term = request.args.get("search_term")
    foundRecipes = findInRecipes (recipes, term)
    page = getHeader ()
    page += "<h2>Resultado de búsqueda: " + term + "</h2>\n"
    if len(foundRecipes) > 0:
        page += getListOfRecipes (foundRecipes)

    else:
        page += "No he encontrado ninguna receta. "
        page += '<br>\n'
        page += '<a href="/">Página principal</a>\n'
    
    return page

@app.route('/add/<hash_value>')
def add_to_list (hash_value):
    addToList (hash_value)
    if 'url' in session:
        return (redirect (session['url']))
    return (redirect ('/'))

@app.route('/remove/<hash_value>')
def remove_from_list (hash_value):
    removeFromList (hash_value)
    if 'url' in session:
        return (redirect (session['url']))
    return (redirect ('/'))

def getRecipesInList (recipes):
    recipesInList = []

    for R in recipes:
        if R["hash_value"] in session["r_list"]:
            recipesInList.append (R)


    return recipesInList

@app.route('/my_list')
def my_list ():
    recipes = loadRecipes ()
    recipesInList = getRecipesInList (recipes)
    page = getHeader()
    page += "<h2>Mi list de recetas</h2>\n"
    page += getListOfRecipes (recipesInList)
    return page

if __name__ == "__main__":
    app.run(debug=True)
