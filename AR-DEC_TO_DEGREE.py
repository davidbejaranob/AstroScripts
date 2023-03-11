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

os.system("clear")

dir_path = str(
    input(
        "\n" * 2
        + "Enter the URL of the files to convert (default this directory): \n>> "
    )
)
if dir_path == "":
    print("aborting...\n")
    sys.exit()
res = []
types = ("*.fit", "*.fits")  # the tuple of file types
for files in types:
    for f in glob.glob(os.path.join(dir_path, files)):
        res.append(f)
print("\n" * 2 + "Converting files..." + "\n")
with alive_bar(len(res)) as bar:
    for i in res:
        # Open the file header for viewing and load the header
        hdulist = fits.open(i)
        header = hdulist[0].header

        # Print the header keys from the file to the terminal
        # print(header.keys)

        if "flat" in header["OBJECT"].lower():
            path = os.path.join(
                os.path.dirname(i),
                "Flat",
                str(header["CCDXBIN"]) + "x" + str(header["CCDYBIN"]),
                str(header["EXPTIME"]),
                os.path.basename(i),
            )
        elif "dark" in header["OBJECT"].lower():
            path = os.path.join(
                os.path.dirname(i),
                "Dark",
                str(header["CCDXBIN"]) + "x" + str(header["CCDYBIN"]),
                str(header["EXPTIME"]),
                os.path.basename(i),
            )
        elif "bias" in header["OBJECT"].lower():
            path = os.path.join(
                os.path.dirname(i),
                "Bias",
                str(header["CCDXBIN"]) + "x" + str(header["CCDYBIN"]),
                str(header["EXPTIME"]),
                os.path.basename(i),
            )
        else:
            path = os.path.join(
                os.path.dirname(i),
                header["OBJECT"],
                str(header["CCDXBIN"]) + "x" + str(header["CCDYBIN"]),
                str(header["EXPTIME"]),
                os.path.basename(i),
            )
        print(os.path.dirname(path))
        os.makedirs(os.path.dirname(path), exist_ok=True)

        # Modify the key called 'RA' and 'DEC' to have a value in degrees
        try:
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
