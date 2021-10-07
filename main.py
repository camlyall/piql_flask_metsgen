import os.path
import uuid

from flask import Flask, request, render_template
import metsrw
import metsrw.plugins.premisrw as premisrw
from lxml import etree

import metsrw_override

app = Flask(__name__)


def create_fse(directory, metadata, is_root=True):
    """
    Recursive function to create FSEntry tree for IP
    :param dict metadata: Add metadata to relevant FSEntry
    :param bool is_root: Ensure premis dmd only added to root FSEntry
    :param str directory:
    :return FSEntry: Root FSEntry containing all child nodes
    """
    base_directory = os.path.basename(directory)
    fse = metsrw.FSEntry(label=base_directory, type="Directory", file_uuid=str(uuid.uuid4()))
    if is_root:
        fse.add_dmdsec(create_premis_dmdsec(directory), mdtype='PREMIS:OBJECT')

    # Add metadata if present
    if base_directory in metadata.keys():
        fse.add_dublin_core(create_dublincore_dmdsec(metadata[base_directory]))

    for file in os.listdir(directory):
        file_path = os.path.join(directory, file).replace('\\', '/')
        if os.path.isdir(file_path):
            # Avoid adding data directory
            if file == 'data':
                for sub_file in os.listdir(file_path):
                    fse.children.append(create_fse(os.path.join(file_path, sub_file), metadata, is_root=False))
            else:
                fse.children.append(create_fse(file_path, metadata, is_root=False))

        elif '/objects/' in file_path:
            if '/objects/metadata/' in file_path:
                fse_use = "metadata"
            elif '/objects/submissionDocumentation/' in file_path:
                fse_use = "submissionDocumentation"
            else:
                fse_use = "original"
            file_fse = metsrw.FSEntry(use=fse_use, label=file, path=file_path[file_path.index('objects/'):],
                                      type="Item", file_uuid=str(uuid.uuid4()))
            # Add metadata if present
            if file in metadata.keys():
                file_fse.add_dublin_core(create_dublincore_dmdsec(metadata[file]))
            fse.children.append(file_fse)
    return fse


def extract_metadata(directory):
    """
    Extracts the data from compliant metadata.csv in metadata directory
    :param str directory:
    :return dict metadata_dict: in the form {baseDirectory : {title : value, ...} }
    """
    metadata_dict = {}
    if os.path.isfile(directory):
        with open(directory, 'r') as metadata_file:
            keys = metadata_file.readline().strip().split(',')
            for line in metadata_file:
                values = line.strip().split(',')
                base_directory = values[0].split('/')[-1]
                metadata_dict[base_directory] = {}
                for i in range(1, len(keys)):
                    metadata_dict[base_directory][keys[i]] = values[i]
    return metadata_dict


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
    ), premis_version=premisrw.utils.PREMIS_VERSION)

    return premis_data


def create_dublincore_dmdsec(metadata):

    dmd_metadata = '<dcterms:dublincore xmlns:dc="http://purl.org/dc/elements/1.1/" ' \
                   'xmlns:dcterms="http://purl.org/dc/terms/" ' \
                   'xsi:schemaLocation="http://purl.org/dc/terms/ ' \
                   'https://dublincore.org/schemas/xmls/qdc/2008/02/11/dcterms.xsd">'
    for key in metadata:
        dmd_metadata += f"\t<{key}>{metadata[key]}</{key}>\n"
    dmd_metadata += "</dcterms:dublincore>"

    return dmd_metadata


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
            base_directory = os.path.basename(file_path)
            objects_path = os.path.join(file_path, "data", "objects").replace('\\', '/')
            if os.path.isdir(objects_path):

                # Update premis version from 2.2 to 3.0
                premisrw.utils.PREMIS_VERSION = premisrw.utils.PREMIS_3_0_VERSION
                premisrw.utils.NAMESPACES = premisrw.utils.PREMIS_VERSIONS_MAP[premisrw.utils.PREMIS_VERSION]["namespaces"]
                premisrw.utils.PREMIS_META = premisrw.utils.PREMIS_VERSIONS_MAP[premisrw.utils.PREMIS_VERSION]["meta"]
                premisrw.utils.PREMIS_SCHEMA_LOCATION = premisrw.utils.PREMIS_3_0_SCHEMA_LOCATION

                metsrw.METSDocument = metsrw_override.METSDocument
                metsrw.FSEntry = metsrw_override.FSEntry

                mets = metsrw.METSDocument()

                # Find and add Metadata
                metadata = {}
                if os.path.isdir(os.path.join(objects_path, "metadata")):
                    metadata_path = find_metadata_file(os.path.join(objects_path, "metadata"))
                    if metadata_path:
                        metadata = extract_metadata(metadata_path)

                fse = create_fse(file_path, metadata)
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
