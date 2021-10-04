import os.path
import uuid

from flask import Flask, request, render_template
import metsrw
import metsrw.plugins.premisrw as premisrw

app = Flask(__name__)


def create_fse(directory):
    fse_directory = metsrw.FSEntry(label=os.path.basename(directory), path="test", type="Directory", file_uuid=str(uuid.uuid4()))
    for file in os.listdir(directory):
        file_path = os.path.join(directory, file).replace('\\', '/')
        if os.path.isdir(file_path):
            fse_directory.children.append(create_fse(file_path))
        else:
            fse_file = metsrw.FSEntry(label=file, path=file_path, type="Item", file_uuid=str(uuid.uuid4()))
            fse_directory.children.append(fse_file)
    return fse_directory


def extract_metadata(directory):
    results = []
    with open(directory, 'r') as metadata_file:
        for line in metadata_file:
            data = line.strip().split(',')
            results.append((data[0], data[1:]))
    return results


def create_premis_dmdsec(directory):
    root_directory_name = os.path.basename(directory)

    premis_data = premisrw.premis.data_to_premis((
        'object',
        premisrw.premis.utils.PREMIS_META,
        (
            'object_identifier',
            ('object_identifier_type', 'UUID'),
            ('object_identifier_value', str(uuid.uuid4())),
        ),
        (
            ('original_name', root_directory_name)
        )
    ))
    return premis_data


def create_dublincore_dmdsec(directory):
    return


def add_dublinecore_dmdsec(fse, headers, metadata):
    dmd_metadata = '<dcterms:dublincore xmlns:dc="http://purl.org/dc/elements/1.1/" ' \
                   'xmlns:dcterms="http://purl.org/dc/terms/">\n'
    # 'xsi:schemaLocation="https://dublincore.org/schemas/xmls/qdc/2008/02/11/dcterms.xsd">\n'
    for i in range(len(headers[1])):
        current_header = headers[1][i]
        current_value = metadata[1][i]
        dmd_metadata += f"\t<{current_header}>{current_value}</{current_header}>\n"
    dmd_metadata += "</dcterms:dublincore>"

    fse.add_dublin_core(dmd_metadata)
    return fse


def find_metadata_file(directory):
    for file in os.listdir(directory):
        file_directory = os.path.join(directory, file)
        if os.path.isdir(file_directory):
            find_metadata_file(file_directory)
        elif file == "metadata.csv":
            return os.path.join(directory, "metadata.csv")
    return None


@app.route("/mets", methods=["POST"])
def metsroute():
    file_path = request.args.get("filepath", None)
    if file_path:
        if os.path.isdir(file_path):
            root_directory_name = os.path.basename(file_path)
            objects_path = os.path.join(file_path, "data", "objects").replace('\\', '/')
            if os.path.isdir(objects_path):

                mets = metsrw.METSDocument()
                fse = create_fse(objects_path)

                fse.add_dmdsec(create_premis_dmdsec(file_path), mdtype='PREMIS:OBJECT')

                # Find and add Metadata
                metadata_path = find_metadata_file(os.path.join(objects_path, "metadata"))
                if metadata_path:
                    metadata = extract_metadata(metadata_path)
                    if len(metadata) > 1:
                        for line in metadata[1:]:
                            fse = add_dublinecore_dmdsec(fse, metadata[0], line)
                    else:
                        print("No metadata in file")
                else:
                    print("No metadata file")

                mets.append(fse)

                return mets.tostring(), 201, {'Content-Type': 'application/xml; charset=utf-8'}
            else:
                return "Not a valid directory", 400
        else:
            return "Not a directory", 400
    else:
        return "Enter directory", 404


@app.route("/")
def index():
    # index template here
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
