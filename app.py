from flask import Flask, render_template, request
from Task5.vector_search import VectorSearchEngine

app = Flask(__name__)

# создаем движок один раз при запуске
engine = VectorSearchEngine("Task4/tf_idf_lemmas")


@app.route("/", methods=["GET", "POST"])
def index():

    results = []
    query = ""

    if request.method == "POST":
        query = request.form["query"]
        results = engine.search(query, top_k=10)

    return render_template("index.html",
                           results=results,
                           query=query)


if __name__ == "__main__":
    app.run(debug=True)