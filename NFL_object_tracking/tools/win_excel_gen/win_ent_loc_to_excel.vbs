
	      strFile_tag = "tag_location.csv" 
		 
	      strFile_ent = "ent_location.csv" 
		 
		  lineSep = vbLf

	      set fso = CreateObject("Scripting.FilesystemObject")
           
		  'tag 
  	      set objFile_tag = fso.opentextfile(strFile_tag,1)
          arrFile_tag = split(objFile_tag.ReadAll,lineSep) 
          objFile_tag.close
		  iCount_tag=ubound(arrFile_tag)+1

		  'entity
  	      set objFile_ent = fso.opentextfile(strFile_ent,1)
          arrFile_ent = split(objFile_ent.ReadAll,lineSep) 
          objFile_ent.close
		  iCount_ent=ubound(arrFile_ent)+1

		  
		  'tag
          dim arrTag(3000,4) ' Note: VBScript is zero-based
		  tag_xi = 2
		  tag_yi = 3
		  for i = 0 to iCount_tag-1
             arrLine = split(arrFile_tag(i),",")
			   j = 0
               arrTag(i,j) = arrLine(tag_xi)
		       j = 1
               arrTag(i,j) = arrLine(tag_yi)
          next 
 
		  'entity
          dim arrEnt(3000,4) 
 		  ent_xi = 1
		  ent_yi = 2
		  for i = 0 to iCount_ent-1
             arrLine = split(arrFile_ent(i),",")
			   j = 0
               arrEnt(i,j) = arrLine(ent_xi)
		       j = 1
               arrEnt(i,j) = arrLine(ent_yi)
          next 
 

          ' Launch Excel
          dim app
          set app = createobject("Excel.Application")
    
          ' Make it visible
          app.Visible = true
    
          ' Add a new workbook
          dim wb
          set wb = app.workbooks.add
    
          'Declare a range object to hold our data
		  'tag
          dim rngTag
          set rngTag = wb.Activesheet.Range("A1").Resize(iCount_tag,2)
          rngTag.value = arrTag  ' Now assign them all in one shot...

		  'entity
          dim rngEnt
          set rngEnt = wb.Activesheet.Range("C1").Resize(iCount_ent,2)
          rngEnt.value = arrEnt  
		  	  
		  

          ' Add a new chart based on the data
          wb.Charts.Add
		  wb.ActiveChart.ChartType = -4169 'xlXYScatter


          wb.ActiveChart.SetSourceData rngTag, 2 ' xlColumns
          wb.ActiveChart.Location 2, "Sheet1" 'xlLocationAsObject
		 
          wb.ActiveChart.SeriesCollection(1).MarkerSize = 2


		  'Dim rngTagX 
          'Dim rngTagY
		  'xColTag = 1
		  'yColTag = 2
		  'With wb.Activesheet
          '   Set rngTagX = .Range(.Cells(1, xColTag), .Cells(iCount_tag, xColTag))
          '   Set rngTagY = .Range(.Cells(1, yColTag), .Cells(iCount_tag, yColTag))
          'End With		  
		  
		  'With wb.ActiveChart.SeriesCollection.NewSeries
          '  .XValues = rngTagX
          '  .Values = rngTagY
          '  .Name = "Tag"
		  '	 .MarkerSize = 2
          'End With	  



		  Dim rngEntX 
          Dim rngEntY
		  xColEnt = 3
		  yColEnt = 4	  
		  With wb.Activesheet
             Set rngEntX = .Range(.Cells(1, xColEnt), .Cells(iCount_ent, xColEnt))
             Set rngEntY = .Range(.Cells(1, yColEnt), .Cells(iCount_ent, yColEnt))
          End With		  

		  With wb.ActiveChart.SeriesCollection.NewSeries
            .XValues = rngEntX
            .Values = rngEntY
            .Name = "Entity"
			.MarkerSize = 2
          End With
	  
		  
          ' Add a new chart based on the data
          'wb.Charts.Add
		  'wb.ActiveChart.ChartType = -4169 'xlXYScatter
          'wb.ActiveChart.SetSourceData rngEnt, 2 ' xlColumns
          'wb.ActiveChart.Location 2, "Sheet2" 'xlLocationAsObject

         
          app.UserControl = true ' Give the user control of Excel


