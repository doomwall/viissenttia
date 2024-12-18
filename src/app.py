from flask import redirect, render_template, request, flash, send_file
from repositories.citation_repository import get_citations, create_citation
from config import app
from util import citation_data_to_class, get_citation_types, citation_class_to_bibtex_file


@app.route("/")
def index():
    citations = get_citations()
    return render_template("index.html", citations=citations)


@app.route("/add_citation", methods=["POST", "GET"])
def add_citation():
    # Code for displaying add_citation page
    if request.method == "GET":
        return render_template("add_citation.html", citation_types=get_citation_types())
    
    # Code for handling citation form
    if request.method == "POST":
        
        # Turn citation form into a citation class
        citation_class = citation_data_to_class(request.form, True)
        
        # Error handling
        if isinstance(citation_class, str):
            flash(citation_class)
            return redirect("/add_citation")
        if not citation_class:
            flash("Citation type not found.")
            return redirect("/add_citation")
        base_key = citation_class.key
        
        citation_class.key = key_generator(base_key)
        
        # Attempt to create citation and then display result
        result = create_citation(citation_class)
        if result:
            flash("Successfully added citation.")
            return redirect("/add_citation")
        flash("Failed to add citation. Please try again later.")
        return redirect("/add_citation")
    return "Invalid request method", 405


def key_generator(base_key):
        # Finding the maximum suffix for the key
        existing_citations = get_citations()
        existing_keys = {citation.key for citation in existing_citations}
        
        # Suffix generation
        suffix = -1
        new_key = f"{base_key}{suffix}"
        while new_key in existing_keys:
            suffix -= 1
            new_key = f"{base_key}{suffix}"
        
        # Set suffix
        return new_key


@app.route("/download")
def download():
    citations = get_citations()
    citation_class_to_bibtex_file(citations)
    path = "./bibtex_files/citations.bib"
    return send_file(path, as_attachment=True)
