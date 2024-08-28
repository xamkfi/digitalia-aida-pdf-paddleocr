#!/usr/bin/env python
# coding: utf-8

# In[1]:


#from PIL import Image
from paddleocr import PaddleOCR
import magic
import numpy as np
#from tqdm import tqdm
import gradio as gr
import os
import PIL
from PIL import Image
from pdf2image import convert_from_path
from numpy import asarray
from cpugpupicker import cpugpupicker

import pdfplumber
import fitz

model_path = './models'

picker = cpugpupicker()
device = picker.getCPUorGPU()
print("Using device: {}".format(device))

if (device =="cuda"):
    ocr = PaddleOCR(lang='latin', det=True, use_angle_cls=True, rec_model_dir=model_path, show_log=False, use_space_char=True, use_gpu=True,use_tensorrt=True)
else:
    ocr = PaddleOCR(lang='latin', det=True, use_angle_cls=True, rec_model_dir=model_path, show_log=True, use_space_char=True, use_tensorrt=True)


def createFinalPDF(images, pdfPath):    
    print("Creating final PDF {}".format(pdfPath))
    images[0].save(pdfPath, 'PDF', resolution=200, save_all=True, append_images=images[1:])


def pdfToImages(pdfpath):
    images = convert_from_path(pdfpath, dpi=200) #REturn PIL images
    return images
        
def getPDFText(pdfpath):
    completeText = ""    
    with pdfplumber.open(pdfpath) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            completeText+=text
    print ("ORIGINAL TEXT = {}".format(completeText))
    return completeText
    
def handleImage(imageFiles):
    #If image try to ocr
    plaintextResponse = ""    
    boxedImages = []
    for oneImage in imageFiles:
        numpyData = asarray(oneImage)
        outputimage = oneImage        
        #print("Image {} opened".format(outputimage))
        draw = PIL.ImageDraw.Draw(outputimage)
        res = ocr.ocr(numpyData)        
        try:
            for i in res[0]:            
                text = i[1][0]            
                plaintextResponse+="{}\n".format(text) 
                box = np.array(i[0]).astype(np.int32)
                #box = i[0]                
                acc = float(i[1][1])
                #print(box)
                xmin = min(box[:, 0])
                ymin = min(box[:, 1])
                xmax = max(box[:, 0])
                ymax = max(box[:, 1])
                #print(acc)
                if acc > 0.95:
                    draw.rectangle((xmin, ymin, xmax, ymax), outline="green", width=3)
                elif 0.85 < acc <=0.95:
                    draw.rectangle((xmin, ymin, xmax, ymax), outline="yellow", width=3)
                elif 0.75 < acc <=0.85:
                    draw.rectangle((xmin, ymin, xmax, ymax), outline="orange", width=3)
                else:
                    draw.rectangle((xmin, ymin, xmax, ymax), outline="red", width=3)
            boxedImages.append(outputimage)
        except Exception:        
            gr.Info("Ei tunnistettua tekstiä kuvassa")
            pass

        
        #print("Start")
          
        #print("Full response : {}".format(res))
        
    return  plaintextResponse, boxedImages
    
    

def primaryHandler(filePath): #/tmp/gradio/a2270f1e67eb1b9ceb884cde01ceb85f046f23d9/F1_0058.tif    
    print("Path = {}".format(filePath))
    if filePath == None:
        gr.Info("Ei tiedostoa --> ei käsittelyä..")
        return 0
    #upFileName = os.path.split(filePath)[1]    
    mime = checkForImage((filePath))
    print (mime)
    mimetype, detail = mime.split('/')    
    if detail=="pdf":
        print("Encoutered a pdf file, create images and capture existing ocr content")
        orgText = getPDFText(filePath)
        
        images = pdfToImages(filePath) #Pil image array
                        
        plaintextResponse, boxedImages  = handleImage(images)   
        finalPDF = "{}_ocr.pdf".format(filePath)
        createFinalPDF(boxedImages, finalPDF) 
                
        return orgText, plaintextResponse, finalPDF
    
    else:
        gr.Info("Väärä tiedostotyyppi, {}. Vain pdf tiedostot ovat sallittuja tässä demossa".format(mimetype))
        return 0   
    #print("avg count")
    

def checkForImage(upFile):
    mime = magic.Magic(mime=True)
    return mime.from_file(upFile)    
        
        
if __name__ == '__main__':    
    
    
    print("Using Gradio {}".format(gr.__version__))
    snkey = "./snakeoil/snakeoil.key"
    sncert="./snakeoil/snakeoil.crt"
    """
    webui = gr.Interface(
        fn=primaryHandler,
        title="AIDA Paddle OCR Demo",
        description="Tämä demo käyttää AIDA -projektin jatko-opettamaa PaddleOCR moottoria",
        #inputs=gr.Image(),
        inputs=gr.File(label="Uppaa tähän kuvatiedosto"),
        outputs=[gr.Textbox(label="OCR tulokset")]
        )
        """
    
    #Alkuperäinen tekstitieto & uusi ocr tieto rinnakkain
    #laatikcan 

    with gr.Blocks(theme=gr.themes.Soft(primary_hue="blue", secondary_hue="stone")) as webui:      
        gr.Markdown("# AIDA projektin Paddle OCR demo PDF tiedostoille")
        gr.Markdown("Käyttää AIDA projektissa jatko-opetettua PaddleOCR moottoria")
        gr.Markdown("Huom! Voit ladata vain yhden pdf tiedoston kerrallaan")
        gr.Markdown("# Käsittely")
        with gr.Row():
            inputdata = gr.File(label="Lataa tähän pdf tiedosto")
        gr.Markdown("### Huom! Mitä enemmän sivuja sen kauenmmin käsittelyssä kestää ~30 sivua ~2minuuttia koska tällä palvelimella ei ole GPU:ta käytössä.")
        btn = gr.Button("OCR-lue")
        gr.Markdown("# Tuloksien vertailu")        
        with gr.Row():
            orgtext = gr.TextArea(label="Alkuperäinen tekstisisältö (jos saatavilla)")   
            with gr.Column():
                paddleText = gr.TextArea(label="Hankkeessa jatko-opetetun PaddleOCR:n tulos")
                fileDownload = gr.File(label="Lataa laatikoitu pdf tiedosto (huom EI tekstitietoa mukana)")
        gr.Markdown("### Tämä pilottiversio ei muodosta OCR tiedon sisältäviä ladattavia PDF tiedostoja, vain kuvatiedon.")
        gr.Markdown("Ladattavassa tiedostossa laatikoiden tunnistus tarkkuus,  punainen < 75%, oranssi 75-85%, keltainen 85-95% ja  vihreä yli 95%")
        #annotated = gr.Image(label="Laatikoitu kuva")    
        
        btn.click(fn=primaryHandler, inputs=inputdata, outputs=[orgtext, paddleText, fileDownload])
        
    #webui.launch(server_name="0.0.0.0", server_port=8089 )
    webui.launch(server_name="0.0.0.0", server_port=8089, root_path="/AIDA/PDFocr-with-boxes", ssl_keyfile=snkey, ssl_certfile=sncert, ssl_verify=False)
    #demo.launch(server_name="0.0.0.0", server_port=8081, root_path="/ai-demo", ssl_keyfile="./snakeoil/snakeoil.key", ssl_certfile="./snakeoil/snakeoil.crt", ssl_verify=False)
    

