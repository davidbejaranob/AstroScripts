from astropy.io import fits
from astropy import units as u
from astropy.coordinates import SkyCoord
import glob
from alive_progress import alive_bar
import time
import sys
import os
import shutil
import os
from pathlib import Path
from string import digits

os.system("clear")


def file_new_path(i, header):
    remove_digits = str.maketrans("", "", digits)

    if "flat" in header["OBJECT"].lower():
        replacementStr, object = (
            header["FILTER"]
            .lower()
            .replace("vacio", "")
            .replace(" ", "")
            .replace("+", "")
            .translate(remove_digits)
            + "_f",
            "Flat",
        )
    elif "dark" in header["OBJECT"].lower():
        replacementStr, object = "_d", "Dark"
    elif "bias" in header["OBJECT"].lower():
        replacementStr, object = "_b", "Bias"
    else:
        replacementStr, object = (
            header["FILTER"]
            .lower()
            .replace("vacio", "")
            .replace(" ", "")
            .replace("+", "")
            .translate(remove_digits)
            + "_o",
            header["OBJECT"],
        )

    file_name, file_extension = os.path.splitext(os.path.basename(i))
    file_name = file_name[:-1] + replacementStr
    file = file_name + file_extension
    path = os.path.join(
        os.path.dirname(i),
        object,
        str(header["CCDXBIN"]) + "x" + str(header["CCDYBIN"]),
        file,
    )
    print(os.path.dirname(path))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return path


def get_path():
    dir_path = input("Enter the path to the directory: ")
    if dir_path == "":
        print("aborting...\n")
        sys.exit()
    return dir_path


def objects_menu(keys):
    print(keys)

    print("Select the object you want to process:")
    for i in range(len(keys)):
        print(str(i + 1) + ". " + keys[i])
    print("0. Exit")
    choice = input("Enter your choice [0-9]: ")
    if choice == "":
        print("aborting...\n")
        sys.exit()
    return keys[int(choice) - 1]


"""
for i in range(len(keys)):
        if "flat" in keys[i].lower():
            keys[i] = "Flat"
"""

dir_path = get_path()
res = []
types = ("*.fit", "*.fits")  # the tuple of file types
objects_dictionary = {}
for files in types:
    for f in glob.glob(os.path.join(dir_path, files)):
        hdulist = fits.open(f)
        header = hdulist[0].header
        res.append(f)
        if len(res) == 0:
            print("No files found")
            sys.exit()
        elif header["OBJECT"] not in objects_dictionary:
            objects_dictionary[header["OBJECT"]] = [f]
        else:
            objects_dictionary[header["OBJECT"]].append(f)
        hdulist.close()

choice = objects_menu(list(objects_dictionary.keys()))
res = objects_dictionary[choice]

with alive_bar(len(res)) as bar:
    for i in res:
        # Open the file header for viewing and load the header
        hdulist = fits.open(i)
        header = hdulist[0].header

        path = file_new_path(i, header)

        try:  # Modify the key called 'RA' and 'DEC' to have a value in degrees
            coordinate = SkyCoord(
                header["RA"] + " " + header["DEC"], unit=(u.hourangle, u.deg)
            )
            # print(coordinate.ra.degree)
            # print(coordinate.dec.degree)
            header["RA"] = coordinate.ra.degree
            header["DEC"] = coordinate.dec.degree

            # Save the new file
            hdulist.writeto(path, overwrite=True)
        except:
            os.makedirs(os.path.join(dir_path, "Error"), exist_ok=True)
            print("Error with file: " + i)
            shutil.copyfile(i, os.path.join(dir_path, "Error", os.path.basename(i)))
            pass
        # Make sure to close the file
        hdulist.close()
        bar()

print("\nDone!" + "\n" * 2)
