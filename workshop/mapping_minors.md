---
title: "Mapping Junior Exploration Companies and Their Subsidiaries"
---

## Geocoding 101

Today, we'll be doing a little bit of geocoding! Geocoding is a process whereby an address is converted into a coordinate pair. While this may seem fairly straightforward---the prevalence of Google Maps, etc. tells us this---it is a very difficult technical problem, especially when many addresses in many localities in multiple languages are involved. It is true that land subdivision, address indexing, cadastral mapping etc. are colonial and capitalistic practices; today, we'll be using them to identify and locate the colonists and the capitalists.

There are a huge number of geocoding services available and they change all the time---our favorite is a service called OpenCage. There are a number of reasons we like it:

1. OpenCage understands complete addresses; while many expect you to parse your address (e.g., into street number, street name, city, state, country), OpenCage does this automatically in the background. This makes life so much easier.
2. OpenCage is built on top of several entirely open-source geocoders.
3. It's free plan is fairly generous: it allows you to geocoder 2,500 addresses per day.
4. Maybe most importantly: your data remains yours after you use the service. This is not the case if you use, for example, Google’s Geocoding service---Google will then claim that they own your data. OpenCage is built to follow the fairly stringent guidelines of the EU’s General Data Protection Regulation (GDPR), which try to coerce firms to let you make your own data.

So we like OpenCage. Let's get you set up with an account.

