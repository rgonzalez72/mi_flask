from flask import Flask, request
import json
import sys
import os
import hashlib
app = Flask(__name__)


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
                            recipe ["hash"] = calculateHash (recipe["name"])
                            recipes.append (recipe)
    return recipes


def recipes_name_select (recipes):
    component = '<form method="GET" action="/recipe">'
    component += '<label for="recipe_names">Select by name: </label>\n'
    component += '<select name="recipe_names" id="names">\n'
    list_of_names = [d["name"] for d in recipes]
    for name in sorted (list_of_names):
        hash_value = calculateHash (name)
        component += '\t<option value="' + hash_value +'">' + name + '</option>\n'
    component += '</select>\n'
    component += '<button type="submit">Ir</button>\n'
    component += '</form>\n'
    return component

@app.route('/')
def main_page ():
    page = '<h2>Consulta recetas</h2>\n'
    recipes = loadRecipes ()

    page += recipes_name_select (recipes)
    return page

def find_recipe (recipes, hash_value):
    recipe = None
    for R in recipes:
        print (R["hash"], hash_value)
        if R["hash"]  == hash_value:
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
    sys.stdout.flush ()
    if recipe is None:
        return "Recipe not found", 404

    page = '<h2>' + recipe["name"] + '</h2>\n'
    page += '<br>\n'
    page += '<a href="/">Volver</a>\n'

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
            page += '<a href="/tag/' + tag + '">' + tag +  "</a>" + " "
        page += "<br>\n"
    page += '<br>\n'
    page += '<a href="/">Volver</a>\n'

    return page

@app.route('/recipes/<hash_value>')
def show_recipe_path (hash_value):
    print ("show_recipe_path: " + hash_value)
    return get_recipe_page (hash_value)

def getRecipesWithTag (recipes, tag_name):
    recipesTag = []
    for R in recipes:
        if tag_name in R["tags"]:
            recipesTag.append (R)
    return recipesTag
    

@app.route ('/tag/<tag_name>')
def show_tag (tag_name):
    recipes = loadRecipes ()
    page = "<h2>Platos con etiqueta: " + tag_name + "</h2>\n"
    recipesTag = getRecipesWithTag (recipes, tag_name)
    page += '<a href="/">Página principal</a>\n'
    page += "<br>\n"

    page += "<UL>\n"
    list_of_names = [d["name"] for d in recipesTag]
    for name in list_of_names:
        hash_value = calculateHash (name)
        page += '\t<li><a href="/recipes/' + hash_value + '">' + name + '</a></li>\n'
    page += "</UL>\n"

    page += '<a href="/">Página principal</a>\n'
    return page


if __name__ == "__main__":
    app.run(debug=True)
