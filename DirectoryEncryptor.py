from os import listdir
from os.path import isfile, join
from random import randint
import lorem
import os, random, struct
from Crypto.Cipher import AES


class Directory:

    def __init__(self, path):
        self.path = path

    #recover all files of path
    def all_files(self):
        files = []
        for f in listdir(self.path):
            if isfile(join(self.path, f)):
                files.append(join(self.path, f))
        return files

    #recover all crypted files
    def all_files_crypted(self, extension):
        files = []
        for f in listdir(self.path):
            if isfile(join(self.path, f)):
                if f.endswith(extension):
                    files.append(join(self.path, f))
        return files

    # TEST ONLY
    def generate_random_files(self, nb_files):
        for i in range(nb_files):
            filename = "TEST_" + str(i) + ".txt"
            f = open(self.path + "\\" + filename, "w")
            f.write(lorem.text())
            f.close()


class Encryptor:

    def __init__(self, key, chunksizeEncr, chunksizeDecr, extension):
        self.key = key
        self.chunksizeEncr = chunksizeEncr
        self.chunksizeDecr = chunksizeDecr
        self.extension = extension

    #encrypt file with key and iv
    def encrypt_files(self, files):
        for f in files:
            out_filename = f + self.extension
            iv = b'1234567812345678'
            encryptor = AES.new(self.key, AES.MODE_CBC, iv)
            filesize = os.path.getsize(f)

            with open(f, 'rb') as infile:
                with open(out_filename, 'wb') as outfile:
                    outfile.write(struct.pack('<Q', filesize))
                    outfile.write(iv)

                    while True:
                        chunk = infile.read(self.chunksizeEncr)
                        if len(chunk) == 0:
                            break
                        elif len(chunk) % 16 != 0:
                            chunk += b' ' * (16 - len(chunk) % 16)

                        outfile.write(encryptor.encrypt(chunk))
            print(f)
            os.remove(f)
    #decrypt file with key and iv
    #the key is in the first 16 characters of the file
    def decrypt_files(self, files):
        for f in files:
            out_filename = os.path.splitext(f)[0]

            with open(f, 'rb') as infile:
                origsize = struct.unpack('<Q', infile.read(struct.calcsize('Q')))[0]
                iv = infile.read(16)
                decryptor = AES.new(self.key, AES.MODE_CBC, iv)

                with open(out_filename, 'wb') as outfile:
                    while True:
                        chunk = infile.read(self.chunksizeDecr)
                        if len(chunk) == 0:
                            break
                        outfile.write(decryptor.decrypt(chunk))

                    outfile.truncate(origsize)
            print(f)
            os.remove(f)


if __name__ == '__main__':
    d = Directory("TEST/")
    #d = Directory(os.path.dirname(os.path.realpath(__file__)))
    print (str(d.path))
    files = d.all_files()
    c = Encryptor(b"1234567812345678", 64*1024, 24*1024, ".DirectoryEncryptor")
    c.encrypt_files(files)
    files = d.all_files_crypted(".DirectoryEncryptor")
    c.decrypt_files(files)
