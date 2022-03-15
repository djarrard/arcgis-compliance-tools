# ArcGIS Financial Services Compliance Tools

## Features

This project is intended as an immediately usable resource in the ArcGIS Pro environment that allows users to perform common compliance workflows within ArcGIS. This toolset serves as a bridge of sorts that enables instant integration of FFIEC data, BISG workflows, and spatial analyses that are frequently used for reporting and evaluation in compliance workflows.

* **BISG (Surgeo 1.1.2)** - leverages the Surgeo python library to perform Bayesian Improved Surname Geocoding analysis on the input customer table. In reality, this tool is simply a wrapper that translates input data from ArcGIS into Surgeo, and results from Surgeo into ArcGIS objects. As such, the Surgeo library must be installed for this tool to work. This tool is hard-configured to use the SurgeoModel model in Surgeo to generate race/ethnicity probabilities based on an input Surname field and input tract FIPS field.

* **Build FFIEC Tracts Feature Class** -  incorporates a data download from the FFIEC website and a standard Census Tracts layer to build a spatially-enabled feature class in ArcGIS. This spatially-enabled dataset can support multiple other workflows including visualization, reporting, and customer analysis. The tool allows for intelligent selection of fields so just the fields from the larger FFIEC dataset are instantiated.

* **Create Unified Tract FIPS Field from Split FIPS Fields** - Many census-based geography datasets will contain FIPS identifiers that are split into multiple fields: state, county, and tract. The split nature of these fields complicates joins. In addition, oftentimes these fields are formatted as numeric fields or don't incorporate the correct number of leading zeroes, complicating reconstruction of a single FIPS identifier. This tool intelligently builds a single FIPS identifier for census tracts based on three input fields. This field is useful for performing joins, BISG workflows, and when working with other tools in this toolbox.

* **Enrich Customer Portfolio with FFIEC Data** - This tool enriches an existing geocoded customer dataset with variables from the FFIEC feature class created by the “Build FFIEC Tracts Feature Class” tool in this same toolbox. It accomplishes the join using the spatial relationship between the individual customer points and the census tract that it intersects.

## Instructions and Notes

1. Download the repository ZIP file
2. Extract the ZIP file to the desired folder
3. If necessary, in your ArcGIS Pro project, use the Catalog view to add a connection to the folder containing the extracted repository.
4. In the Catalog view, expand the _Compliance Tools.pyt_ toolbox.
5. Double-click a tool to launch it.

NOTE: In order to leverage the BISG tool, the Surgeo module will need to installed. Installation instructions can be found here: https://github.com/theonaunheim/surgeo

## Requirements

1. ArcGIS Pro 2.9 or higher. Lower versions may work but have not been tested. Please submit an issue if you have issues specific to versions of ArcGIS Pro.
2. The Geoprocessing tools used in the toolbox only require a Basic license of ArcGIS Pro. No extensions are used. Standard and Advanced licenses are supported, but not required.
3. This toolbox will not work in ArcMap, and no development efforts will be made make a compatible version.

## Issues

If there are bugs/issues with the toolbox that prevent usage or create incorrect results, please let me know by submitting an issue. I am also open to expanding the toolbox to include other use cases that expand capabilities and compatibility with compliance workflows. Please feel free to submit enhancement requests along those lines.

## Contributing

I follow the Esri Github guidelines for contributing. Please see [guidelines for contributing](https://github.com/esri/contributing).

## Licensing

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at


   http://www.apache.org/licenses/LICENSE-2.0


Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.


A copy of the license is available in the repository.