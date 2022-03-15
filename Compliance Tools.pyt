# -*- coding: utf-8 -*-

import arcpy
import os
import pandas as pd
from arcgis import GeoAccessor
import surgeo


class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "complianceTools"
        self.alias = "Compliance Tools"

        # List of tool classes associated with this toolbox
        self.tools = [buildFFIECFeatureClass, enrichCustomerPortfolio, BISG, unifiedFIPS]


class Tool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Tool"
        self.description = ""
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        params = None
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        return


class buildFFIECFeatureClass(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Build FFIEC Tracts Feature Class"
        self.description = "This tool will join tract data from the FFIEC to a census tract layer and produce a new feature class."
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        ### inFile param[0] ###
        inFile = arcpy.Parameter(
            displayName = "Input Census File",
            name = "inFile",
            datatype = ["DEFile", "GPTableView"],
            parameterType = "Required",
            direction = "Input")
        
        ### dataYear param[1] ###
        dataYear = arcpy.Parameter(
            displayName = "FFIEC Data Year",
            name = "dataYear",
            datatype = "GPString",
            parameterType = "Required",
            direction = "Input")

        dataYear.filter.type = "ValueList"
        dataYear.filter.list = ['2021', '2020', '2019']
        
        ### tractsLayer param[2] ###
        tractsLayer = arcpy.Parameter(
            displayName = "Census Tracts Feature Layer",
            name = "tractsLayer",
            datatype = ["DEFeatureClass","GPFeatureLayer","DETable","DEDbaseTable","GPTableView","DETextfile"],
            parameterType = "Required",
            direction = "Input")

        
        ### fipsSingleFieldName param[3] ###
        fipsSingleFieldName = arcpy.Parameter(
            displayName = "Census Tract Layer FIPS Field",
            name = "fipsSingleFieldName",
            datatype = "Field",
            parameterType = "Required",
            direction = "Input")

        fipsSingleFieldName.parameterDependencies = [tractsLayer.name]
        fipsSingleFieldName.filter.list = ["String"]
        
        
        ### fieldsToJoin param[4] ###
        fieldsToJoin = arcpy.Parameter(
            displayName = "Field Indexes to Join from FFIEC Data",
            name = "fieldsToJoin",
            datatype = "GPString",
            parameterType = "Required",
            direction = "Input")

        fieldsToJoin.value = "1-14, 231-233, 377, 581, 745-749, 1205-1212"

        ## outputDirectory param(5) ###
        outputDirectory = arcpy.Parameter(
            displayName = "Output Geodatabase",
            name = "outputDirectory",
            datatype = "DEWorkspace",
            parameterType = "Required",
            direction = "Input")


        ## outFeatureClassName param(6) ###
        outFeatureClassName = arcpy.Parameter(
            displayName = "Output Feature Class Name",
            name = "outFeatureClassName",
            datatype = "GPString",
            parameterType = "Required",
            direction = "Input")


        ## resultLayer param(7) ###
        resultLayer = arcpy.Parameter(
            displayName = "Result Layer",
            name = "resultLayer",
            datatype = "GPFeatureLayer",
            parameterType = "Derived",
            direction = "Output")

        params = [inFile, dataYear, tractsLayer, fipsSingleFieldName, fieldsToJoin, outputDirectory, outFeatureClassName, resultLayer]
        
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""

        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        ### SCRIPT FUNCTIONS ###

        #Interprets in the input field expression to create an index list
        def generateFieldIndexList(inString, reserve):
            elementList = inString.split(",")
            fieldList = []
            for item in elementList:
                if "-" in item:
                    fieldRange = item.split("-")
                    start = int(fieldRange[0])
                    end = int(fieldRange[1]) + 1
                    for field in list(range(start,end)): 
                        fieldList.append(field)
                else:
                    fieldList.append(int(item))

            for item in reserve:
                if item not in fieldList:
                    fieldList.append(item)
                    arcpy.AddMessage("Field {0} required but not in user-provided index. Adding...".format(item))

            arcpy.AddMessage("Field index list generated")
            return fieldList

        #Identifies the schema file location
        def findSchemaTable(vintage):
            arcpy.AddMessage("{0} schema template file found".format(vintage))
            return os.path.join(os.path.dirname(os.path.abspath(__file__)),"Schemas","{0}_FFIEC_Schema.csv".format(vintage))

        #Creates and empty geodatabase table and then adds fields to it
        def createContainer(outTableName, inFieldIndexes, inSchemaFile, workspace, prefix):
            #Define and creat output table
            outTable = os.path.join(workspace, outTableName)
            arcpy.management.CreateTable(workspace, outTableName)
            arcpy.AddMessage("New empty table created in workspace")

            #Read Schema File
            field_df = pd.read_csv(inSchemaFile, header=0)
            field_df.set_index("Index")
            

            #Match Indexes to Schema to create ArcGIS Field List
            fieldList = []
            for column in inFieldIndexes:
                fieldSchema = []
                if field_df.iloc[column-1]['Data Type'] == "AN":
                    esriType = "TEXT"
                    length = field_df.iloc[column-1]["Max Length"]
                elif field_df.iloc[column-1]['Data Type'] == "N":
                    esriType = "LONG"
                    length = 0
                else:
                    esriType = "DOUBLE"
                    length = 0
                    
                fieldName = "{0}_{1}".format(prefix,field_df.iloc[column-1]["Index"])
                fieldAlias = field_df.iloc[column-1]["Description"]
                fieldSchema.append(fieldName)
                fieldSchema.append(esriType)
                fieldSchema.append(fieldAlias)
                if length > 0:
                    fieldSchema.append(int(length))
                else:
                    fieldSchema.append(None)
                fieldList.append(fieldSchema)

            arcpy.AddMessage("Schema successfully translated from template")
            arcpy.management.AddFields(outTable,fieldList)
            arcpy.AddMessage("Fields schema successfully applied to new table")
            return outTable

        #Hydrates the empty template table with records from the Census File
        def hydrateContainer(inTable, inDataFile, inFieldIndexes):

            #Create search cursor for iterating over rows in the source census data
            data_field_list = ["Field{0}".format(n) for n in inFieldIndexes]
            dataCursor = arcpy.da.SearchCursor(inDataFile, data_field_list)

            #Create insert cursor for transposing data from file into table
            fc_field_list = [f.name for f in arcpy.ListFields(inTable)]
            fc_field_list.remove("OBJECTID")
            fcCursor = arcpy.da.InsertCursor(inTable, fc_field_list)

            #Iterate through search cursor and transpose values through the insert cursor
            data = []
            for row in dataCursor:
                fcCursor.insertRow(row)
            arcpy.AddMessage("Table successfully hydrated")

            del dataCursor, fcCursor
            return inTable

        #Utility for taking separated FIPS values and creating a unified FIPS value
        def createFIPS(state, county, tract):
            if len(str(state)) < 2:
                newState = "0{0}".format(state)
            else:
                newState = str(state)

            if len(str(county)) < 3:
                if len(str(county)) == 1:
                    newCounty = "00{0}".format(county)
                elif len(str(county)) == 2:
                    newCounty = "0{0}".format(county)
            else:
                newCounty = str(county)

            if len(str(tract)) < 6:
                if len(str(tract)) == 1:
                    newTract = "00000{0}".format(tract)
                elif len(str(tract)) == 2:
                    newTract = "0000{0}".format(tract)
                elif len(str(tract)) == 3:
                    newTract = "000{0}".format(tract)
                elif len(str(tract)) == 4:
                    newTract = "00{0}".format(tract)
                elif len(str(tract)) ==5:
                    newTract = "0{0}".format(tract)
            else:
                newTract = str(tract)
            finalCode = "{0}{1}{2}".format(newState,newCounty,newTract)
            if len(finalCode) == 11:
                return "{0}{1}{2}".format(newState,newCounty,newTract)
            else:
                return "nan"

        #Utility for translating income level code into category values
        def translateIncomeCode(code):
            if code == 0:
                return "Not Available"
            elif code == 1:
                return "Low"
            elif code == 2:
                return "Moderate"
            elif code == 3:
                return "Middle"
            elif code == 4:
                return "Upper"
            else:
                return "Not Available"
        

        #Create unified FIPS field
        def addMaintenanceFields(inTable, indexList, prefix):
            fips_field_name = "unified_fips"
            inc_cat_field_name = "income_level_category"
            cursor_fields = ["{0}_{1}".format(prefix,f) for f in indexList]
            reservedLength = len(indexList)
            cursor_fields.append(fips_field_name)
            cursor_fields.append(inc_cat_field_name)

            arcpy.AddField_management(inTable, fips_field_name, "Text", "", "", 11, "Unified FIPS Code")
            arcpy.AddMessage("New Unified FIPS field added")
            arcpy.AddField_management(inTable, inc_cat_field_name, "Text", "", "", 13, "Income Level Category")
            arcpy.AddMessage("New Income Level Category field added")
            
            cursor = arcpy.da.UpdateCursor(inTable, cursor_fields)
            for row in cursor:
                row[reservedLength] = createFIPS(row[0],row[1],row[2])
                row[reservedLength + 1] = translateIncomeCode(row[3])
                cursor.updateRow(row)

            del cursor
            arcpy.AddMessage("Values populated for new fields")

            return inTable, fips_field_name

        #Copies feature class from one workspace to the target workspace
        def copyTractsFeatureClass(inLayer, outLayer):
            arcpy.management.Copy(inLayer, outLayer)
            arcpy.AddMessage("Tracts layer copied to workspace")
            return outLayer


        def joinDataToLayer(inLayer, inTable, inLayerJoinField, inTableJoinField):
            arcpy.management.JoinField(inLayer, inLayerJoinField, inTable, inTableJoinField)
            arcpy.AddMessage("Data joined to layer")
            return

        def addDivider():
            arcpy.AddMessage(u"\u200B")
            arcpy.AddMessage("----------------------------------------------------")
            arcpy.AddMessage(u"\u200B")
            return
                

        ### SCRIPT LOGIC AND EXECUTION ###

        in_data = parameters[0].valueAsText
        data_year = parameters[1].valueAsText
        tracts_layer = parameters[2].valueAsText
        fips_field = parameters[3].valueAsText
        fields_to_join = parameters[4].valueAsText
        output_directory = parameters[5].valueAsText
        out_fc_name= parameters[6].valueAsText

        field_prefix = "ffiec" #changing this parameter will change the prefix used in each field name
        outTableName = "FFIEC_Table" #changing this parameter will change the name of the geodatabase table that's created
        outLayerName = "FFIEC_Feature_Class" #changing this parameter will change the name of the geodatabase feature class that's created
        reservedList = [3,4,5,1205,11,13,581] #changing this parameter will require modifying the addMaintenanceFields function

        arcpy.AddMessage("Interpreting input field list expression...")
        ffiec_field_list = generateFieldIndexList(fields_to_join, reservedList)
        addDivider()
        
        arcpy.AddMessage("Identifying correct schema template...")
        schema_file = findSchemaTable(data_year)
        addDivider()

        arcpy.AddMessage("Building geodatabase table from template...")
        new_FFIEC_table = createContainer(outTableName, ffiec_field_list, schema_file, "memory", field_prefix)
        addDivider()

        arcpy.AddMessage("Hydrating geodatabase table with source data...")
        hydrated_FFIEC_table = hydrateContainer(new_FFIEC_table, in_data, ffiec_field_list)
        addDivider()

        arcpy.AddMessage("Adding addional fields to table...")
        final_FFIEC_table = addMaintenanceFields(hydrated_FFIEC_table, reservedList, field_prefix)
        addDivider()

        arcpy.AddMessage("FFIEC data translated and prepped.")
        addDivider()

        arcpy.AddMessage("Copying Tracts feature class to workspace...")
        tractsLayer = copyTractsFeatureClass(tracts_layer, os.path.join(output_directory, out_fc_name))
        addDivider()
        
        arcpy.AddMessage("Joining data to layer...")
        final = joinDataToLayer(tractsLayer, final_FFIEC_table[0], fips_field, final_FFIEC_table[1])
        addDivider()

        arcpy.AddMessage("Cleaning up workspaces and preparing output...")
        arcpy.management.Delete("{0}\{1}".format("memory", outTableName))
        arcpy.management.MakeFeatureLayer(tractsLayer,"FFIEC Tracts")

        parameters[7].value = "FFIEC Tracts"
        parameters[7].symbology = os.path.join(os.path.dirname(os.path.abspath(__file__)),"Templates","FFIEC_Tracts.lyrx")

        return



class enrichCustomerPortfolio(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Enrich Customer Portfolio with FFIEC Data"
        self.description = "Transfers FFIEC attributes from a census tract layer to customer points based on spatial intersection"
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        ### customerLayer param[0] ###
        customerLayer = arcpy.Parameter(
            displayName = "Customer Point Layer",
            name = "customerLayer",
            datatype = "GPFeatureLayer",
            parameterType = "Required",
            direction = "Input")
        customerLayer.filter.list = ["Point"]

        ### tractsLayer param[1] ###
        tractsLayer = arcpy.Parameter(
            displayName = "FFIEC Tracts Layer",
            name = "tractsLayer",
            datatype = "GPFeatureLayer",
            parameterType = "Required",
            direction = "Input")
        tractsLayer.filter.list = ["Polygon"]

        ### fieldSelectMode param[2] ###
        fieldSelectMode = arcpy.Parameter(
            displayName = "Field Selection Mode",
            name = "fieldSelectMode",
            datatype = "GPString",
            parameterType = "Required",
            direction = "Input")

        fieldSelectMode.filter.type = "ValueList"
        fieldSelectMode.filter.list = ['Join All Fields from FFIEC Layer', 'Manually Select Fields']
        fieldSelectMode.value = "Join All Fields from FFIEC Layer"

        ### manualSelect param[3] ###
        manualSelect = arcpy.Parameter(
            displayName = "FFIEC Fields to Join",
            name = "manualSelect",
            datatype = "Field",
            parameterType = "Optional",
            multiValue = True,
            enabled = False,
            direction = "Input")

        manualSelect.parameterDependencies = [tractsLayer.name]

        ### resultLayer param[4] ###
        resultLayer = arcpy.Parameter(
            displayName = "Output Customer Feature Class",
            name = "resultLayer",
            datatype = "GPFeatureLayer",
            parameterType = "Required",
            direction = "Output")
        
        params = [customerLayer,tractsLayer,fieldSelectMode, manualSelect, resultLayer]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        if parameters[2].value == "Join All Fields from FFIEC Layer":
            parameters[3].enabled = False

        elif parameters[2].value == "Manually Select Fields":
            parameters[3].enabled = True
            
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""


        reservedList = ["unified_fips","income_level_category"]
        prefix = "ffiec"

        target = parameters[0].valueAsText
        join = parameters[1].valueAsText
        mode = parameters[2].valueAsText
        out = parameters[4].valueAsText
        

        if mode == "Join All Fields from FFIEC Layer":
            arcpy.SpatialJoin_analysis(target, join, out)


        elif mode == "Manually Select Fields":
            joinList = parameters[4].valueAsText
            joinList = joinList.split(';')
            indelible = ['OBJECTID', 'Shape']

            tractFieldList = [f.name for f in arcpy.ListFields(join)]
            for field in indelible:
                joinList.append(field)

            for field in reservedList:
                if field not in joinList:
                    joinList.append(field)

            fieldmappings = arcpy.FieldMappings()
            fieldmappings.addTable(target)
            fieldmappings.addTable(join)

            for field in tractFieldList:
                if field not in joinList:
                    x = fieldmappings.findFieldMapIndex(field)
                    fieldmappings.removeFieldMap(x)

            arcpy.SpatialJoin_analysis(target, join, out,"","", fieldmappings)

        parameters[4].symbology = os.path.join(os.path.dirname(os.path.abspath(__file__)),"Templates","Customer_Result.lyrx")
        
        return

    

class BISG(object):
    
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "BISG (Surgeo 1.1.2)"
        self.description = "This tool leverages the Surgeo python library to execute Beysian Improved Surname Geocoding against a customer layer containing a first name field, surname field, and a tract ID field"
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""

        ### customerLayer param[0] ###
        customerLayer = arcpy.Parameter(
            displayName = "Customer Layer",
            name = "customerLayer",
            datatype = "GPFeatureLayer",
            direction = "Input")

        ### customerID param[1] ###
        customerID = arcpy.Parameter(
            displayName = "Customer ID Field",
            name = "customerID",
            datatype = "Field",
            direction = "Input")

        customerID.parameterDependencies = [customerLayer.name]

        ### surname param[2] ###
        surname = arcpy.Parameter(
            displayName = "Surname Field",
            name = "surname",
            datatype = "Field",
            parameterType = "Required",
            direction = "Input")
        
        surname.parameterDependencies = [customerLayer.name]
        surname.filter.list = ["String"]
        
        ### tract param[3] ###
        tract = arcpy.Parameter(
            displayName = "Tract Unified FIPS Field",
            name = "tract",
            datatype = "Field",
            parameterType = "Required",
            direction = "Input")

        tract.parameterDependencies = [customerLayer.name]
        tract.filter.list = ["String"]

        ### mode param[4] ###
        mode = arcpy.Parameter(
            displayName = "Output Mode",
            name = "mode",
            datatype = "GPString",
            parameterType = "Required",
            direction = "Input")

        mode.filter.list = ["Append to Input Layer", "Create New Layer"]
        mode.value = "Append to Input Layer"

        ### outFC param[5] ###
        outFC = arcpy.Parameter(
            displayName = "Output Feature Class",
            name = "outFC",
            datatype = "GPFeatureLayer",
            parameterType = "Optional",
            direction = "Output")
        
        params = [customerLayer, customerID, surname, tract, mode, outFC]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""

        if parameters[4].value == "Create New Layer":
            parameters[5].enabled = True
        else:
            parameters[5].enabled = False
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""

        def splitFIPS(fips):
            state = fips[0:2]
            county = fips[2:5]
            tract = fips[5:11]
            return [state,county,tract]
        
        #Input parameter references
        in_data = parameters[0].valueAsText
        id_field = parameters[1].valueAsText
        surname_field = parameters[2].valueAsText
        tract_field = parameters[3].valueAsText
        mode = parameters[4].valueAsText
        outFC = parameters[5].valueAsText

        #Import input feature class to dataframe
        in_df = GeoAccessor.from_featureclass(in_data,
                                              where_clause = "CHAR_LENGTH(unified_fips) = 11",
                                              fields = [id_field, surname_field, tract_field])

        #Extract series for fips and surnames to go into Surgeo
        fips = in_df[tract_field].squeeze()
        surnames = in_df[surname_field].squeeze()

        #Surgeo requires that FIPS be split, so we will split the series into a new data frame
        val_list = []
        for val in fips.tolist():
            val_list.append(splitFIPS(val))

        fips_split = pd.DataFrame(val_list, columns = ["state","county","tract"])

        #Run surnames and fips values through the Surgeo model
        sg = surgeo.SurgeoModel(geo_level='TRACT')
        sg_results = sg.get_probabilities(surnames,fips_split)

        #Join results back to original dataframe
        joined_data = in_df.join(sg_results)

        #Drop all columns in the dataframe except what's in the list
        keep_list = [id_field, "api", "black","hispanic","multiple","native","white"]
        joined_data = joined_data[keep_list]

        #Save table to memory for later join
        joined_data.spatial.to_table(r"memory\BISG_result")

        #Join results to original data or to a copy of the original data
        if mode == "Append to Input Layer":
            arcpy.management.JoinField(in_data,id_field,r"memory\BISG_result",id_field)
        elif mode == "Create New Layer":
            arcpy.management.CopyFeatures(in_data, outFC)
            arcpy.management.JoinField(outFC,id_field,r"memory\BISG_result",id_field)
            print("hello")

        #Delete intermediate data
        arcpy.management.Delete(r"memory\BISG_result")
        
        return

class unifiedFIPS(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Create Unified Tract FIPS Field From Split FIPS Fields"
        self.description = "Uses input state, county, and tract FIPS values to create a new unified FIPS field"
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        ### inLayer [param0] ###
        inLayer = arcpy.Parameter(
            displayName = "Input Layer",
            name = "inLayer",
            datatype = "GPFeatureLayer",
            direction = "Input")

        ### stateField [param1] ###
        stateField = arcpy.Parameter(
            displayName = "State FIPS Field",
            name = "stateField",
            datatype = "Field",
            direction = "Input")

        stateField.parameterDependencies = [inLayer.name]

        ### countyField [param2] ###
        countyField = arcpy.Parameter(
            displayName = "County FIPS Field",
            name = "countyField",
            datatype = "Field",
            direction = "Input")

        countyField.parameterDependencies = [inLayer.name]

        ### tractField [param3] ###
        tractField = arcpy.Parameter(
            displayName = "Tract FIPS Field",
            name = "tractField",
            datatype = "Field",
            direction = "Input")

        tractField.parameterDependencies = [inLayer.name]

        ### newFieldName [param4] ###
        newFieldName = arcpy.Parameter(
            displayName = "New Field Name",
            name = "newFieldName",
            datatype = "GPString",
            direction = "Input")
        
        params = [inLayer,stateField,countyField,tractField,newFieldName]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""

        def padZeroes(inValue, desiredLength, stage):
            try:
                int(inValue)
                if len(inValue) > desiredLength:
                    arcpy.AddWarning("The '{0}' value in the provided {1} FIPS field is incompatible because it is too long".format(inValue, stage))
                    return "nan"
                elif inValue == "0":
                    arcpy.AddWarning("The '{0}' value in the provided {1} FIPS field is incompatible because it is a 0".format(inValue, stage))
                    return "nan"
                elif len(inValue) == 0:
                    arcpy.AddWarning("A value in the provided {00} FIPS field is incompatible because it is empty".format(stage))
                    return "nan"
                elif len(inValue) == desiredLength:
                    return inValue
                elif len(inValue) < desiredLength:
                    while len(inValue) < desiredLength:
                        inValue = "0{0}".format(inValue)
                return inValue
            except:
                arcpy.AddWarning("The '{0}' value in the provided {1} FIPS field is incompatible due to the presence of non-numeric values".format(inValue, stage))
                return "nan"
            

        #Instantiate variable references
        in_data = parameters[0].valueAsText
        state_field = parameters[1].valueAsText
        county_field = parameters[2].valueAsText
        tract_field = parameters[3].valueAsText
        field_name = parameters[4].valueAsText

        #Add new blank text field to input with a length of 11
        arcpy.management.AddField(in_data, field_name, "TEXT", "", "", 11)

        #Create a cursor on the input including the involved fields
        cursor = arcpy.da.UpdateCursor(in_data, [state_field, county_field, tract_field, field_name])

        #Calculate unified FIPS and write it to new field
        for row in cursor:
            state = padZeroes(str(row[0]), 2, "state")
            county = padZeroes(str(row[1]), 3, "county")
            tract = padZeroes(str(row[2]), 6, "tract")
            if state == "nan":
                row[3] = "nan"
            elif county == "nan":
                row[3] = "nan"
            elif tract == "nan":
                row[3] = "nan"
            else:
                row[3] = "{0}{1}{2}".format(state, county, tract)

            cursor.updateRow(row)

        del cursor
                
        
        return
    

