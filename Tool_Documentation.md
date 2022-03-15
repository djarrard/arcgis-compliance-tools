# Tool Documentation

This file serves as documentation for the tools in the python toolbox. The metadata for each individual tool has been populated, and these same documentation concepts are accessible in the tool tips for each tool. Though efforts will be made to ensure both sets are synchronized, this page will represent the most up-to-date documentation for the individual tools.

## BISG (Surgeo 1.1.2)

### Description

Uses Surgeo's BISG algorithm to append race/ethnicity probability fields to an input customer layer.

### Usage

Use this tool to add race/ethnicity probability fields to a customer layer. This tool leverages the BISG algorithm in the Surgeo python library to take surname and census tract FIPS codes to generate these probabilities.

### Parameters

Parameter | Description
-----------| -----------
Customer Layer | The input customer table or layer. This tool does not use spatial functions to generate probabilities so a geocoded customer layer is not necessary.
Customer ID Field | The field describing a unique identifier in the customer layer.
Surname Field | The field describing the surname of each customer in the table or layer.
Tract Unified FIPS Field | The single field describing the tract FIPS value of each customer in the table or layer. If this field does not exist, it can be created using the "Enrich Customer Portfolio with FFIEC Data" tool in this toolbox.
Output Mode | The probablities will be created and added to the customer layer. There are two modes for doing this. <br><br><ul><li><b>Append to Input Layer</b> - with this setting, the input layer will be modified by adding and calculating the new fields to it.</li><li><b>Create New Layer</b> - the input layer will be copied to a new layer and the new fields will be added and calculated to it, thus preserving the original file.</li></ul>

### Requirements and Resources

This tool requires the [Surgeo 1.1.2](https://github.com/theonaunheim/surgeo) python library to be installed in order to run.

## Build FFIEC Tracts Feature Class

### Description

Translates raw FFIEC data into an ArcGIS Feature Class

### Usage

Use this tool to process FFIEC raw data and transform it into a feature class. The tool is flexible to accommodate different data vintages, allows for specific selection of fields through indexes and index ranges, and can accommodate different FIPS formats.

### Parameters

Parameter | Description
-----------| -----------
Input Census File | The input FFIEC data file to be translated into ArcGIS. The input files can be downloaded directly from the FFIEC website.
FFIEC Data Year | Given that the FFIEC data schema can change from year-to-year, this toolbox includes schema spreadsheets that the tool will use to correctly read and translate the data. The data year selected in this parameter should correspond to the data year downloaded from the FFIEC website. For example, if the 2021 data was downloaded from the FFIEC, 2021 should be selected as this parameter's value. This build of the toolbox supports these data years: <br><br><ul><li>2021</li><li>2020</li><li>2019</li></ul>
Census Tracts Feature Layer | The tracts feature class or shapefile that will be used as the geographies for the output. This tracts layer MUST contain a single text-based FIPS field that contains the FIPS identifier for each census tract (e.g. "15007041200"). Note that this field must be a text field since FIPS identifiers often contain leading zeroes. Unified FIPS identifiers for census tracts always contain 11 characters. If the input layer contains split FIPS identifiers, the "Create Unified Tract FIPS Field from Split FIPS Fields" tool in this toolbox can be used to create a new unified FIPS field.
Census Tract Layer FIPS Field | Select the field in the input Census Tracts layer that contains the unified FIPS values for each record.
Field Index to Join from FFIEC Data | Use this parameter to specify which fields from the FFIEC data file you want present within the output. The parameter can use a series of individual field index references along with ranges. The field indexes correspond with the .doc file packaged with the FFIEC data. The default string is: 1-14, 231-233, 377, 581, 745-749, 1205-1212. <br><br>NOTE: some essential fields from the FFIEC data will ALWAYS be added regardless of whether they are specified in this parameter. This is to support default visualization settings and downstream analyses within the same toolbox. For example, the tool will always create a unified FIPS field.
Output Geodatabase | The output of this tool will always be a polygon feature class in a geodatabase. Use this parameter to specify which geodatabase that the output should be stored in.
Output Feature Class Name | The output name of the feature class to be generated.

### Requirements and Resources

* FFIEC Data Download - https://www.ffiec.gov/censusapp.htm

* US Census Tracts Download - https://www.census.gov/geographies/mapping-files/time-series/geo/cartographic-boundary.html

## Create Unified Tract FIPS Field from Split FIPS Fields

### Description

Generates a new single FIPS identifier field from multiple FIPS fields

### Usage

Many census-based geography datasets will contain FIPS identifiers that are split into multiple fields: state, county, and tract. The split nature of these fields complicates joins. In addition, oftentimes these fields are formatted as numeric fields or don't incorporate the correct number of leading zeroes, complicating reconstruction of a single FIPS identifier. This tool intelligently builds a single FIPS identifier for census tracts based on three input fields. This field is useful for performing joins, BISG workflows, and when working with other tools in this toolbox.

### Parameters

Parameter | Description
-----------| -----------
Input Layer | The input layer, shapefile, feature class, or editable table containing the splits FIPS fields to be transformed.
State FIPS Field | The field describing the State FIPS value for each tract.
County FIPS Field | The field describing the County FIPS value for each tract.
Tract FIPS Field | The field describing the Tract FIPS value for each tract.
New Field Name | The name of the new unified FIPS field to be created.

### Requirements and Resources

## Enrich Customer Portfolio with FFIEC Data

### Description
Associates FFIEC attributes to a customer dataset

### Usage
Use this tool to enrich an existing geocoded customer dataset with variables from the FFIEC. This tool is intended to be used the output of the Build FFIEC Feature Class tool. It accomplishes the join using the spatial relationship between the individual customer points and the census tract that it intersects.

### Parameters

Parameter | Description
-----------| -----------
Customer Point Layer | The input ArcGIS point layer representing the portfolio you wish to enrich. This input MUST be a point layer. If your customers are not yet geocoded, you will need to [geocode your customer table](https://pro.arcgis.com/en/pro-app/latest/tool-reference/geocoding/geocode-addresses.htm) first.
FFIEC Tracts Layer | The input tracts layer containing the fields you wish to join. Use the _Build FFIEC Feature Class_ tool to create this layer, and then use the output of that tool as input to this one.
Field Selection Mode | The input tracts layer containing the fields you wish to join. Use the Build FFIEC Feature Class tool to create this layer, and then use the output of that tool as input to this one.<br><br><ul><li><b>Join All Fields from the FFIEC Layer</b>- this option will join all available fields in the input tracts layer to the customer points.</li><li><b>Manually Select Fields</b> - this option will join all available fields in the input tracts layer to the customer points.</li></ul>
FFIEC Fields to Join (contextual) | This parameter is only available when the Field Selection Mode parameter is set to "Manually Select Fields". Use this parameter to select the individual fields you wish to join from the tracts layer to the customer layer.
Output Customer Feature Class | Specify the output location and desired name of the result layer.

### Requirements and Resources
