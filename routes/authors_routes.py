from flask import *
author_bp=Blueprint("author",__name__)

@author_bp.route("/author-register")
def author_register():

    return render_template("author/author-register.html")
