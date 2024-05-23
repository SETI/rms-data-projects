# Author: Mia J.T. Mace

# Bespoke script to generate labelled diagrams for the bundleset of Earth-Based
# Uranus Occultations (Dick French) from the *_obs_geom.pdf browse products.

# The browse products can be found in:
# https://pds-rings.seti.org/pds4/bundles/uranus_occs_earthbased

# NOTE: this code assumes that all the * _obs_geom.pdf browse products supplied
# by the data provider have been copied over to a single directory `input_dir`.
# This can be achieved using the `copy_obs_geom_browseproducts_to_new_dir.sh`
# bash script supplied in the same parent dir as this python script.

# Virtual environment dependencies are listed in the supplied requirements.txt.
# NOTE: this script requires poppler for the pdfinfo comand used by pdf2image
# (e.g. `brew install poppler`).

import os
import re
import matplotlib.pyplot as plt
from pdf2image import convert_from_path
from PIL import Image, ImageFilter, ImageDraw, ImageFont
# Font for full-res (Computer Modern Unicode Sans Serif Demi Condensed)
from matplotlib import font_manager
font_path = './cmunssdc.ttf'
prop = font_manager.FontProperties(fname=font_path)
font_name = './cmunssdc.ttf'


def parse_xmlprimaryfilespec(filespec):
    """
    Parses the primary filespec XML to label the diagram with the type of
    observation, for each OPUS ID.

    Parameters:
    filespec (str): A filepath string for an observation (OPUS ID).

    Returns:
    str: The label to be added to the diagram.

    Example:
    >>> parse_xmlprimaryfilespec(
    ...     "uranus_occs_earthbased/uranus_occ_u5_lco_250cm/data/rings/" \
    ...     "u5_lco_250cm_2200nm_radius_beta_egress_100m.xml"
    ... )
    "Ring β Egress"
    """
    filename = os.path.split(filespec)[1]
    # Split by both "." and "_", as atmosphere/ files end with
    # "ingress.xml" or "egress.xml" so filename.split("_") wouldn't work
    parts = re.split(r'[._]', filename)
    annotation = ""

    # Mapping of Greek letter names and numbers to LaTeX representations
    symbols = {
        "alpha": "α",
        "beta": "β",
        "gamma": "γ",
        "delta": "δ",
        "epsilon": "ε",
        "eta": "η",
        "theta": "θ",
        "lambda": "λ",
        "four": "4",
        "five": "5",
        "six": "6",
    }

    # Iterate through parts and append annotations
    for part in parts:
        if part == "atmos":
            annotation += "Atmos "
        elif part == "equator":
            annotation += "Ring-plane "
        elif part in symbols:
            annotation += "Ring " + symbols[part] + " "
        if part in ["ingress", "egress"]:
            annotation += part.title() + " "
    return annotation.strip()


def format_title_str(pdf_file):
    """
    Generates title string for diagram from filename.

    Parameters:
    pdf_file (str): Input filename of data provider's browse product.

    Returns:
    str: The title string for the diagram.

    Example:
    >>> format_title_str("u9_lco_250cm_2200nm_obs_geom.pdf")
    "u9 LCO 2.5m 2200nm"
    """

    title_text = re.split("_obs_geom.pdf", pdf_file)[0]  # e.g. 'u14_lco_250cm_2200nm'
    title_text = re.split("_", title_text)  # e.g. ['u14', 'lco', '250cm', '2200nm']
    if title_text[2] != "fos":  # convert numerical cm to m
        cm_val = float(title_text[2][:-2])
    if title_text[1] == "teide":
        title_text = (
            title_text[0] + " "
            + title_text[1].title() + " "
            + f"{cm_val/100:.2f}" + "m "
            + title_text[3]
        )
    elif title_text[1] == "lowell":
        title_text = (
            title_text[0] + " "
            + title_text[1].title() + " "
            + f"{cm_val/100:.1f}" + "m "
            + title_text[3]
        )
    elif title_text[1] == "palomar":
        title_text = (
            title_text[0] + " Pal "
            + f"{cm_val/100:.2f}" + "m "
            + title_text[3]
        )
    elif title_text[1] == "mcdonald":
        title_text = (
            title_text[0] + " McDon "
            + f"{cm_val/100:.1f}" + "m "
            + title_text[3]
        )
    elif title_text[1] == "maunakea":
        title_text = (
            title_text[0] + " UKIRT "
            + f"{cm_val/100:.1f}" + "m "
            + title_text[3]
        )
    elif title_text[1] == "hst":
        title_text = (
            title_text[0] + " HST FOS "
            + title_text[3]
        )
    else:
        title_text = (
            title_text[0] + " "
            + title_text[1].upper() + " "
            + (lambda length_cm: f"{length_cm / 100:g}m ")(cm_val)
            + title_text[3]
        )
    return title_text


