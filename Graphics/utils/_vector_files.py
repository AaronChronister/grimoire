
import xml.dom.minidom as minidom
import cairosvg
import json
import os
import sys
import base64
import numpy as np
import pandas as pd
import re

COLORMAP = {"Necro" : "#763F8B", "Pyro" : "#DF4D1F", "Druid" : "#136b08", "Priest" : "#FFFDD9"}
NAMEMAP = {"Necro" : "Necromancer", "Pyro" : "Pyromancer", "Druid" : "Druid", "Priest" : "Priest"}
convert_to_pngs=True

specified_card = sys.argv[1] if len(sys.argv)>1 else []

current_directory = os.getcwd()
parent_directory = os.path.dirname(current_directory)
top_directory = os.path.dirname(parent_directory)

# Load card data from CSV
card_list= f'{top_directory}/Card_data/Grimoire Draft Set (Alpha).csv'
df=pd.read_csv(card_list)

# trim dataframe if subset of cards is specified
if specified_card:
    specified_card = re.sub("'", "’", specified_card) ##Numbers exports apostrophes as the Shift + Option + ] kind. (Unicode 8217)
    mask = df['Card Name'] == specified_card 
    df = df[mask]
num_total = len(df)
count = 0

# Load the SVG templates
background_image_data = dict()
mana_icon_image_data = dict()
#for classname in [ "Pyromancer"]:
for classname in ["Necromancer", "Pyromancer", "Priest", "Druid"]:
    
    icon_path = f'{parent_directory}/icons/{classname}_mana.png'
    with open(icon_path, "rb") as image_file:
        new_image_data = image_file.read()
    new_base64_data = base64.b64encode(new_image_data).decode("utf-8")
    mana_icon_image_data[classname] =  new_base64_data

    background_image_data[classname] = dict()
    for rarity in ["common", "uncommon", "rare"]:
    #for rarity in ["uncommon"]:
        # Encode the background image data in base64
        background_path = f'{parent_directory}/backgrounds/{classname}_{rarity.upper()}_card_template_typebox.png'
        with open(background_path, "rb") as image_file:
            new_image_data = image_file.read()
        new_base64_data = base64.b64encode(new_image_data).decode("utf-8")

        background_image_data[classname][rarity] =  new_base64_data

icon_path = f'{parent_directory}/icons/Colorless_mana.png'
with open(icon_path, "rb") as image_file:
    new_image_data = image_file.read()
new_base64_data = base64.b64encode(new_image_data).decode("utf-8")
mana_icon_image_data["Colorless"] =  new_base64_data

with open(f'{parent_directory}/vector_templates/draft_template_minion_ALPHA.svg', "r") as file:
    minion_svg_data = file.read()

with open(f'{parent_directory}/vector_templates/draft_template_spell_ALPHA.svg', "r") as file:
    spell_svg_data = file.read()

with open(f'{parent_directory}/vector_templates/draft_template_conduit_ALPHA.svg', "r") as file:
    conduit_svg_data = file.read()

# Find the element by its ID
name_id = "text1089"
text_id = "text839"
mana_id = "text990-1"#tspan988-8
attack_id = "text990-5"#tspan988-3
HP_id = "text990"#tspan988

