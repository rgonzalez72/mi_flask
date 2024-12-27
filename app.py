from flask import Flask, request, session, redirect, make_response, send_file, render_template
from flask_session import Session
from fpdf import FPDF
import json
import sys
import os
import hashlib
import re

from .createPdf import PDF

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

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
    if 'r_list' not in session:
        session ['r_list'] = []

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
                            recipe ["selected"] = hashInList (recipe["hash_value"])
                            recipes.append (recipe)
    return recipes


def getListOfIngredients (recipes):
    ingredients = []
    for R in recipes:
        for i in R["ingredients"]:
            i = i.lower()
            if not i in ingredients:
                ingredients.append (i.lower())
    return sorted(ingredients)

def getListOfTags (recipes):
    tags = []
    for R in recipes:
        for i in R["tags"]:
            if not findInList (i, tags):
                tags.append (i.lower())
    return sorted(tags)

def getListSize ():
    if 'r_list' not in session:
        session ['r_list'] = []

    return len(session["r_list"])


@app.route('/')
def main_page ():
    session ['url'] = request.full_path
    recipes = loadRecipes ()
    ing_list = getListOfIngredients (recipes)
    tag_list = getListOfTags (recipes)
    
    return render_template ("index.html", 
            list_size = getListSize (),
            recipes=recipes,
            ingredients=ing_list,
            tags= tag_list)

def find_recipe (recipes, hash_value):
    recipe = None
    for R in recipes:
        if R["hash_value"]  == hash_value:
            recipe = R
            break
    return recipe


@app.route('/recipe')
def show_recipe ():
    session ['url'] = request.full_path
    hash_value = request.args.get("recipe_names")
    recipes = loadRecipes()
    recipe = find_recipe (recipes, hash_value)
    if recipe is None:
        return "Recipe not found", 404

    selected = False 
    if recipeInList (recipe):
        selected = True

    return render_template ("recipe.html",
            list_size = getListSize (),
            recipe = recipe,
            recipe_selected = selected)

def getRecipesWithTag (recipes, tag_name):
    recipesTag = []
    for R in recipes:
        if findInList (tag_name, R["tags"]):
            recipesTag.append (R)
    return recipesTag

@app.route ('/tag')
def show_tag ():
    session ['url'] = request.full_path
    tag_name = request.args.get("tags")
    recipes = loadRecipes ()
    recipesTag = getRecipesWithTag (recipes, tag_name)

    title ="Platos con etiqueta: " + tag_name
    return render_template ("recipe_list.html",
            list_size = getListSize (),
            title = title, 
            recipes = recipesTag)

def getRecipesWithIngredient (recipes, ing):
    recipesIng = []
    for R in recipes:
        if findInList (ing, R["ingredients"]):
            recipesIng.append (R)
    return recipesIng

@app.route ('/ingredient')
def show_ingredient ():
    session ['url'] = request.full_path
    recipes = loadRecipes ()
    ing = request.args.get("ingredients")
    recipesIng =  getRecipesWithIngredient (recipes, ing)

    title = "Platos con ingrediente: " + ing 
    return render_template ("recipe_list.html",
            list_size = getListSize (),
            title = title, 
            recipes = recipesIng)

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
    session ['url'] = request.full_path
    recipes = loadRecipes ()
    term = request.args.get("search_term")
    foundRecipes = findInRecipes (recipes, term)

    title = "Resultado de búsqueda: " + term 
    return render_template ("recipe_list.html",
            list_size = getListSize (),
            title = title, 
            recipes = foundRecipes)

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

@app.route('/reset')
def reset_list ():
    session["r_list"] = []
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
    session ['url'] = request.full_path
    recipes = loadRecipes ()
    recipesInList = getRecipesInList (recipes)

    title = "Mi lista de recetas"
    return render_template ("recipe_list.html",
            list_size = getListSize (),
            title = title, 
            recipes = recipesInList,
            is_my_list = True)

@app.route('/download')
def download_pdf ():
    pdf = PDF ()
    pdf.set_title ('Lista de recetas')
    recipes = loadRecipes ()
    recipesInList = getRecipesInList (recipes)
    index = 1
    for R in recipesInList:
        pdf.add_recipe (index, R)
        index += 1
    pdf.add_shopping_list (recipesInList)
    pdf.output("recetas.pdf")
    return send_file ('recetas.pdf', as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