1.	Go to the [OpenCage Website](https://opencagedata.com/) and sign-up for an account. Once you have your account set-up you should see something called an 'API key' on your Dashboard. You will need this key to geocode your addresses. Copy your API key and store it somewhere. You will need it later!

![The OpenCage dashboard.](media/opencage-api-key.png)

2. Navigate to the [sheet to which we provided access](https://docs.google.com/spreadsheets/d/1DSYTECsygiCwn5PkyE8RYBeZa8bov8Q2SQzEC2ejKZ8/edit#gid=0). This is a sheet with names, web sites, booth numbers, and addresses of all the firms exhibiting at the investors exchange.

3. Cluster yourself into a group of 3-5 and claim a firm by writing 'y' in the 'claimed column. Copy-paste the name of that firm, its address and its country code (to avoid typos!). Paste them into a sheet named after your group and create the following adjacent columns: `sub_name`, `relationship`, `notes`, `add`, `country`, `lat`, and `lng`. You can reference these in the table titled DemoSheet.

4. Using the research methods Chris discussed earlier, do your best to collectively locate the subsidiaries of the firm you've selected. This may or may not be possible---data availability is spotty. For each new subsidiary, you'll need their address (or as close as you cane come) and their 2-character country code (set by the International Organization for Standardization).

    - Each subsidiary row should include the name of the parent company in the `par_name` column.
    - The name of the subsidiary should go in the `sub_name` column.
    - Retain the parent company, with no subsidiary. This should be described as the parent in the `relationship` column.
    - Addresses should be in a format that _excludes apartment and unit numbers_, as well as the country (this goes into the next column). For example, 401 Richmond St W, Toronto M5V 3A8.
    - Country codes must their standard two-letter codes. We usually just reference the Wikipedia entry for the `ISO 3166-1 alpha-2` codes.

5. When you've exhausted available resources, you should have something that looks like this:

![Completed subsidiary research on one firm.](media/finished-firm.png)

6.  To geocode, select values in the address, country, lat, and lng columns, then click 'Geocode', choosing 'Geocode Address to Latitude, Longitude' in the dropdown menu.

    - You may be be prompted to give the script permission to run. Do so. A popup will appear asking you which Google account you want to authorize. Select one.

    - The popup will display a warning that our app isn't verified. Click "Advanced", scroll down, click on the link to "Go to your-project-name (unsafe)." 

7. A popup will appear in your spreadsheet asking your for your OpenCage API key. Enter it and click "Geocode". This will take about a second per row.

![Google Sheet set up for Geocoding.](media/select-columns.png)

8. Now that you get the mechanics, go ahead and do this for more firms. You can do all of them in the same sheet. Just be careful to not overwrite each others work, and geocode sparingly - try to do it only when you've come to the end of a research process.

### Make a Map!

1. Open QGIS; as we discussed earlier, QGIS is a geographic information system, or a desktop application that allows us to make maps from spatial data... including the latitudes and longitudes that we just geocoded.

![Import CSV using the Data Source Manager.](media/qgis-csv.png)

2. You can add a CSV with coordinates to QGIS in a very simple way: open the Data Source Manager, and choose 'Delimited Text'. Open the CSV; your X filed is longitude and your Y field is latitude!

3. Your Geometry CRS is EPSG:4326 WGS 84. Click 'Add' when you are done. You should see points corresponding to your latitudes and longitudes.

4. Add the 'countries.geojson' file we provided to your layers pane by clicking-and-dragging or by using the Data Source Manager like we did above. This will serve as a simple basemap.

5. We're now going to choose a coordinate reference system (CRS), or _projection_---we don't have the space to discuss map projections and their challenges here, but suffice it to say that it's hard to take the a globe and flatten it. We're going to choose 'World Azimuthal Equidistant' projection, partly because it's arguably anti-colonial and partly because it's aesthetically pleasing.

![Selecting a project coordinate reference system (CRS).](media/map_proj.png)

6. Style your countries basemap by right-clicking it in the layers pane and selecting properties. Customize the 'Symbology', choose a black fill, and a white outline with a width of 0.15.

![Styling the basemap.](media/countries-sym.png)

7. Now, we're going to style the parents and subsidiaries of each company! Open the properties pane of the geocoded points and select 'Categorized' from the drop-down menu at the top. We want to categorize based on the 'subsidiary column'.

![Styling the investors, symbology pane.](media/point-sym.png)

8. Style the 'parent' investors using a circle symbol of size 10 with a stroke width of 1.

![Styling the investors, parent circle.](media/parent-circle.png)

9. Style the 'subsidiary' investors using a plus symbol of size 10 with a stroke width of 1.

![Styling the investors, subsidiary plus.](media/subsidiary-plus.png)

10. But we want to make a map for each parent investor! To do this, filter your layer. Right click the layer, click 'Filter' on the left side of the pane and write a _query_ in the text box. We want to filter by parent name. To do this, for each company write a query like this: `"par_name"='Amex Exploration'`. After submitting the query, the number of visible points on your screen will drop.

11. Save this as a new layer by right-clicking the layer and selecting 'save as layer definition file'. Name it after the company. Rinse and repeat for each company!

12. For each company, you're going to want to export the map; first, right-click the countries layer and click 'zoom to layer'. Use the following settings:

    + Scale: 1:220000000 (in other words, 1:220,000,000 but you need to exclude the commas)
    + Resolution: 300 dpi
    + Output width: 2000px
    + Output heigh: 2000px

![Exporting the map.](media/export-map.png)

![Exporting the map.](media/final_output_1.png)


## Appendix: Setting This Up on Your Own

1. You'll need to set up a Google Sheet with at least four columns: address, country code, latitude, and longitude.

2. In your Google Sheet open the Script Editor (`Tools > Script Editor`) The following interface will appear. We need to add a script into this box.

![Google Sheet set up for Geocoding.](media/script-editor.png)

3. Graphe has developed [a gently customized version of a script made available by OpenCage](https://gitlab.com/geo-graphe/beyond-extraction/-/blob/master/workshop/geocode.js). Copy paste this script and replace all text with this code.

4. Save the script, calling it 'Geocoder'.

5. Refresh your Google Sheet---you should see a new menu bar item that says 'Geocode'.

6.  Select values in the address, country, lat, and lng columns, then click 'Geocode', selecing Geocode Address to Latitude, Longitude.

![Google Sheet set up for Geocoding.](media/google-sheet-screenshot.png)

7. You will be prompted to give the script permission to run. Do so. A popup will appear asking you which Google account you want to authorize. Select one.

8.	The popup will display a warning that our app isn't verified. Click "Advanced", scroll down, click on the link to "Go to your-project-name (unsafe)." 

9. A popup will appear in your spreadsheet asking your for your OpenCage API key. Enter it and click "Geocode".

10. Nice work!
