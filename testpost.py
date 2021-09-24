import requests
import metsrw

if __name__ == '__main__':
    file_path_to_send = "C:/Users/Cameron/Documents/01538a96-c96e-4334-ad72-7934a7a22553/data/objects"
    response_text = requests.post(f'http://localhost:5000/mets?filepath={file_path_to_send}')
    print(response_text.text)
    print(response_text.text.encode())

    # mets_text = metsrw.METSDocument.fromstring(response_text.text)  # Creates Value Error
    mets_encoded = metsrw.METSDocument.fromstring(response_text.text.encode())  # Doesn't parse correctly

    print(mets_encoded.tostring())
    mets_encoded.write("test_mets.xml", pretty_print=True)

