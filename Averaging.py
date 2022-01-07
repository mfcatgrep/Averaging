import matplotlib.pyplot as plt
import numpy as np
import logging
import imghdr
import sys
import os


def run_verification(imageslist):
    logging.info("[VERIFICATION] Checking images")
    if len(imageslist) > 0:
        logging.info("[VERIFICATION] Opening the first image "+imageslist[0])
        img=plt.imread(imageslist[0])
        first_shape=img.shape
        for image in imageslist[1:]:
            logging.info("[VERIFICATION] Opening image "+imageslist[0])
            aux_image=plt.imread(image)
            logging.info("[VERIFICATION] Comparing shape "+imageslist[0]+" against "+image)
            if first_shape != aux_image.shape:
                logging.error("[VERIFICATION] The shapes of "+imageslist[0]+" is different than shape of "+image+" "+str(first_shape)+" is different than "+str(aux_image.shape))
                return False
    else:
        logging.error("[VERIFICATION] There are not images")
        return False
    logging.info("[VERIFICATION] Images has the same shape. All good")
    return True

def openImage(imagepath):
    #Due to imread returns in a different way png images, we need to adapt the images
    #to work with them in the same way. For this reason we made openImage function
    openedimage=None
    imagetype=imghdr.what(imagepath)
    if imagetype=="png":
        openedimage=plt.imread(imagepath)*255
        openedimage=openedimage.astype(int)
    else:
        openedimage=plt.imread(imagepath).astype(int)

    return openedimage

def run_core(imageslist,progressbar):
    logging.info("[CORE] Calculating average")
    if len(imageslist) > 0:
         currentimage=1
         logging.info("[CORE] Opening the first image "+imageslist[0])
         destiny=openImage(imageslist[0])

         if progressbar is None:
             showProgress(currentimage,len(imageslist))
         else:
             progressbar.showProgress(currentimage,len(imageslist))

         for image in imageslist[1:]:
            currentimage=currentimage+1
            logging.info("[CORE] Adding the image (stacking)"+image)
            destiny=destiny+openImage(image)

            if progressbar is None:
                showProgress(currentimage,len(imageslist))
            else:
                progressbar.showProgress(currentimage,len(imageslist))

         logging.info("[CORE] Returning  average. All good")
         return (destiny/len(imageslist)).astype("uint8")
    else:
        logging.error("[CORE] There are no images")
        return None

def showProgress(current,total):
    percentage=(int) ((current*100)/total)
    print("\rProgess: "+str(percentage)+"%",end="")
    if(percentage==100):
        print("")

def getFilesFromFolder(path):
    logging.info("[GETFILESFROMFOLDER] Getting files from folder")
    images=list()
    if os.path.isfile(path) == False:
        if os.path.exists(path) == True:
            for element in os.listdir(path):
                logging.info("[GETFILESFROMFOLDER] Checking "+element)
                fullpath=os.path.join(path,element)
                if os.path.isfile(fullpath) == True:
                    imagetype=imghdr.what(fullpath)
                    if imagetype == "bmp" or imagetype == "jpeg" or imagetype == "png" :
                        images.append(fullpath)
                    else:
                        logging.info("[GETFILESFROMFOLDER] Discarting "+element+". Image type not supported")
                else:
                    logging.info("[GETFILESFROMFOLDER] Discarting "+element+". Is a folder")

        else:
            logging.error("[GETFILESFROMFOLDER] The folder doesn't exists")
            return list()
    else:
        logging.error("[GETFILESFROMFOLDER] The folder is a file")
        return list()

    logging.info("[GETFILESFROMFOLDER] Returning images found. All good")
    return images


def checkImageType(imagelist):
    logging.info("[CHECKINGIMGETYPE] Checking image types")
    for element in imagelist:
        imagetype=imghdr.what(element)
        logging.info("[CHECKIMAGETYPE] Checking "+element)
        if imagetype != "bmp" and imagetype != "jpeg" and imagetype != "png" :
            imagelist.remove(element)
            logging.info("[CHECKIMAGETYPE] Removing "+element+". Image type not supported")

    return imagelist


def outputResult(option,result):
    if option=="show" :
        logging.info("[OUTPUTRESULT] Showing result")
        plt.imshow(result)
        plt.axis("off")
        plt.show()
    else:
        logging.info("[OUTPUTRESULT] Saving result "+option)
        plt.imsave(option,result)



def checkOptions(arguments):
    if len(arguments) != 3:
        return False
    else:
        for argument in arguments[1:]:
            if argument.startswith("--folder=") == False and argument.startswith("--output=") == False and argument.startswith("--files=")==False:
                return False
    return True

def help(name):
    print("")
    print(name)
    print("")
    print("Usage: "+name+ "[SOURCE] [OUTPUT]")
    print("Average a group of images to avoid random noise")
    print("")
    print("Sources")
    print("")
    print("--folder=<folder>")
    print("--files=<file1.png,file2.png>")
    print("")
    print("Output")
    print("--output=show Show the output in a window")
    print("--output=<outputfile> Export the result image to outputfile")
    print("")
    print("Example")
    print(name+" --folder=/home/user/photos --output=show")
    print(name+" --files=/home/user/image1.png,/home/user/image3.png,/home/user/image3.png --output=output.png")
    print("")
    return True

def convertOptions(arguments):
    argumentsmap=dict()

    for argument in arguments:
        if argument.startswith("--folder="):
            argumentsmap["folder"]=argument[9:]
        if argument.startswith("--files="):
            argumentsmap["files"]=argument[8:]
        if argument.startswith("--help="):
            argumentsmap["help"]=""
        if argument.startswith("--output="):
            argumentsmap["output"]=argument[9:]

    return argumentsmap


def main(arguments):
    logging.basicConfig(filename="Average.log",level=logging.INFO)
    images=list();

    if checkOptions(arguments) == True:


        args=convertOptions(arguments)

        if "help" in args:
            help(arguments[0])
            return 0

        if "folder" in args:
            images=getFilesFromFolder(args["folder"])

        if "files" in args:
            splittedimages=args["files"].split(",")
            images=checkImageType(splittedimages)

        if run_verification(images):
            result=run_core(images,None)
            outputResult(args["output"],result)
            return 0

        else:
            print("An error happened in image verification. Check Average.log")
            return 2
    else:
        help(sys.argv[0])
        return 1


if __name__ == "__main__":
    value=main(sys.argv)
    sys.exit(value)


