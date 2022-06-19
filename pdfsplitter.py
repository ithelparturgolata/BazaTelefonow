from PyPDF2 import PdfFileWriter, PdfFileReader

def splitPDF(fileName, customSplitPages):
    inputpdf = PdfFileReader(open(fileName, "rb"))
    fileNameSplit = fileName.split(".")
    data = []
    count = 0

    for i in range(0,inputpdf.numPages, customSplitPages):
        inputpdf = PdfFileReader(open(fileName, "rb"))
        count+=1
        outputPDF = PdfFileWriter()
        for j in range(customSplitPages):
            page = i+j

            try:
                outputPDF.addPage(inputpdf.getPage(page))
            except:
                break

        outputPDFSource =  open(f"{fileNameSplit[0]}%03i.pdf" % (count), "wb")
        data.append(f"{fileNameSplit[0]}%03i.pdf" % (count))
        outputPDF.write(outputPDFSource)
        outputPDFSource.close()

    return data