# The input_dir is where the * _obs_geom.pdf browse products reside that were
# supplied by the data provider, Dick French.
# (These can be copied over from the browse/global subdirectories of the
# observation bundles, using copy_obs_geom_browseproducts_to_new_dir.sh)
input_dir = "."  # Update as appropriate

pdf_files = [file for file in os.listdir(input_dir) if file.endswith("_obs_geom.pdf")]

# Read in full primary filespec so can use dir tree info to save diagrams to
# appropriate location reflecting /Volumes/pdsdata-admin/pds4-holdings/bundles/
with open("./primary_filespec_list_mjtm.txt", "r") as filepath:
    filespecs = filepath.read().splitlines()  # list
    filenames = [os.path.split(filespec)[1] for filespec in filespecs]

# Create dictionary of labelling info from the primary filespecs that will be
# used to annotate the diagrams
annotations = {filespec: parse_xmlprimaryfilespec(filespec) for filespec in filespecs}

for pdf_file in pdf_files:
    pdf_file_path = os.path.join(input_dir, pdf_file)  # Construct full filepath
    print("Processing: ", pdf_file)
    images = convert_from_path(pdf_file_path)  # Default format is JPEG
    image = images[0]  # Since there's only one image (page) per PDF
    # Crop out whitespace – obtained by trial-and-error(!)
    horizontal_crop = 350  # Pixels
    vertical_crop = 100  # Chosen to retain square aspect ratio (at expense of more whitespace)

    # Determine dimensions
    width, height = image.size

    # Crop out white space
    image_full = image.crop((
         horizontal_crop,
         vertical_crop,
         width - horizontal_crop,
         height - vertical_crop
    ))

    # Extract substring from input PDF filename
    # (to match against corresponding XML primary filespec)
    pdf_file_substr = re.sub(r'_obs_geom\.pdf$', '', pdf_file)

    # For each annotation, check if the substring exists in the XML filename
    for xml_filespec, annotation_label in annotations.items():
        xml_filename = os.path.split(xml_filespec)[1]
        if pdf_file_substr in xml_filename:
            # Handle full, medium, small, and thumbnail sizes in turn
            # --- FULL-RES --- #
            image_full_annot = image_full.copy()  # Create a copy of the original image

            # Draw annotation label on the image using Matplotlib
            # Same blue as used by pds-rings.seti.org
            plt.figure(figsize=(10, 10))
            plt.imshow(image_full_annot)
            plt.axis('off')
            color_rgb = (69/255, 120/255, 180/255)  # Convert each component to range [0, 1].

            # Label with text from annotations dictionary and the wavelength
            # Guesstimate placement to line up with title text
            plt.text(200, 0.145*image_full_annot.height, annotation_label,
                     color=color_rgb, fontproperties=prop, fontsize=26)
            # Output of re.split("_", pdf_file_substr) is, e.g.,
            #  ['u25', 'palomar', '508cm', '2200nm']
            wavelength_label = re.split("_", pdf_file_substr)[3]
            plt.text(200, 0.145*image_full_annot.height-44, wavelength_label,
                     color=color_rgb, fontproperties=prop, fontsize=26)
            plt.subplots_adjust(left=0, right=1, top=1, bottom=0)

            # Save the composite image
            parent_dir_tree = os.path.split(xml_filespec)[0]
            os.makedirs(parent_dir_tree, exist_ok=True)

            if "_100m" in xml_filename:
                # Strip off the resolution
                output_path_full = os.path.join(parent_dir_tree,
                                                xml_filename.replace(
                                                "_100m.xml", "_diagram_full.png"
                                                ))
            else:
                output_path_full = os.path.join(parent_dir_tree,
                                                xml_filename.replace(
                                                ".xml", "_diagram_full.png"
                                                ))
            plt.savefig(output_path_full, dpi=150)
            plt.close()

            # --- MEDIUM ---  #
            # For medium-size image, resize to 500x500px
            # Create a copy of the original image
            image_med_annot = image_full.copy()
            # Thicken lines before shrinking image
            image_med_annot_filter = image_med_annot.filter(
                                     ImageFilter.MinFilter(size=3)
                                     )
            image_med_annot_filter.thumbnail((500, 500))
            # Create a blank image for rendering text with higher DPI
            dpi = 600  # Adjust DPI as needed for sharpness
            text_med_image = Image.new('RGBA',
                                       (500*dpi//100, 500*dpi//100),
                                       (255, 255, 255, 0)
                                       )
            draw = ImageDraw.Draw(text_med_image)
            fontsize = 24*dpi // 100  # Adjust font size based on DPI
            font = ImageFont.truetype(font_name, fontsize)

            # Calculate text size and position
            text_med_width = draw.textlength(annotation_label, font=font)
            text_med_x = (text_med_image.width - text_med_width) // 2
            text_med_y = (50*dpi // 100)  # Adjust vertical position as needed

            # Draw white rectangle behind the text (to mask)
            background_rectangle = ((text_med_x, text_med_y*1.1),
                                    (text_med_x + text_med_width*1.3,
                                     text_med_y + fontsize*1.5
                                    ))
            draw.rectangle(background_rectangle, fill="white")

            # Draw text onto the blank image
            # (use same blue as pds-rings.seti.org)
            draw.text((text_med_x, text_med_y+fontsize*0.9),
                      annotation_label, fill=(69, 120, 180), font=font)
            # Output of re.split("_", pdf_file_substr) is, e.g.,
            # ['u25', 'palomar', '508cm', '2200nm']
            wavelength_label = re.split("_", pdf_file_substr)[3]
            text_med_wavelength = (text_med_image.width - draw.textlength(wavelength_label, font=font)) // 2
            draw.text((text_med_wavelength, text_med_y),
                       wavelength_label,
                       fill=(69, 120, 180),
                       font=font
                     )
            # Ensure the text image has the same dims as the annotated image
            text_med_image = text_med_image.resize(image_med_annot_filter.size, Image.LANCZOS)

            # Composite the text image onto the annotated image
            composite_med_image = Image.alpha_composite(image_med_annot_filter.convert('RGBA'), text_med_image)
            # Convert the image mode from RGBA to RGB (alpha not compatible with JPEG)
            composite_med_image = composite_med_image.convert('RGB')

            # Save the composite image
            parent_dir_tree = os.path.split(xml_filespec)[0]
            os.makedirs(parent_dir_tree, exist_ok=True)

            if "_100m" in xml_filename:
                # Strip off the resolution
                output_path_med = os.path.join(parent_dir_tree,
                                               xml_filename.replace(
                                               "_100m.xml", "_diagram_med.png"
                                               ))
            else:
                output_path_med = os.path.join(parent_dir_tree,
                                               xml_filename.replace(
                                               ".xml", "_diagram_med.png"
                                               ))
            composite_med_image.save(output_path_med, dpi=(150, 150))

            # --- SMALL --- #
            # For small-size image, resize to 250x250px
            # Make a copy before resizing, and since going to crop a different amount, use image not image_full
            image_small = image.copy()
            # Crop out white space and labels, since illegible at this scale.
            # Planet not centred so asymmetric cropping required.
            # Crop amounts (in pixels) – obtained by trial-and-error(!)
            left_crop = 515
            right_crop = 431
            top_crop = 194
            bottom_crop = 250
            image_small_annot = image_small.crop((left_crop,
                                                  top_crop,
                                                  image.width - right_crop,
                                                  image.height - bottom_crop))
            # Thicken lines before shrinking image
            image_small_annot_filter = image_small_annot.filter(ImageFilter.MinFilter(size=3))
            image_small_annot_filter.thumbnail((250, 250))  # Resize cropped img
            title_text = format_title_str(pdf_file)

            # Use layers to improve text sharpness
            dpi = 300  # Adjust DPI as needed for sharpness
            font_size = 18*dpi//100  # Adjust font size based on DPI
            # Create a blank image for rendering text with higher DPI
            text_small_image = Image.new('RGBA',
                                         (250 * dpi // 100, 250 * dpi // 100),
                                         (255, 255, 255, 100)
                                        )
            draw = ImageDraw.Draw(text_small_image)
            font = ImageFont.truetype(font_name, font_size)
            # Calculate text size and position
            title_small_width = draw.textlength(title_text, font=font)
            # Center title horizontally
            title_small_x = (text_small_image.width - title_small_width) // 2
            title_small_y = 15  # Adjust the vertical position as needed
            text_small_width = draw.textlength(annotation_label, font=font)
            # Center text horizontally
            text_small_x = (text_small_image.width - text_small_width) // 2
            text_small_y = (title_small_y+font_size) * 0.85
            # Draw text onto the blank image with white rectangle behind text
            # (to mask out Dick French's prior labelling)
            background_rectangle = ((15, text_small_y),
                                    (text_small_x + text_small_width*1.3,
                                     text_small_y + font_size)
                                   )
            draw.rectangle(background_rectangle, fill="white")
            background_rectangle_title = ((15, title_small_y),
                                          (title_small_x + title_small_width*1.1,
                                           title_small_y + font_size*1.5)
                                         )
            draw.rectangle(background_rectangle_title, fill="white")
            # Use same blue as pds-rings.seti.org
            draw.text((text_small_x, text_small_y), annotation_label,
                       fill=(69, 120, 180), font=font)
            draw.text((title_small_x, title_small_y), title_text,
                       fill=(69, 120, 180), font=font)
            # Ensure the text image has the same dims as the annotated img
            text_small_image = text_small_image.resize(image_small_annot_filter.size, Image.LANCZOS)

            # Composite the text image onto the annotated image
            composite_small_image = Image.alpha_composite(image_small_annot_filter.convert('RGBA'), text_small_image)
            # Convert the image mode from RGBA to RGB (alpha not compatible with JPEG)
            composite_small_image = composite_small_image.convert('RGB')

            # Save the composite image
            parent_dir_tree = os.path.split(xml_filespec)[0]
            os.makedirs(parent_dir_tree, exist_ok=True)

            if "_100m" in xml_filename:
                # Strip off the resolution
                output_path_small = os.path.join(parent_dir_tree,
                                                 xml_filename.replace(
                                                 "_100m.xml", "_diagram_small.png"
                                                 ))
            else:
                output_path_small = os.path.join(parent_dir_tree,
                                                 xml_filename.replace(
                                                 ".xml", "_diagram_small.png"
                                                 ))
            composite_small_image.save(output_path_small, dpi=(150, 150))

            # --- THUMBNAIL --- #
            # For thumbnail-size image, resize to 100x100px
            image_thumb = image.copy()
            # Crop out white space and labels, since illegible at this scale.
            # Planet not centred so asymmetric cropping required.
            # Crop amounts (in pixels) – obtained by trial-and-error(!)
            left_crop = 515
            right_crop = 430
            top_crop = 80
            bottom_crop = 370
            image_thumb_annot = image_thumb.crop((left_crop,
                                                  top_crop,
                                                  image.width - right_crop,
                                                  image.height - bottom_crop))
            # Thicken lines before shrinking image
            image_thumb_annot_filter = image_thumb_annot.filter(ImageFilter.MinFilter(size=5))
            image_thumb_annot_filter.thumbnail((100, 100))  # Resize cropped img
            title_text = format_title_str(pdf_file)
            # Use layers to improve text sharpness
            dpi = 600  # Adjust DPI as needed for sharpness
            font_size = 9*dpi//100  # Adjust font size based on DPI
            # Create a blank image for rendering text with higher DPI
            text_thumb_image = Image.new('RGBA',
                                         (100 * dpi // 100, 100 * dpi // 100),
                                         (255, 255, 255, 100)
                                        )
            draw = ImageDraw.Draw(text_thumb_image)
            font = ImageFont.truetype(font_name, font_size)
            # Calculate text size and position
            title_thumb_width = draw.textlength(title_text, font=font)
            title_thumb_x = (text_thumb_image.width - title_thumb_width) // 2
            title_thumb_y = 5
            text_thumb_width = draw.textlength(annotation_label, font=font)

            text_thumb_x = (text_thumb_image.width - text_thumb_width) // 2
            text_thumb_y = (title_thumb_y+font_size) * 0.9
            # Draw text onto the blank image with white rectangle behind text
            background_rectangle = ((0, text_thumb_y),
                                    (text_thumb_x + text_thumb_width*1.55,
                                     text_thumb_y + font_size*1.5))
            draw.rectangle(background_rectangle, fill="white")
            background_rectangle_title = ((0, title_thumb_y),
                                          (title_thumb_x + title_thumb_width*1.6,
                                           title_thumb_y + font_size*1.3))
            draw.rectangle(background_rectangle_title, fill="white")
            # Use same blue as pds-rings.seti.org
            draw.text((text_thumb_x, text_thumb_y), annotation_label,
                       fill=(69, 120, 180), font=font)
            draw.text((title_thumb_x, title_thumb_y), title_text, fill=(69, 120, 180), font=font)
            # Ensure the text image has the same dimensions as the annotated image
            text_thumb_image = text_thumb_image.resize(image_thumb_annot_filter.size, Image.LANCZOS)

            # Composite the text image onto the annotated image
            composite_thumb_image = Image.alpha_composite(image_thumb_annot_filter.convert('RGBA'), text_thumb_image)
            # Convert the image mode from RGBA to RGB (alpha not compatible with JPEG)
            composite_thumb_image = composite_thumb_image.convert('RGB')

            # Save the composite image
            parent_dir_tree = os.path.split(xml_filespec)[0]
            os.makedirs(parent_dir_tree, exist_ok=True)

            if "_100m" in xml_filename:
                # Strip off resolution
                output_path_thumb = os.path.join(parent_dir_tree,
                                                 xml_filename.replace(
                                                 "_100m.xml", "_diagram_thumb.png"
                                                 ))
            else:
                output_path_thumb = os.path.join(parent_dir_tree,
                                                 xml_filename.replace(
                                                 ".xml", "_diagram_thumb.png"
                                                 ))
            composite_thumb_image.save(output_path_thumb, dpi=(150, 150))

print("Done!")
