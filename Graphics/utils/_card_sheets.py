from PIL import Image
import os
import sys
import math
import pandas as pd

# Set the directory containing your JPEG images

current_directory = os.getcwd()
parent_directory = os.path.dirname(current_directory)
top_directory = os.path.dirname(parent_directory)

image_directory = f'{parent_directory}/finished_cards/pngs'
card_list= f'{top_directory}/Card_data/Grimoire Draft Set (Alpha).csv'

df=pd.read_csv(card_list)

# Set the number of rows and columns for the grid
rows = 3
columns = 3
cards_per_sheet= rows*columns

# Get a list of image file paths in the directory
all_image_files = [os.path.join(image_directory, filename) for filename in os.listdir(image_directory) if filename.endswith('.png')]



rarity = sys.argv[1] if len(sys.argv)>1 else []

if rarity:
    image_files=[]
    for image_file in all_image_files:
        selected_rows = df[df['Card Name'] == image_file.split("/")[-1].split(".")[0]]
        if len(selected_rows['Rarity'].values)==0:
            print(image_file)
        if selected_rows['Rarity'].values[0] == rarity:
            image_files.append(image_file)
else:
    image_files=all_image_files

# Calculate the width and height of the individual images
image_width, image_height = Image.open(image_files[0]).size
width_margin, height_margin = (image_width*0, image_height*0)
# Create blank images with the dimensions of the grid
number_of_sheets = math.ceil(len(image_files)/(cards_per_sheet))
sheets=[]
for i in range(number_of_sheets):
    grid_width = columns * image_width
    grid_height = rows * image_height
    grid_image = Image.new('RGB', (int(grid_width+width_margin), int(grid_height+height_margin)), (255,255,255))
    sheets.append(grid_image)

# Iterate through the image files and paste them into the grid
for i, image_file in enumerate(image_files):
        sheet_num = i // cards_per_sheet
        row = (i-sheet_num*cards_per_sheet) // columns
        col = (i-sheet_num*cards_per_sheet) % columns
        image = Image.open(image_file)
        sheets[sheet_num].paste(image, (int(col * image_width + 1/2*width_margin), int(row * image_height+ 1/2*height_margin)))


for sheet_num, sheet in enumerate(sheets):
    # Save the final stacked image
    sheet.save(f'{parent_directory}/finished_cards/card_sheets/{rarity}_set_{sheet_num}.jpg')


print('Stacked image saved as stacked_image.jpg')

