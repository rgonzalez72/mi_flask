from fpdf import FPDF

title = 'Lista de recetas'

class PDF(FPDF):
    def header(self):
        # Arial bold 15
        self.set_font('Arial', 'B', 15)
        # Calculate width of title and position
        w = self.get_string_width(title) + 6
        self.set_x((210 - w) / 2)

        # Colors of frame, background and text
        self.set_draw_color(0, 0, 0)
        self.set_fill_color(255, 255, 255)
        self.set_text_color(0, 0, 0)
        # Thickness of frame (1 mm)
        self.set_line_width(1)
        # Title
        self.cell(w, 9, title, 1, 1, 'C', 1)
        # Line break
        self.ln(10)

    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        # Arial italic 8
        self.set_font('Arial', 'I', 8)
        # Text color in gray
        self.set_text_color(128)
        # Page number
        self.cell(0, 10, 'Página ' + str(self.page_no()), 0, 0, 'C')

    def recipe_title (self, num, label):
        # Arial 12
        self.set_font('Arial', 'B', 12)
        # Background color
        self.set_fill_color(255, 255, 255)
        # Title
        self.cell(0, 6, 'Receta %d: %s' % (num, label), 0, 1, 'L', 1)
        # Line break
        self.ln(4)

    def recipe_ingredients (self, ingredients):
        self.set_font('Times', 'B', 12)
        # Output justified text
        self.cell(0, 5, "Ingredientes:")
        self.ln(5)

        self.set_font('Times', '', 12)
        for i in  ingredients:
            self.cell (0, 5, i)
            self.ln()
        self.ln(2)

    def recipe_steps (self, steps):
        self.set_font('Times', 'B', 12)
        # Output justified text
        self.cell(0, 5, "Steps:")
        self.ln(5)

        self.set_font('Times', '', 12)
        for i in  steps:
            self.multi_cell (0, 5, i)
            self.ln()

    def chapter_body(self, txt):
        # Times 12
        self.set_font('Times', 'B', 12)
        # Output justified text
        self.multi_cell(0, 5, txt)
        # Line break
        self.ln()
        # Mention in italics
        self.set_font('', 'I')
        self.cell(0, 5, '(end of excerpt)')

    def print_chapter(self, num, title, txt):
        self.add_page()
        self.recipe_title (num, title)
        self.chapter_body(txt)

    def add_recipe (self, num, recipe):
        self.add_page()
        self.recipe_title (num, recipe["name"])
        self.recipe_ingredients (recipe["ingredients"])
        self.recipe_steps (recipe["steps"])

    def ingredients_title (self):
        # Arial 12
        self.set_font('Arial', 'B', 12)
        # Background color
        self.set_fill_color(255, 255, 255)
        # Title
        self.cell(0, 6, 'Lista de la compra', 0, 1, 'L', 1)
        # Line break
        self.ln(4)

    def add_shopping_items (self, ing_list):
        self.set_font('Times', '', 12)
        for i in  ing_list:
            self.cell (0, 5, i)
            self.ln()
        self.ln(2)

    def add_shopping_list (self, recipes):
        self.add_page()
        self.ingredients_title ()
        ing_list = set ()
        for R in recipes:
            for i in R["ingredients"]:
                ing_list.add (i.lower())
        ing_list = sorted(list(ing_list))
        self.add_shopping_items(ing_list)
