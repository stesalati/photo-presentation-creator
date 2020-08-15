from os import listdir
from os.path import isfile, join
from fpdf import FPDF
import string
import re
import getopt
import sys
import numpy as np

def atoi(text):
    return int(text) if text.isdigit() else text
def natural_keys(text):
    return [atoi(c) for c in re.split(r'(\d+)', text)]


def main(argv):
    # Valori default
    input_folder = "."
    output_filename = "presentation"
    title = ""
    subtitle = ""
    author = ""
    grid_only = False
    R = -1
    C = -1
    white_background = False
    
    # Interpretazione linea di comando
    try:
        opts, args = getopt.getopt(argv,"hi:o:t:s:a:gr:c:w",["input_folder=", "output_filename=", "title=", "subtitle=", "author=", "grid_only=", "R=", "C=", "white="])
    except getopt.GetoptError:
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print("Create a nice PDF portfolio presentation with the images contained in the folder specified.")
            print("Usage: python3 crea [-i folder] [-o file] ...")
            print("Options and arguments:")
            print("-i folder  \t: The folder where the images are. Images are processed in alphabetical order. Default: current folder.")
            print("-o filename\t: Name of the output presentation to be created (extension is not required) in the image folder. Default: \"Presentation\".")
            print("-t text    \t: Title to be shown on the cover page, if not specified, no cover is created. Default: empty.")
            print("-s text    \t: Subtitle to be shown on the cover page. Default: empty.")
            print("-a text    \t: Author name to be shown on the cover page. Default: empty.")
            print("-g         \t: Create only the grid page. Default: not active.")
            print("-r number  \t: Number of rows in the grid view. If not specified, it will be calculated.")
            print("-c number  \t: Number of columns in the grid view. If not specified, it will be calculated.")
            print("-w         \t: Create a presentation with white background instead of the default black.")
            print("-h         \t: Show this help.")
            sys.exit()
        elif opt in ("-i", "--input_folder"):
            input_folder = arg
        elif opt in ("-o", "--output_filename"):
            output_filename = arg
        elif opt in ("-t", "--title"):
            title = arg
        elif opt in ("-s", "--subtitle"):
            subtitle = arg
        elif opt in ("-a", "--author"):
            author = arg
        elif opt in ("-g", "--grid_only"):
            grid_only = True
        elif opt in ("-r", "--rows"):
            try:
                R = int(arg)
            except:
                print("Number of rows must be a number.")
                exit(-1)
        elif opt in ("-c", "--columns"):
            try:
                C = int(arg)
            except:
                print("Number of columns must be a number.")
                exit(-1)
        elif opt in ("-w", "--white_background"):
            white_background = True
    
    # Dimensioni foglio A4 in mm
    H = 210
    W = 297
    
    # Creazione file e impostazioni generali
    pdf = FPDF(orientation = 'L', unit = 'mm', format='A4')
    pdf.set_compression(False)
    pdf.set_margins(0, 0, 0)
    pdf.set_auto_page_break(False)
    if white_background:
        pdf.set_fill_color(255, 255, 255)
        pdf.set_text_color(0, 0, 0)
    else:
        pdf.set_fill_color(0, 0, 0)
        pdf.set_text_color(255, 255, 255)
    
    try:
        miofont = True
        pdf.add_font('miofont', '', 'miofont.ttf', uni=True)
        pdf.set_font('miofont', '', 48)
    except:
        miofont = False
        pdf.set_font('Arial', '', 48)
    
    # Ricerca immagini
    images = [f for f in listdir(input_folder) if f.endswith(".jpg")]
    images.sort(key=natural_keys)
    
    # Copertina
    if title != "":
        pdf.add_page()
        pdf.set_font_size(48)
        if not white_background:
            pdf.cell(0, H, "", 0, 1, align="C", fill=True)
        pdf.set_y(H*4./10.)
        pdf.cell(0, 0, title, 0, 1, align="C", fill=False)
        pdf.set_y(H*5./10.)
        pdf.set_font_size(20)
        pdf.cell(0, 0, subtitle, 0, 1, align="C", fill=False)
        pdf.set_y(H*9/10)
        pdf.set_font_size(12)
        pdf.cell(0, 0, author, 0, 1, align="C", fill=False)

    #Aggiungi immagini
    if not grid_only:
        pdf.set_font_size(12)
        for i, image in enumerate(images):
            pdf.add_page()
            if not white_background:
                pdf.cell(0, H, "", 0, 1, align="C", fill=True)
            pdf.image(join(input_folder, image), x=0, y=0, w=W, h=0)
            pdf.set_y(H-12)
            pdf.cell(0, 12, str(i+1), 0, 1, align="C", fill=False)

    # Contatti
    m_oriz = 5
    m_vert = 5
    m_lat = 10
    
    # Calcolo migliore configurazione griglia
    N = len(images)
    if C == -1 and R != -1:
        C = np.ceil(N/R)
    elif R == -1 and C != -1:
        R = np.ceil(N/C)
    elif C == -1 or R == -1:
        possibili_colonne = np.arange(N*1.)+1
        possibili_righe = np.ceil(N/possibili_colonne)
        possibili_aree_immagini_a_guida_colonne = ((W-2*m_lat)/possibili_colonne)**2*(2/3)
        possibili_aree_immagini_a_guida_righe = ((H-2*m_lat)/possibili_righe)**2*(3/2)
        aree_risultanti = np.minimum(possibili_aree_immagini_a_guida_colonne, possibili_aree_immagini_a_guida_righe)
        i_migliore = np.where(aree_risultanti == np.max(aree_risultanti))
        R = possibili_righe[i_migliore]
        C = possibili_colonne[i_migliore]
        #print(possibili_colonne)
        #print(possibili_righe)
        #print(aree_risultanti)
        max_to_min_sort_index = np.argsort(aree_risultanti)[::-1]
        print(possibili_righe[max_to_min_sort_index][:4])
        print(possibili_colonne[max_to_min_sort_index][:4])
        print(aree_risultanti[max_to_min_sort_index][:4])     
    
    # Creazione pagina
    pdf.add_page()
    pdf.cell(0, H, "", 0, 1, align="C", fill=True)
    
    # Parto dalle colonne e vedo se l'altezza sta nei margini
    w = (W-2*m_lat-(C-1)*m_oriz)/C
    h = w/3.*2.
    total_h = R*h+(R-1)*m_vert + m_lat
    # E' troppo alta, devo ripartire dalle righe e calcolare le colonne di conseguenza
    if total_h > H:
        h = (H-2*m_lat-(R-1)*m_vert)/R
        w = h*3./2.
        total_w = C*w+(C-1)*m_oriz + m_lat
        if total_w > W:
            print("Non può essere.")
    
    for i, image in enumerate(images):
        pdf.image(join(input_folder, image), x=(W-(C*w+(C-1)*m_oriz))/2 + (i%C)*(w+m_oriz), y=(H-(R*h+(R-1)*m_vert))/2 + int(i/C)*(h+m_vert), w=w, h=0)

    # Salva
    pdf.output(join(input_folder, output_filename+".pdf"), "F")

    
if __name__ == "__main__":
   main(sys.argv[1:])