#! python3
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# EncryptPDF.py - Encrypt a PDF file to avoid changing by someone.
#                 Add a random owner password to PDF file.
# Created by: Meng Yuxin
# Created on: 24/12/2017
#-------------------------------------------------------------------------------
"""
Reference:
    http://www.python.org
    https://docs.python.org/3/
    http://pythonhosted.org/PyPDF2/
    https://github.com/mstamy2/PyPDF2
    https://github.com/mengyuxin/EncryptPDF
    https://pypi.python.org/pypi/PyPDF2/1.26.0
    
PyPDF2 is a pure-python PDF library capable of splitting, merging together, cropping, and transforming the pages of PDF files. 
It can also add custom data, viewing options, and passwords to PDF files. 
It can retrieve text and metadata from PDFs as well as merge entire files together.
"""
import PyPDF2
import os
import random
import logging
import argparse

logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(levelname)s - %(message)s')
logging.disable(logging.CRITICAL)

def set_password(input_file, owner_pass):
    """
    Function creates new temporary pdf file with same content,
    assigns given password to pdf and rename it with original file.
    temporary output file with name same as input file but prepended
     by "encrypted_", inside same direcory as input file.
    """
    path, filename = os.path.split(input_file)
    output_file = os.path.join(path, "encrypted_" + filename)

    output = PyPDF2.PdfFileWriter()

    input_stream = PyPDF2.PdfFileReader(open(input_file, "rb"))

    for i in range(0, input_stream.getNumPages()):
        output.addPage(input_stream.getPage(i))

    #try:
    #    outputStream = open(output_file, "wb")
    #except PermissionError:
    #    raise Exception("[Errno 13] Permission denied: '%s'" % (output_file))
    outputStream = open(output_file, "wb")

    """/
    encrypt(user_pwd, owner_pwd=None, use_128bit=True)
    Encrypt this PDF file with the PDF Standard encryption handler.

    Parameters:	
        user_pwd (str) – The “user password”, which allows for opening and reading the PDF file with the restrictions provided.
        owner_pwd (str) – The “owner password”, which allows for opening the PDF files without any restrictions. By default, the owner password is the same as the user password.
        use_128bit (bool) – flag as to whether to use 128bit encryption. When false, 40bit encryption will be used. By default, this flag is on.
    """
    # Set owner password to pdf file
    output.encrypt('', owner_pass, use_128bit=True)
    
    output.write(outputStream)
    outputStream.close()

def get_password():
    text_string = '1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()'
    password = ''.join(random.sample(text_string, 32))
    logging.info("Password = '%s'" % password)
    return password

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input_pdf', required=True, help='Input PDF file')
    args = parser.parse_args()
    set_password(args.input_pdf, get_password())

if __name__ == "__main__":
    main()
