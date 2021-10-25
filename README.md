# Piql Flask Metsgen

This project facilitates the generation of compliant METS.xml files for Information Packages

## Usage

`python3 main.py`

This will start the Flask application

A valid http request can be made using software such as Postman.\
Example using the sample input in repository:\
POST http://`[YOUR-IP]`:5005/mets?filepath=sample_input/01538a96-c96e-4334-ad72-7934a7a22553

## Dependencies

metsrw
	- `pip install metsrw`

flask
	- `pip install flask`
	
## Contributing
This project is a work in progress.
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.