for index, row in df.iterrows():
    card_name=row['Card Name']
    rarity=row['Rarity']
    color1=row['Color1']
    color2=row['Color2']
    cost0=row['Cost0'] #row['Cost0'] is a string due to presence of "X" entries
    cost1=row['Cost1']
    cost2=row['Cost2']
    maintype=row['Type']
    subtype=row['Subtype']
    atk=row['ATK']
    hp=row['HP']
    move = row["Move"]
    card_text = row["Text"]
    refund_color =row["Refund"]

    if maintype == 'Minion':
        svg_data = minion_svg_data
    elif maintype == 'Conduit':
        svg_data = conduit_svg_data
    else:
        svg_data = spell_svg_data


    dom = minidom.parseString(svg_data)
    count+=1
    print(f'processing card {count}/{num_total}: {card_name}')

    elements = dom.getElementsByTagName("tspan")  # Change "text" to the appropriate tag name
    for element in elements:
        for node in [node for node in element.childNodes if node.nodeValue is not None]:

            template_text= node.nodeValue.strip()

            if template_text == 'Card Name':
                node.nodeValue = card_name
                if not pd.isna(color2):
                    pass
                    #element.setAttribute('style',f'fill: #D3AF37') 
                    # element.setAttribute('fill', '#FFD700')
                    # element.setAttribute('stroke', '#FFD700')
                else:
                    pass
                    #element.setAttribute('style',f'fill: {COLORMAP[color1]}') 


            if template_text == 'Card Text':
                node.nodeValue = "" if pd.isna(card_text) else card_text

            if cost2 or (cost0!="0"):           
                
	            if template_text == 'M2':
	                node.nodeValue = cost1 if cost1 else ""
	                element.setAttribute('style',f'fill: {COLORMAP[color1]}') 

	            if template_text == 'M1':
	            	if cost2:
	            		node.nodeValue = cost2
	            		element.setAttribute('style',f'fill: {COLORMAP[color2]}')
	            	elif cost0:
	                	node.nodeValue = cost0
	                	element.setAttribute('style',f'fill: #6A6A6A')         	
	            	else:
	                	node.nodeValue = ""
            else: 
	            if template_text == 'M2':
	                node.nodeValue = ""

	            if template_text == 'M1':
            		node.nodeValue = cost1
            		element.setAttribute('style',f'fill: {COLORMAP[color1]}')


                     

            if template_text == 'mov' and move:
                node.nodeValue = int(move)

            if template_text == 'Type' and maintype:
                node.nodeValue = maintype if pd.isna(subtype) else f"{maintype} : {subtype}"

            if template_text == 'P' and atk:
                node.nodeValue = atk

            if template_text == 'T' and hp:
                node.nodeValue = hp




    #check if card name has associated art
    card_name_pic = re.sub("’", "'", card_name) ##Need to convert from Numbers apostrophe (Shift + Option + ] (Unicode 8217) ) to normal

    art_path_jpg = f"{parent_directory}/card_art/{card_name_pic}.jpg"
    art_path_png = f"{parent_directory}/card_art/{card_name_pic}.png"

    art_path = None
    if os.path.isfile(art_path_jpg):
        art_path = art_path_jpg
    elif os.path.isfile(art_path_png):
        art_path = art_path_png 
        print(f"Found {art_path}")
    else:
        art_path = f"{parent_directory}/card_art/Placeholder.png"
        print(f"No card art found for {card_name}")

    if art_path:
        # Encode the card's image data in base64
        with open(art_path, "rb") as image_file:
            new_image_data = image_file.read()
        new_base64_data = base64.b64encode(new_image_data).decode("utf-8")

        # Find the <image> element by its ID
        image_id = "image2515"  
        elements = dom.getElementsByTagName("image")  
        for element in elements:
            if element.getAttribute('id')==image_id:
                # Replace the xlink:href attribute with the new image data
                new_xlink_href = f"data:image/jpeg;base64,{new_base64_data}"
                element.setAttribute("xlink:href", new_xlink_href)


    #### background 
    image_id = "image1"  #was7320
    elements = dom.getElementsByTagName("image")  
    for element in elements:
        if element.getAttribute('id')==image_id:
            # Replace the xlink:href attribute with the new image data
            new_xlink_href = f"data:image/jpeg;base64,{background_image_data[NAMEMAP[refund_color]][rarity.lower()]}" 
            element.setAttribute("xlink:href", new_xlink_href)

    if cost2 or (cost0!="0"): 
	    #### mana symbol 1
	    for element in elements:
	        if element.getAttribute('id')=="image19380":
	            # Replace the xlink:href attribute with the new image data
	            new_xlink_href = f"data:image/jpeg;base64,{mana_icon_image_data[NAMEMAP[color1]]}" 
	            element.setAttribute("xlink:href", new_xlink_href)

	    #### mana symbol 2 
	        if element.getAttribute('id')=="image19379":
	            # Replace the xlink:href attribute with the new image data
	            if not pd.isna(color2):
	                new_xlink_href = f"data:image/jpeg;base64,{mana_icon_image_data[NAMEMAP[color2]]}" 
	                element.setAttribute("xlink:href", new_xlink_href)
	            else:
	            	mana_icon = mana_icon_image_data['Colorless']
	            	new_xlink_href = f'data:image/jpeg;base64,{mana_icon}'
	            	element.setAttribute("xlink:href", new_xlink_href)

    else:
	    for element in elements:
	        if element.getAttribute('id')=="image19380":
	        	element.parentNode.removeChild(element)
	        	element.unlink()

	        if element.getAttribute('id')=="image19379":
	            new_xlink_href = f"data:image/jpeg;base64,{mana_icon_image_data[NAMEMAP[color1]]}" 
	            element.setAttribute("xlink:href", new_xlink_href)


    # Save the modified SVG to a new file
    output_svg_filename=f"{parent_directory}/finished_cards/vector_files/{card_name}.svg"
    output_png_filename=f"{parent_directory}/finished_cards/pngs/{card_name}.png"
    
    with open(output_svg_filename, "w") as file:
        file.write(dom.toxml())

    if convert_to_pngs:
        input_svg_filename = output_svg_filename.replace("'", "\'\\\''")
       # print(f"/Applications/Inkscape.app/Contents/MacOS/inkscape --export-type png --export-filename '{output_png_filename}' -w 1024 '{input_svg_filename}'")
        os.system(f"/Applications/Inkscape.app/Contents/MacOS/inkscape --export-type png --export-filename '{output_png_filename}' -w 1024 '{input_svg_filename}' > /dev/null 2>&1")



