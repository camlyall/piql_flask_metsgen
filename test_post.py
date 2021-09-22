import requests
import metsrw

if __name__ == '__main__':
    file_path_to_send = "C:/Users/Cameron/Documents/01538a96-c96e-4334-ad72-7934a7a22553"
    response_text = requests.post(f'http://localhost:5000/mets?filepath={file_path_to_send}')
    #print(type(response_text.text))
    print('response from server:', response_text.text)
    mets = metsrw.METSDocument.fromstring(response_text.text.encode())
    mets.write("METSSY.xml", pretty_print=True)
    
