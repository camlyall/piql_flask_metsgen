import os.path
import uuid

from flask import Flask, request
import metsrw

app = Flask(__name__)


def create_mets(directory):
    print(directory)
    mets = metsrw.METSDocument()
    fse = create_fse(directory)
    mets.append(fse)
    mets.write(f"{directory}/METSs.xml", pretty_print=True)
    return mets


def create_fse(directory):
    fse_directory = metsrw.FSEntry(label="test", path="test", type="Directory")
    for file in os.listdir(directory):
        file_path = os.path.join(directory, file).replace('\\', '/')
        if os.path.isdir(file_path):
            fse_directory.children.append(create_fse(file_path))
        else:
            print(file_path)
            fse_file = metsrw.FSEntry(label=file, path=file_path, type="Item", file_uuid=str(uuid.uuid4()))
            fse_directory.children.append(fse_file)
    return fse_directory


@app.route("/mets")
def metsroute():
    file_path = request.args.get("filepath", None)
    if file_path:
        if os.path.isdir(file_path):
            mets = create_mets(file_path.replace('\\', '/'))
            return str(mets.all_files())
        else:
            return "Not a valid directory", 400
    else:
        return "Enter directory", 404


@app.route("/")
def index():
    # index template here
    return "hello"


if __name__ == '__main__':
    app.run(debug=True)
