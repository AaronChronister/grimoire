import json
import os
import sys
import pandas as pd
import re

####INSTRUCTIONS ###########################################################

#In order to use this, you need to upload all the card images to an image hosting site.
#I am using Flickr. Once you have uploaded all the images, you need to get a list of all the URLs
#to associate them with the respective card. Flickr is good for this because the URL has the card name
#inside it, so you can parse that out. 
#
#Use the Flickr API browser helper here: https://www.flickr.com/services/api/explore/flickr.photosets.getPhotos
#plug in the photoset_id of whatever album you saved all the card images to. Then, copy the entire output of that 
#http call and paste it into a file that has the name of whatever you set "input_file" to be below.
# Once that is done, you can run this script to generate an appropriately formatted text file to load into Draftmancer
# at "output_file", and another file useful for the tts custom game "tts_file"

input_file = "flickr_response.txt"
output_file = "Grimoire_CustomCardList.txt"
tts_file = "tts_list_all.txt"

########## FLICKR PARSING ###################################################

import xml.etree.ElementTree as ET

def flickr_xml_to_dict(file_path):
    """
    Parse a Flickr photoset XML file and return a dict {title: direct_image_url}.
    """
    tree = ET.parse(file_path)
    root = tree.getroot()

    photoset = root.find("photoset")
    if photoset is None:
        raise ValueError("No <photoset> element found in XML file")

    photo_map = {}

    for photo in photoset.findall("photo"):
        title = photo.attrib.get("title", "").strip()
        photo_id = photo.attrib.get("id")
        secret = photo.attrib.get("secret")
        server = photo.attrib.get("server")

        if not (title and photo_id and secret and server):
            continue  # skip incomplete entries

        url = f"https://live.staticflickr.com/{server}/{photo_id}_{secret}.jpg"
        photo_map[title] = url

    return photo_map

#############################################################################



########## DRAFTMANCER JSON CONSTUCTOR ###################################################

RARITY_TO_RATING = {'common' : 0, 'uncommon' : 3, 'rare' : 5}
CLASS_TO_COLOR = {'Necro' : 'B', 'Priest' :'W', 'Pyro':'R', 'Druid': 'G'}

### number duplicate cards per rarity in total game box 
rare_copies = 1
uncommon_copies = 2
common_copies = 3

### number of packs to draft, and cards per rarity in each pack
num_players = 4
num_packs = 3
rares_per_pack = 2
uncommons_per_pack = 4
commons_per_pack = 7


current_directory = os.getcwd()
parent_directory = os.path.dirname(current_directory)
top_directory = os.path.dirname(parent_directory)

card_list= f'{top_directory}/Card_data/Grimoire Draft Set (Alpha).csv'
df=pd.read_csv(card_list)

image_map = flickr_xml_to_dict(input_file)

draftmancer_cards = []
common_cards = []
uncommon_cards=[]
rare_cards=[]
for index, row in df.iterrows():
    name=row['Card Name']
    rarity=row['Rarity']
    color1=row['Color1']
    color2=row['Color2']
    cost1=row['Cost1']
    cost2=row['Cost2']
    typ=row['Type']
    subtyp=row['Subtype']
    atk=row['ATK']
    hp=row['HP']
    move = row["Move"]
    text = row["Text"]

    colors=[]
    colors.append(CLASS_TO_COLOR[color1])
    if not pd.isna(color2):
        colors.append(CLASS_TO_COLOR[color2])

    if type(cost1) != int:
        cost1=int(cost1.strip("X")) if cost1.strip("X") != "" else 0
    if type(cost2) != int and cost2 != "None":
        cost2=int(cost1.strip("X")) if cost2.strip("X") != "" else 0
    elif cost2 == "None":
        cost2=0 

    # name_processed = name.rstrip().replace(" ","-")
    # name_processed = re.sub(r'[^a-zA-Z0-9]', '-', name_processed)
    draftmancer_cards.append(
        {
        "name": name.rstrip(),
        "rarity": rarity.lower(),
        "mana_cost": f"{cost1+cost2}",
        "type": "Legendary Creature",
        "subtypes": [
            "God"
        ],
        "rating" : RARITY_TO_RATING[rarity.lower()],
        "image": f'{image_map[name]}',
        "colors" : colors
        }
    )

    match rarity.lower():
        case 'common':
            common_cards.append(name)
        case 'uncommon':
            uncommon_cards.append(name)
        case 'rare':
            rare_cards.append(name)

with open(output_file, "w", encoding="utf-8") as f:
    f.write("[CustomCards]\n")

with open(output_file, "a", encoding="utf-8") as f:
    json.dump(draftmancer_cards, f, indent=4, ensure_ascii=False)


# Open the same file in append mode
with open(output_file, "a", encoding="utf-8") as f:
    f.write(f"\n[Rares({rares_per_pack})]")
    f.write("\n")  # make sure the list starts on a new line
    for cardname in rare_cards:
        f.write(f"{rare_copies} {cardname}\n")

    f.write(f"\n[Uncommons({uncommons_per_pack})]")
    f.write("\n")  # make sure the list starts on a new line
    for cardname in uncommon_cards:
        f.write(f"{uncommon_copies} {cardname}\n")
        
    f.write(f"\n[Commons({commons_per_pack})]")
    f.write("\n")  # make sure the list starts on a new line
    for cardname in common_cards:
        f.write(f"{common_copies} {cardname}\n")

print(f"\nTotal number of cards (including duplicates: \nRares = {rare_copies*len(rare_cards)}\nUncommons = {uncommon_copies*len(uncommon_cards)}\nCommons = {common_copies*len(common_cards)}\nTotal = {rare_copies*len(rare_cards)+uncommon_copies*len(uncommon_cards)+common_copies*len(common_cards)}\n\nNumber of cards needed for 4 man draft \nRares = {rares_per_pack*num_players*num_packs} \nUnommons = {uncommons_per_pack*num_players*num_packs} \nCommons = {commons_per_pack*num_players*num_packs} \nTotal = {(rares_per_pack+uncommons_per_pack+commons_per_pack)*num_players*num_packs}")


with open(tts_file, "w", encoding="utf-8") as f:
    f.write("local cardDataJson = [[\n")

with open(tts_file, "a", encoding="utf-8") as f:
    json.dump(draftmancer_cards, f, indent=4, ensure_ascii=False)

with open(tts_file, "a", encoding="utf-8") as f:
    f.write("\n]]")


